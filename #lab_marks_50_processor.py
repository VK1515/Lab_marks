#lab_marks_50_processor.py
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("📊 Student Marks Calculator")

# Sidebar menu
menu = st.sidebar.selectbox("Menu", ["Single Entry", "Bulk Upload"])

# Function to calculate total marks
def calculate_marks(row):
    # record
    b = 5 if str(row.get('Record','')).lower() == 'y' else 0

    # SAQ marks
    saq_marks = int(row.get('SAQ', 0)) * 2

    # Program 1
    p1 = str(row.get('Program 1', '4'))
    p1_score = {'1':10, '2':7, '3':5, '4':0}.get(p1, 0)

    # Program 2
    p2 = str(row.get('Program 2', '4'))
    p2_score = {'1':10, '2':7, '3':5, '4':0}.get(p2, 0)

    viva = int(row.get('Viva', 0))

    total = b + saq_marks + p1_score + p2_score + viva
    return pd.Series({
        "Record": b,
        "SAQ Marks": saq_marks,
        "Program1": p1_score,
        "Program2": p2_score,
        "Viva": viva,
        "Total": total
    })

if menu == "Single Entry":
    st.header("Single Student Entry")

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")

    record = st.selectbox("Record Submitted?", ['y','n'])
    saq = st.number_input("Number of SAQs Answered", 0, 5)

    prog1 = st.selectbox("1st Program", ["1","2","3","4"], format_func=lambda x: 
                          "1. Perfect (10)" if x=='1' else
                          "2. Few Errors (7)" if x=='2' else
                          "3. Many Errors (5)" if x=='3' else
                          "4. Not Attempted (0)")
    prog2 = st.selectbox("2nd Program", ["1","2","3","4"], format_func=lambda x: 
                          "1. Perfect (10)" if x=='1' else
                          "2. Few Errors (7)" if x=='2' else
                          "3. Many Errors (5)" if x=='3' else
                          "4. Not Attempted (0)")

    viva = st.number_input("Viva Marks", 0, 15)

    if st.button("Calculate"):
        data = {
            "Record": record,
            "SAQ": saq,
            "Program 1": prog1,
            "Program 2": prog2,
            "Viva": viva
        }
        df = pd.DataFrame([data])
        result = calculate_marks(df.iloc[0])

        st.write("### 🧾 Mark Sheet")
        st.write(f"**Name:** {name}")
        st.write(f"**Roll:** {roll}")
        st.write(result.to_frame().T)

elif menu == "Bulk Upload":
    st.header("Bulk Excel Upload")

    uploaded_file = st.file_uploader("Upload Excel file with student data", type=["xlsx"])
    st.markdown("""
    The Excel should have columns:  
    **Name, Roll, Record (y/n), SAQ, Program 1 (1–4), Program 2 (1–4), Viva**  
    """)

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("📥 Uploaded Data")
        st.dataframe(df)

        # calculate for all
        results = df.apply(calculate_marks, axis=1)
        final = pd.concat([df[['Name','Roll']], results], axis=1)

        st.write("✅ Calculated Results")
        st.dataframe(final)

        # Excel download
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            final.to_excel(writer, index=False, sheet_name="Results")
        buffer.seek(0)

        st.download_button(
            label="📥 Download Results as Excel",
            data=buffer,
            file_name="calculated_marks.xlsx",
            mime="application/vnd.ms-excel"
        )
