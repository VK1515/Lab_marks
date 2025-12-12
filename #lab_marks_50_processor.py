#lab_marks_50_processor.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.title("📊 Student Marks Evaluation System")

menu = st.sidebar.selectbox("Menu", ["Single Entry", "Bulk Upload & Analytics"])

# Function to calculate marks for each row
def compute_marks(row):
    # SAQ marks (2 each)
    saq = int(row.get("SAQ", 0))
    saq_marks = saq * 2

    # Program 1
    p1 = str(row.get("Program 1", '4'))
    p1_marks = {'1':10, '2':7, '3':5, '4':0}.get(p1, 0)

    # Program 2
    p2 = str(row.get("Program 2", '4'))
    p2_marks = {'1':10, '2':7, '3':5, '4':0}.get(p2, 0)

    # Execution
    execn = str(row.get("Execution", "")).lower()
    exec_marks = 5 if execn == "yes" else 0

    # Lab record
    lab = str(row.get("Lab Record", "")).lower()
    lab_marks = 5 if lab == "yes" else 0

    # Viva
    viva = int(row.get("Viva", 0))

    total_score = saq_marks + p1_marks + p2_marks + exec_marks + lab_marks + viva

    return pd.Series({
        "SAQ Marks": saq_marks,
        "Program1 Marks": p1_marks,
        "Program2 Marks": p2_marks,
        "Execution Marks": exec_marks,
        "Lab Record Marks": lab_marks,
        "Viva Marks": viva,
        "Total Marks": total_score
    })


# --------------------------- Single Entry ---------------------------
if menu == "Single Entry":
    st.header("👨‍🎓 Single Student Entry")

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")

    saq = st.number_input("Number of SAQs Answered", 0, 5)

    prog1 = st.selectbox("Program 1", ["1","2","3","4"],
                         format_func=lambda x:
                         "1. Perfect (10)" if x=='1' else
                         "2. Few Errors (7)" if x=='2' else
                         "3. Many Errors (5)" if x=='3' else
                         "4. Not Attempted (0)")

    prog2 = st.selectbox("Program 2", ["1","2","3","4"],
                         format_func=lambda x:
                         "1. Perfect (10)" if x=='1' else
                         "2. Few Errors (7)" if x=='2' else
                         "3. Many Errors (5)" if x=='3' else
                         "4. Not Attempted (0)")

    execution = st.selectbox("Execution Successful?", ["yes", "no"])

    lab = st.selectbox("Lab Record Submitted?", ["yes", "no"])

    viva = st.number_input("Viva Marks", 0, 15)

    if st.button("Generate Report"):
        data = {
            "SAQ": saq,
            "Program 1": prog1,
            "Program 2": prog2,
            "Execution": execution,
            "Lab Record": lab,
            "Viva": viva
        }
        df = pd.DataFrame([data])
        res = compute_marks(df.iloc[0])

        st.markdown("### 📋 Student Report")
        st.write(f"**Name:** {name}")
        st.write(f"**Roll No:** {roll}")
        st.write(f"SAQ: {saq} × 2 → {res['SAQ Marks']} marks")
        st.write(f"Program 1 → {res['Program1 Marks']} marks")
        st.write(f"Program 2 → {res['Program2 Marks']} marks")
        st.write(f"Execution: {execution} → {res['Execution Marks']} marks")
        st.write(f"Lab Record: {lab} → {res['Lab Record Marks']} marks")
        st.write(f"Viva → {res['Viva Marks']} marks")
        st.write(f"**Total Marks:** {res['Total Marks']}")


# --------------------------- Bulk Upload & Analytics ---------------------------
else:
    st.header("📥 Bulk Excel Upload + Analytics")

    st.markdown("""
    Upload an Excel file (.xlsx) with these columns:
    - Name  
    - Roll  
    - SAQ  
    - Program 1  
    - Program 2  
    - Execution  
    - Lab Record  
    - Viva
    """)

    file = st.file_uploader("Select Excel file", type=["xlsx"])

    if file:
        df = pd.read_excel(file)
        st.write("📊 Uploaded Data")
        st.dataframe(df)

        # compute marks
        results = df.apply(compute_marks, axis=1)
        final = pd.concat([df, results], axis=1)

        st.write("✅ Calculated Results")
        st.dataframe(final)

        # Download result
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            final.to_excel(writer, index=False, sheet_name="Results")
        buffer.seek(0)

        st.download_button(
            label="📥 Download Result Excel",
            data=buffer,
            file_name="calculated_student_marks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # ===== Charts =====
        st.subheader("📈 Performance Charts")

        # Bar chart — Total Marks distribution
        st.markdown("### 📊 Total Marks Distribution")
        fig1, ax1 = plt.subplots()
        ax1.bar(final["Name"], final["Total Marks"], color="teal")
        ax1.set_xlabel("Students")
        ax1.set_ylabel("Total Marks")
        ax1.set_xticklabels(final["Name"], rotation=45, ha='right')
        st.pyplot(fig1)

        # Optional: pie chart for grade ranges
        st.markdown("### 🟡 Grade Distribution")
        bins = [0, 20, 35, 50, 70, 100]
        labels = ["0–20", "21–35", "36–50", "51–70", "71–100"]
        grades = pd.cut(final["Total Marks"], bins=bins, labels=labels, right=True)
        fig2, ax2 = plt.subplots()
        grades.value_counts().plot.pie(autopct="%1.1f%%", ax=ax2)
        ax2.set_ylabel("")
        st.pyplot(fig2)
