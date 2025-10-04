import streamlit as st
from PIL import Image
import os
# Import the new "bridge" function that uses Gemini
from src.report_generator import generate_final_report_with_gemini

# --- PAGE CONFIG ---
st.set_page_config(page_title="AP Shah Attendance System", page_icon="📝", layout="wide")

# --- HEADER ---
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if os.path.exists("src/image.png"):
        st.image(Image.open("src/image.png"), width=120)
with col2:
    st.markdown("<div style='text-align: center; font-size:30px; font-weight:bold;'>A.P. Shah Institute of Technology, Thane</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size:20px; color:gray;'>Department of Computer Engineering</div>", unsafe_allow_html=True)
with col3:
    st.empty()
st.write("---")

# --- API KEY INPUT ---
st.subheader("🔑 Gemini API Key")
api_key = st.text_input("Enter your Google Gemini API Key to enable vision processing:", type="password")
if not api_key:
    st.warning("Please enter a valid Gemini API Key to proceed.")
    st.stop()

# --- SUBJECTS DATA ---
subjects_data = {
    "First Year": { "Semester 1": ["Mathematics I", "Physics I"], "Semester 2": ["Mathematics II", "C Programming"] },
    "Second Year": { "Semester 3": ["Data Structures", "OOP in C++"], "Semester 4": ["Database Management", "Operating Systems"] },
    "Third Year": { "Semester 5": ["Design & Analysis of Algorithms", "Computer Graphics"], "Semester 6": ["Machine Learning", "Web Technologies"] },
    "Final Year": { "Semester 7": ["Big Data Analytics", "Cloud Computing"], "Semester 8": ["Project Phase II", "IoT"] }
}

# --- UPLOAD WORKFLOW ---
st.subheader("📤 Upload and Process Attendance Sheet")
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

year = st.selectbox("Select Year", list(subjects_data.keys()))
semester = st.selectbox("Select Semester", list(subjects_data[year].keys()))
subject = st.selectbox("Select Subject", subjects_data[year][semester])

uploaded_file = st.file_uploader(f"Upload Attendance Sheet for {subject}", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")

    if st.button(f"🚀 Generate Report with Gemini Vision", type="primary"):
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("🤖 Gemini is analyzing the document... This may take a moment."):
            try:
                # Call the powerful Gemini backend function
                report_path = generate_final_report_with_gemini(api_key, file_path, "reports", subject)
                st.success("✅ Report generated successfully!")

                with open(report_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Gemini Vision Report",
                        data=file,
                        file_name=os.path.basename(report_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.warning("This could be due to an invalid API key, a poor quality scan, or an issue with the Gemini API.")

else:
    st.info("Please upload a file after selecting the year, semester, and subject.")

st.write("---")
# --- FOOTER ---
st.markdown("<div style='text-align: center; margin-top: 50px;'><a href='https://www.apsit.edu.in' target='_blank' style='color:#00BFFF; font-size:16px; text-decoration:none;'>Visit A.P. Shah Institute of Technology Website</a></div>", unsafe_allow_html=True)