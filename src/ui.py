import streamlit as st
import pandas as pd
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
    logo = Image.open("C:\errorcoders\Error_Coders\src\image.png")  # ensure the file is in the same folder
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
    st.empty()  # right space for symmetry

st.write("---")

# -------------------------------
# FUTURE FEATURE PLACEHOLDERS
# -------------------------------
st.subheader("📤 Upload Attendance Sheet")
uploaded_file = st.file_uploader("Upload scanned attendance sheet (Image/PDF)", type=["jpg", "jpeg", "png", "pdf"])

st.subheader("🔍 Processing Area")
st.info("This section will show extracted data, anomalies, and reports once implemented.")

st.subheader("📥 Reports Section")
st.warning("Reports will be available here for download.")

# Keep extra space for more buttons/features
st.subheader("✨ Extra Features (Future Scope)")
st.write("🔘 Space reserved for additional features like signature detection, anomaly charts, etc.")

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