import os
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Any
from dotenv import load_dotenv
load_dotenv()


@st.cache_resource
def get_sheets_service():
    try:
        # expense_tracker directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        creds_path = os.path.join(
            project_root,
            os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")
        )

        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Credentials file not found at: {creds_path}")

        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

        return build("sheets", "v4", credentials=creds)

    except Exception as e:
        raise RuntimeError(f"Google Sheets init failed: {e}")

