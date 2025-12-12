# lab_marks_processor.py
"""
Streamlit Lab Marks Processor
- Interactive single-student calculator
- Batch Excel upload -> processed Excel download
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Lab Marks Processor", layout="centered")

# --- helper functions (business logic) ---
def attendance_marks(att):
    try:
        att = float(att)
    except Exception:
        return None
    if att < 0 or att > 100:
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

def compute_row_marks(row):
    a = attendance_marks(row.get("Attendance"))
    e = execution_marks(row.get("Execution"))
    r = labrecord_marks(row.get("LabRecord"))
    return a, e, r, ( (a or 0) + e + r )

def dataframe_with_marks(df):
    # expects columns: Name, Roll, Attendance, Execution, LabRecord
    df = df.copy()
    df["AttendanceMarks"] = df["Attendance"].apply(attendance_marks)
    df["ExecutionMarks"] = df["Execution"].apply(execution_marks)
    df["RecordMarks"] = df["LabRecord"].apply(labrecord_marks)
    df["TotalMarks"] = df["AttendanceMarks"].fillna(0) + df["ExecutionMarks"] + df["RecordMarks"]
    return df

def to_excel_bytes(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return buffer

# --- UI ---
st.title("Lab Marks Processor")
st.write(
    "Calculate lab marks (out of 25) from attendance, execution status and lab record. "
    "Use the Single Student tab for interactive demos or Batch for Excel processing."
)

tab1, tab2 = st.tabs(["Single Student (Interactive)", "Batch (Excel upload/download)"])

with tab1:
    st.header("Single Student — Interactive")
    with st.form("single_form", clear_on_submit=False):
        c1, c2 = st.columns([2, 1])
        with c1:
            name = st.text_input("Student Name", "")
            roll = st.text_input("Roll Number", "")
        with c2:
            attendance = st.number_input("Attendance (%)", min_value=0.0, max_value=100.0, value=75.0, step=0.1, format="%.1f")
            execution = st.selectbox("Execution status", options=["yes", "badoutput", "no"], index=0)
            labrecord = st.radio("Lab record submitted?", options=["yes", "no"], index=0)
        submitted = st.form_submit_button("Calculate Marks")
        st.button("Sample Demo", key="single_sample", help="Fill form with a sample student")
        # handle Sample Demo (non-form button)
        if st.session_state.get("single_sample", False):
            # populate sample values (one-shot)
            st.session_state["single_sample"] = False
        # If user pressed the Sample Demo button, prefill via st.experimental_set_query_params is heavy; instead show sample result directly
        if st.button("Fill sample values"):
            name = "Chandana M"
            roll = "CE203"
            attendance = 75.0
            execution = "no"
            labrecord = "yes"
            st.experimental_rerun()

    # compute and show result
    if submitted:
        a_mark = attendance_marks(attendance)
        if a_mark is None:
            st.error("Attendance value invalid. Must be 0–100.")
        else:
            e_mark = execution_marks(execution)
            r_mark = labrecord_marks(labrecord)
            total = a_mark + e_mark + r_mark

            st.subheader("Student Report")
            st.markdown(
                f"**Name:** {name}  \n"
                f"**Roll No:** {roll}  \n"
                f"**Attendance:** {attendance:.1f}% → **{a_mark}** marks  \n"
                f"**Execution:** {execution} → **{e_mark}** marks  \n"
                f"**Lab Record:** {labrecord} → **{r_mark}** marks  \n"
                f"**Total Marks (out of 25):** **{total}**"
            )

            # prepare single-row DataFrame and offer download
            result_df = pd.DataFrame([{
                "Name": name,
                "Roll": roll,
                "Attendance": attendance,
                "Execution": execution,
                "LabRecord": labrecord,
                "AttendanceMarks": a_mark,
                "ExecutionMarks": e_mark,
                "RecordMarks": r_mark,
                "TotalMarks": total
            }])

            st.download_button(
                "Download result as Excel",
                data=to_excel_bytes(result_df),
                file_name=f"lab_marks_{roll or 'student'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with tab2:
    st.header("Batch processing — upload an Excel and download results")
    st.markdown("Upload an Excel file with the exact columns: **Name, Roll, Attendance, Execution, LabRecord** (case-sensitive).")
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx", "xls", "csv"])

    if uploaded is not None:
        # try reading into DataFrame
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
        except Exception as exc:
            st.error(f"Could not read uploaded file: {exc}")
            st.stop()

        required = ["Name", "Roll", "Attendance", "Execution", "LabRecord"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Uploaded file is missing required columns: {missing}")
            st.write("Detected columns:", list(df.columns))
            st.stop()

        st.subheader("Preview (first 10 rows)")
        st.dataframe(df.head(10))

        if st.button("Compute marks for uploaded file"):
            out_df = dataframe_with_marks(df)
            st.success("Computation complete — preview results below.")
            st.dataframe(out_df.head(20))

            # show simple validation summary
            invalid_att = out_df[out_df["AttendanceMarks"].isna()]
            if not invalid_att.empty:
                st.warning(f"{len(invalid_att)} rows had invalid attendance values (AttendanceMarks blank). Check those rows.")
                st.dataframe(invalid_att[["Name", "Roll", "Attendance"]].head(10))

            # download button for results in Excel
            st.download_button(
                "Download results as Excel",
                data=to_excel_bytes(out_df),
                file_name=f"lab_marks_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.info("No file uploaded. You can download a sample input file and use it to test.")
        if st.button("Download sample input Excel"):
            sample_df = pd.DataFrame([
                {"Name":"Anita K","Roll":"CE201","Attendance":92,"Execution":"yes","LabRecord":"yes"},
                {"Name":"Bala M","Roll":"CE202","Attendance":48,"Execution":"badoutput","LabRecord":"no"},
                {"Name":"Chandana M","Roll":"CE203","Attendance":75,"Execution":"no","LabRecord":"yes"},
                {"Name":"Dinesh R","Roll":"CE204","Attendance":24.9,"Execution":"yes","LabRecord":"no"},
                {"Name":"Keerthana S","Roll":"CE205","Attendance":88,"Execution":"yes","LabRecord":"no"}
            ])
            st.download_button(
                "Download sample_input_marks.xlsx",
                data=to_excel_bytes(sample_df),
                file_name="sample_input_marks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Footer / notes
st.markdown("---")
st.markdown(
    "**Notes:**\n\n"
    "- `Execution` accepted values: `yes`, `no`, `badoutput` (case-insensitive on upload).\n"
    "- `LabRecord` accepted values: `yes` or `no`.\n"
    "- Attendance must be numeric (0–100). Rows with invalid attendance will still be included but AttendanceMarks will be blank."
)

