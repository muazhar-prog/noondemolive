import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Attendance Dashboard", layout="wide")
st.title("Rider Attendance Dashboard")

st.markdown(
    "Upload the Excel file, pick the sheet with daily attendance codes "
    "(**P** = present, **A** = absent, **WO** = week off), and this will "
    "calculate each rider's attendance percentage. Week-offs are excluded "
    "from the calculation."
)

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Waiting for a file to be uploaded.")
    st.stop()

# Load workbook and let the user pick a sheet
try:
    excel_file = pd.ExcelFile(uploaded_file)
except Exception as e:
    st.error(f"Could not read this file as an Excel workbook: {e}")
    st.stop()

sheet_name = st.selectbox("Select sheet", excel_file.sheet_names)

df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Identify which columns are "day" columns: their header is a date
day_columns = [c for c in df.columns if isinstance(c, (datetime.datetime, datetime.date, pd.Timestamp))]

if not day_columns:
    st.error(
        "No date-labeled columns were found in this sheet, so attendance "
        "can't be calculated. Make sure you've selected the sheet where "
        "each day's status (P/A/WO) sits under a column headed with that "
        "day's date."
    )
    st.stop()

st.success(f"Found {len(day_columns)} day columns
