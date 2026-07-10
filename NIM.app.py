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

st.success(f"Found {len(day_columns)} day columns in '{sheet_name}'.")

# Non-day columns are treated as the rider's detail columns (ID, name, etc.)
detail_columns = [c for c in df.columns if c not in day_columns]

# Normalize the codes in the day columns (strip spaces, uppercase)
codes = df[day_columns].apply(lambda col: col.astype(str).str.strip().str.upper())

present_count = (codes == "P").sum(axis=1)
absent_count = (codes == "A").sum(axis=1)
weekoff_count = (codes == "WO").sum(axis=1)

denominator = present_count + absent_count
attendance_pct = (present_count / denominator * 100).round(1)
attendance_pct = attendance_pct.where(denominator > 0, other=pd.NA)

result = df[detail_columns].copy()
result["Present Days"] = present_count
result["Absent Days"] = absent_count
result["Week Off Days"] = weekoff_count
result["Attendance %"] = attendance_pct

st.subheader("Attendance by rider")
st.dataframe(result, use_container_width=True)

# Simple summary
valid = result["Attendance %"].dropna()
if len(valid) > 0:
    col1, col2, col3 = st.columns(3)
    col1.metric("Riders with valid attendance %", len(valid))
    col2.metric("Average attendance %", f"{valid.mean():.1f}%")
    col3.metric("Lowest attendance %", f"{valid.min():.1f}%")

st.subheader("Attendance % chart")
if len(valid) > 0:
    chart_data = result.dropna(subset=["Attendance %"]).set_index(detail_columns[0])["Attendance %"]
    st.bar_chart(chart_data)
else:
    st.info("No riders had both Present and Absent days recorded, so no chart to show.")

# Download button
csv = result.to_csv(index=False).encode("utf-8")
st.download_button("Download results as CSV", csv, "attendance_results.csv", "text/csv")
