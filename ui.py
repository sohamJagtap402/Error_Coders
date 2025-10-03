import streamlit as st
from PIL import Image

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AP Shah Attendance System",
    page_icon="📝",
    layout="wide"
)

# -------------------------------
# HEADER (Logo + College Name)
# -------------------------------
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    logo = Image.open("C:\errorcoders\Error_Coders\src\image.png")  # ensure file is in the same folder
    st.image(logo, width=120)

with col2:
    st.markdown(
        """
        <div style="text-align: center; font-size:30px; font-weight:bold;">
            A.P. Shah Institute of Technology, Thane
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="text-align: center; font-size:20px; color:gray;">
            Department of Computer Engineering
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.empty()

st.write("---")

# -------------------------------
# DATA STRUCTURE FOR SUBJECTS
# -------------------------------
subjects_data = {
    "First Year": {
        "Semester 1": ["Mathematics I", "Physics I", "Chemistry I", "Engineering Graphics", "Basic Electrical Engg"],
        "Semester 2": ["Mathematics II", "Physics II", "Communication Skills", "C Programming", "Engineering Mechanics"]
    },
    "Second Year": {
        "Semester 3": ["Data Structures", "Digital Logic", "OOP in C++", "Discrete Mathematics", "Computer Architecture"],
        "Semester 4": ["Database Management", "Computer Networks", "Operating Systems", "Software Engineering", "Microprocessors"]
    },
    "Third Year": {
        "Semester 5": ["Design & Analysis of Algorithms", "Theory of Computation", "Computer Graphics", "Advanced DBMS", "Professional Elective I"],
        "Semester 6": ["Machine Learning", "Artificial Intelligence", "Web Technologies", "Compiler Design", "Professional Elective II"]
    },
    "Final Year": {
        "Semester 7": ["Big Data Analytics", "Cloud Computing", "Cyber Security", "Elective III", "Elective IV"],
        "Semester 8": ["Project Phase II", "IoT", "Blockchain Technology", "Elective V", "Elective VI"]
    }
}

# -------------------------------
# UPLOAD + SELECTION WORKFLOW
# -------------------------------
st.subheader("📤 Upload Attendance Sheet")

# Step 1: Select Year
year = st.selectbox("Select Year", list(subjects_data.keys()))

# Step 2: Select Semester
semester = st.selectbox("Select Semester", list(subjects_data[year].keys()))

# Step 3: Select Subject
subject = st.selectbox("Select Subject", subjects_data[year][semester])

# Step 4: Upload File
uploaded_file = st.file_uploader(f"Upload Attendance Sheet for {subject}", type=["pdf"])

# Step 5: Generate Report
if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")

    st.write("### 📊 Generate Reports")
    colA, colB = st.columns(2)

    with colA:
        if st.button("📑 Generate Summary Report"):
            st.info(f"Summary Report generated for {subject} ({year}, {semester}).")
            st.write("🔹 Placeholder: Attendance summary table will appear here.")

    with colB:
        if st.button("🚨 Generate Defaulter List"):
            st.warning(f"Defaulter List generated for {subject} ({year}, {semester}).")
            st.write("🔹 Placeholder: Defaulter list with roll numbers will appear here.")

else:
    st.info("Please upload a PDF file after selecting year, semester, and subject.")

st.write("---")

# -------------------------------
# EXTRA FEATURES PLACEHOLDER
# -------------------------------
st.subheader("✨ Extra Features (Future Scope)")
st.write("🔘 Signature Detection")
st.write("🔘 Attendance Anomaly Charts")
st.write("🔘 Auto Report Mailing")
st.write("🔘 AI-based Attendance Correction")

# -------------------------------
# FOOTER LINK
# -------------------------------
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px;">
        <a href="https://www.apsit.edu.in" target="_blank" style="color:#00BFFF; font-size:16px; text-decoration:none;">
            Visit A.P. Shah Institute of Technology Website
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
