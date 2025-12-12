# Lab Marks Processor.py (fixed — removed experimental_rerun)
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Lab Marks Processor", layout="centered")

# Helper functions
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

def to_excel_bytes(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return buffer

def dataframe_with_marks(df):
    df = df.copy()
    df["AttendanceMarks"] = df["Attendance"].apply(attendance_marks)
    df["ExecutionMarks"] = df["Execution"].apply(execution_marks)
    df["RecordMarks"] = df["LabRecord"].apply(labrecord_marks)
    df["TotalMarks"] = df["AttendanceMarks"].fillna(0) + df["ExecutionMarks"] + df["RecordMarks"]
    return df

# Page UI
st.title("Lab Marks Processor")
st.write(
    "Calculate lab marks (out of 25) from attendance, execution status and lab record. "
    "Use the Single Student tab for interactive demos or Batch for Excel processing."
)

tab1, tab2 = st.tabs(["Single Student (Interactive)", "Batch (Excel upload/download)"])

# Ensure session_state keys exist with safe defaults
defaults = {
    "name": "",
    "roll": "",
    "attendance": 75.0,
    "execution": "yes",
    "labrecord": "yes",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Callbacks
def fill_sample():
    # Runs as widget callback — safe to modify session_state here
    st.session_state["name"] = "Chandana M"
    st.session_state["roll"] = "CE203"
    st.session_state["attendance"] = 75.0
    st.session_state["execution"] = "no"
    st.session_state["labrecord"] = "yes"
    # No experimental_rerun() — not required and may cause AttributeError in some environments

def show_sample_report():
    # Prepare sample report data in session state for display in main flow
    name = "Anita K"
    roll = "CE201"
    attendance = 92.0
    execution = "yes"
    labrecord = "yes"
    a_mark = attendance_marks(attendance)
    e_mark = execution_marks(execution)
    r_mark = labrecord_marks(labrecord)
    total = a_mark + e_mark + r_mark
    st.session_state["_sample_report"] = {
        "name": name, "roll": roll, "attendance": attendance,
        "execution": execution, "labrecord": labrecord,
        "a_mark": a_mark, "e_mark": e_mark, "r_mark": r_mark, "total": total
    }

with tab1:
    st.header("Single Student — Interactive")

    with st.form("single_form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.text_input("Student Name", key="name")
            st.text_input("Roll Number", key="roll")
        with c2:
            st.number_input(
                "Attendance (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state["attendance"],
                step=0.1,
                format="%.1f",
                key="attendance"
            )
            st.selectbox(
                "Execution status",
                options=["yes", "badoutput", "no"],
                index=["yes", "badoutput", "no"].index(st.session_state["execution"]),
                key="execution"
            )
            st.radio(
                "Lab record submitted?",
                options=["yes", "no"],
                index=["yes", "no"].index(st.session_state["labrecord"]),
                key="labrecord"
            )
        submitted = st.form_submit_button("Calculate Marks")

    # Buttons outside form — use on_click callbacks
    colA, colB = st.columns(2)
    with colA:
        st.button("Fill sample values", on_click=fill_sample)
    with colB:
        st.button("Sample Demo Report", on_click=show_sample_report)

    # If sample report prepared in session_state by callback, display it
    if "_sample_report" in st.session_state:
        sr = st.session_state.pop("_sample_report")
        st.subheader("Sample Student Report")
        st.markdown(
            f"**Name:** {sr['name']}  \n"
            f"**Roll No:** {sr['roll']}  \n"
            f"**Attendance:** {sr['attendance']:.1f}% → **{sr['a_mark']}** marks  \n"
            f"**Execution:** {sr['execution']} → **{sr['e_mark']}** marks  \n"
            f"**Lab Record:** {sr['labrecord']} → **{sr['r_mark']}** marks  \n"
            f"**Total Marks (out of 25):** **{sr['total']}**"
        )

    if submitted:
        name = st.session_state.get("name", "")
        roll = st.session_state.get("roll", "")
        attendance = st.session_state.get("attendance", 0)
        execution = st.session_state.get("execution", "no")
        labrecord = st.session_state.get("labrecord", "no")

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
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx", "xls", "csv"])

    if uploaded is not None:
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

            invalid_att = out_df[out_df["AttendanceMarks"].isna()]
            if not invalid_att.empty:
                st.warning(f"{len(invalid_att)} rows had invalid attendance values (AttendanceMarks blank). Check those rows.")
                st.dataframe(invalid_att[["Name", "Roll", "Attendance"]].head(10))

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

st.markdown("---")
st.markdown(
    "**Notes:**\n\n"
    "- `Execution` accepted values: `yes`, `no`, `badoutput` (case-insensitive on upload).\n"
    "- `LabRecord` accepted values: `yes` or `no`.\n"
    "- Attendance must be numeric (0–100). Rows with invalid attendance will still be included but AttendanceMarks will be blank."
)
