import streamlit as st
import pandas as pd
import os
from services.google_sheets import get_sheets_service
from dotenv import load_dotenv
from datetime import date

# THEME 
with st.sidebar:
    st.markdown("## 🎨 Theme")
    dark_mode = st.toggle("🌙 Dark Mode")


st.set_page_config(
    page_title="AI Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)
# UI
st.markdown("""
<style>
.stApp {
    background-color: #f6f8fc;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

load_dotenv()

SHEET_NAME = "AI_Expense_Data"

st.title("💸 AI Expense Tracker")

spreadsheet_id = os.getenv("SPREADSHEET_ID")
service = get_sheets_service()

def apply_theme(dark):
    if dark:
        st.markdown("""
        <style>
        /* Main background */
        .stApp {
            background-color: #0e1117;
            color: #e6e6e6;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #161b22;
        }

        /* Headings & text */
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #e6e6e6 !important;
        }

        /* Input fields */
        input, textarea, select {
            background-color: #161b22 !important;
            color: #ffffff !important;
        }

        /* Dataframe */
        .stDataFrame {
            background-color: #161b22;
            color: #ffffff;
        }

        /* Buttons */
        button {
            background-color: #238636 !important;
            color: white !important;
            border-radius: 8px;
        }
        </style>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }

        section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }

        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)


apply_theme(dark_mode)
spreadsheet_id = os.getenv("SPREADSHEET_ID")
sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

with st.sidebar:
    st.markdown("## 📄 Data")
    st.link_button(
        "📊 View in Google Sheets (Excel)",
        sheet_url
    )

# LOAD DATA 
def load_data():
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=f"{SHEET_NAME}!A1:H"
        )
        .execute()
    )

    values = result.get("values", [])
    if len(values) <= 1:
        return pd.DataFrame(columns=[
            "Date", "Amount", "Type", "Category",
            "Subcategory", "Description", "Due Date", "Status"
        ])

    df = pd.DataFrame(values[1:], columns=values[0])
    return df


df = load_data()

st.markdown("## 📋 Existing Expenses")

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


st.divider()

# ADD NEW EXPENSE 
st.markdown("## ➕ Add New Expense")

st.markdown('<div class="card">', unsafe_allow_html=True)

with st.form("expense_form"):
    col1, col2 = st.columns(2)

    with col1:
        exp_date = st.date_input("Date", date.today())
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        exp_type = st.selectbox("Type", ["Expense", "Income"])
        category = st.text_input("Category")
        subcategory = st.text_input("Subcategory")

    with col2:
        description = st.text_input("Description")
        due_date = st.date_input("Due Date", value=None)
        status = st.selectbox("Status", ["PENDING", "COMPLETED"])

    submitted = st.form_submit_button("Save")

    if submitted:
        new_row = [
            str(exp_date),
            str(amount),
            exp_type,
            category,
            subcategory,
            description,
            str(due_date) if due_date else "",
            status
        ]

        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [new_row]}
        ).execute()

        st.toast("✅ Expense saved successfully!", icon="💸")
        st.rerun()
        
