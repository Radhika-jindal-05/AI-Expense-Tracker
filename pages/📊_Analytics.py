import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# UI STYLING 
st.markdown("""
<style>
.metric-box {
    padding: 18px;
    border-radius: 16px;
    background: #ffffff;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    text-align: center;
}

.metric-title {
    font-size: 14px;
    color: #6b7280;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

/* 🌙 Dark mode override */
.dark .metric-box {
    background: #161b22;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}

.dark .metric-title {
    color: #9da5b4;
}

.dark .metric-value {
    color: #ffffff;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Main app background */
.stApp {
    background-color: #f6f8fc;
}

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
}

/* Container cards */
[data-testid="stContainer"] {
    background-color: white;
    border-radius: 16px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# CONFIG 
st.set_page_config(
    page_title="Expense Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown("## 🎨 Theme")
    dark_mode = st.toggle("🌙 Dark Mode")

st.title("📊 Expense Analytics")

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
SHEET_NAME = "AI_Expense_Data"   


def apply_theme(dark):
    if dark:
        st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #e6e6e6;
        }

        /* add dark class */
        .stApp > div {
            class: dark;
        }

        body { background-color:#0e1117; }

        section[data-testid="stSidebar"] {
            background-color: #161b22;
        }

        h1,h2,h3,h4,h5,h6,p,span,label {
            color:#e6e6e6 !important;
        }
        </style>
        """, unsafe_allow_html=True)


apply_theme(dark_mode)

# GOOGLE SHEETS SERVICE 
@st.cache_resource
def get_sheets_service():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=scopes
    )
    return build("sheets", "v4", credentials=creds)

service = get_sheets_service()

# LOAD DATA 
@st.cache_data(ttl=300)
def get_transactions_data():
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1:H"
        ).execute()

        values = result.get("values", [])
        if len(values) <= 1:
            return pd.DataFrame(columns=[
                "Date","Amount","Type","Category",
                "Subcategory","Description","Due Date","Status"
            ])

        df = pd.DataFrame(values[1:], columns=values[0])
        df.columns = df.columns.str.strip()

        # Clean string columns
        for col in ["Type","Category","Subcategory","Description","Status"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()

        # Amount
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

        # Dates
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
        df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce", dayfirst=True)

        # Remove invalid rows
        df = df.dropna(subset=["Date","Amount"]).reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

# DATA 
df = get_transactions_data()

# SIDEBAR FILTERS
st.sidebar.header("📅 Filters")
filter_type = st.sidebar.radio(
    "Select Time Period",
    ["All Time", "Year", "Month", "Custom Range"]
)

# Default dates
start_date = df["Date"].min()
end_date = df["Date"].max()

# YEAR FILTER
if filter_type == "Year" and not df.empty:
    years = sorted(df["Date"].dt.year.unique(), reverse=True)
    selected_year = int(st.sidebar.selectbox("Select Year", years))
    start_date = datetime(selected_year, 1, 1)
    end_date = datetime(selected_year, 12, 31)

# MONTH FILTER
elif filter_type == "Month" and not df.empty:
    years = sorted(df["Date"].dt.year.unique(), reverse=True)
    selected_year = int(st.sidebar.selectbox("Select Year", years))

    selected_month = st.sidebar.selectbox(
        "Select Month",
        range(1, 13),
        format_func=lambda x: datetime(2000, x, 1).strftime("%B")
    )

    start_date = datetime(selected_year, selected_month, 1)
    end_date = datetime(selected_year, selected_month, 28) + timedelta(days=4)
    end_date = end_date - timedelta(days=end_date.day)

# CUSTOM RANGE
elif filter_type == "Custom Range" and not df.empty:
    sd = st.sidebar.date_input("Start Date", start_date.date())
    ed = st.sidebar.date_input("End Date", end_date.date())
    start_date = datetime.combine(sd, datetime.min.time())
    end_date = datetime.combine(ed, datetime.max.time())

#  FILTER DATA 
df_filtered = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

#  TABS
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Income", "Expense", "Pending"]
)

#  OVERVIEW 
with tab1:
    st.subheader("📈 Financial Overview")

    if df_filtered.empty:
        st.info("No data for selected period.")
    else:
        income = df_filtered[df_filtered["Type"] == "Income"]["Amount"].sum()
        expense = df_filtered[df_filtered["Type"] == "Expense"]["Amount"].sum()
        savings = income - expense
        rate = (savings / income * 100) if income > 0 else 0

        # c1, c2, c3, c4 = st.columns(4)
        # c1.metric("Total Income", f"₹ {income:,.2f}")
        # c2.metric("Total Expense", f"₹ {expense:,.2f}")
        # c3.metric("Net Savings", f"₹ {savings:,.2f}")
        # c4.metric("Saving Rate", f"{rate:.1f}%")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Total Income</div>
                <div class="metric-value">₹ {income:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Total Expense</div>
                <div class="metric-value">₹ {expense:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Net Savings</div>
                <div class="metric-value">₹ {savings:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Saving Rate</div>
                <div class="metric-value">{rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)


        monthly = (
            df_filtered
            .groupby([df_filtered["Date"].dt.strftime("%Y-%m"), "Type"])["Amount"]
            .sum()
            .unstack(fill_value=0)
        )

        fig = px.bar(monthly, barmode="group", title="Monthly Income vs Expense")
        fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6e6e6" if dark_mode else "#111827"
)

        fig.update_layout(title_x=0.4, height=420)
        st.plotly_chart(fig, use_container_width=True)

# -------------------- INCOME --------------------
with tab2:
    st.subheader("💰 Income Analytics")
    income_df = df_filtered[df_filtered["Type"] == "Income"]

    if income_df.empty:
        st.info("No income data.")
    else:
        monthly_income = income_df.groupby(
            income_df["Date"].dt.strftime("%Y-%m")
        )["Amount"].sum()

        fig = px.bar(monthly_income, title="Monthly Income Trend")
        fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6e6e6" if dark_mode else "#111827"
        )

        fig.update_layout(title_x=0.4, height=420)
        st.plotly_chart(fig, use_container_width=True)

# EXPENSE 
with tab3:
    st.subheader("💸 Expense Analytics")
    expense_df = df_filtered[df_filtered["Type"] == "Expense"]

    if expense_df.empty:
        st.info("No expense data.")
    else:
        monthly_expense = expense_df.groupby(
            expense_df["Date"].dt.strftime("%Y-%m")
        )["Amount"].sum()

        fig = px.bar(monthly_expense, title="Monthly Expense Trend")
        fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6e6e6" if dark_mode else "#111827"
        )

        fig.update_layout(title_x=0.4, height=420)
        st.plotly_chart(fig, use_container_width=True)

        cat_sum = expense_df.groupby("Category")["Amount"].sum()
        fig2 = px.pie(
            values=cat_sum.values,
            names=cat_sum.index,
            title="Expenses by Category"
        )
        st.plotly_chart(fig2, use_container_width=True)

# PENDING 
with tab4:
    st.subheader("📋 Pending Transactions")
    pending_df = df_filtered[df_filtered["Status"] == "Pending"]

    if pending_df.empty:
        st.info("No pending transactions.")
    else:
        st.dataframe(pending_df, use_container_width=True)