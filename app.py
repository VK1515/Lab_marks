"""
Streamlit app: Lab Marks Processor
Upload an Excel file with columns: Name, Roll, Attendance, Execution, LabRecord
It will compute AttendanceMarks, ExecutionMarks, RecordMarks and TotalMarks
and provide a downloadable Excel with results.
"""

import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Lab Marks Processor", layout="centered")

st.title("Lab Marks Processor (Upload Excel -> Download Results)")
st.markdown("""
Upload an Excel file that contains **these exact column names** (case-sensitive):
- **Name**
- **Roll**
- **Attendance**
- **Execution**  (values: yes / no / badoutput)
- **LabRecord**  (values: yes / no)

The app will add these columns: **AttendanceMarks, ExecutionMarks, RecordMarks, TotalMarks**.
""")

uploaded = st.file_uploader("Upload input Excel file", type=["xlsx","xls"])

def attendance_marks(att):
    try:
        att = float(att)
    except:
        return None
    if att < 25:
        return 2.5
    elif att < 50:
        return 5
    elif att < 75:
        return 7.5
    elif att < 90:
        return 8.5
    else:
        return 10

def execution_marks(exe):
    exe = str(exe).strip().lower()
    if exe == "yes":
        return 10
    elif exe == "badoutput":
        return 6
    else:
        return 0

def labrecord_marks(rec):
    return 5 if str(rec).strip().lower() == "yes" else 0

if uploaded is not None:
    try:
        df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.stop()

    required = ["Name","Roll","Attendance","Execution","LabRecord"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}. Please upload a file with columns exactly: {required}")
        st.write("Preview of uploaded columns:", list(df.columns))
        st.stop()

    st.subheader("Preview (first 10 rows)")
    st.dataframe(df.head(10))

    # Compute marks
    df["AttendanceMarks"] = df["Attendance"].apply(attendance_marks)
    df["ExecutionMarks"] = df["Execution"].apply(execution_marks)
    df["RecordMarks"] = df["LabRecord"].apply(labrecord_marks)
    df["TotalMarks"] = df["AttendanceMarks"].fillna(0) + df["ExecutionMarks"] + df["RecordMarks"]

    st.subheader("Computed Results (first 10 rows)")
    st.dataframe(df.head(10))

    # Provide download
    towrite = BytesIO()
    df.to_excel(towrite, index=False, engine="openpyxl")
    towrite.seek(0)

    st.download_button(
        label="Download results as Excel",
        data=towrite,
        file_name="lab_marks_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("Processing complete. Download the results using the button above.")
else:
    st.info("Upload an Excel file to get started. Use the provided sample_input_marks.xlsx format if needed.")