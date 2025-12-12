Lab Marks Processor - Streamlit app

Files in this package:
- app.py               : Streamlit application
- requirements.txt     : Python dependencies
- sample_input_marks.xlsx : Sample Excel input file structure

How to run locally:
1. Create a Python virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate   (Linux/macOS) or venv\Scripts\activate (Windows)
2. Install dependencies:
   pip install -r requirements.txt
3. Run Streamlit:
   streamlit run app.py

How to deploy to Streamlit Community Cloud:
1. Create a GitHub repo and push these files.
2. In share.streamlit.io, choose New app -> connect your repo -> select app.py -> Deploy.

Excel input requirements:
The Excel file must contain these columns (case-sensitive): Name, Roll, Attendance, Execution, LabRecord
Execution allowed values: yes / no / badoutput
LabRecord allowed values: yes / no
