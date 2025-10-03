import streamlit as st
import os
from src.report_generator import generate_final_report

st.set_page_config(page_title="Attendance Processor", layout="wide")
st.title("🎓 Automated Attendance Processor")
st.subheader("The ultimate tool for digitizing and analyzing attendance sheets with high-accuracy OCR and signature consistency checks.")

os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

uploaded_file = st.file_uploader("Upload an attendance sheet (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"File '{uploaded_file.name}' uploaded successfully.")
    
    if st.button("✨ Generate Final Report", type="primary"):
        with st.spinner("Performing advanced analysis... Please wait, this may take a moment."):
            try:
                report_path = generate_final_report(file_path, "reports")
                st.success("✅ Report generated successfully!")
                
                with open(report_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Color-Coded Excel Report",
                        data=file,
                        file_name=os.path.basename(report_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.warning("This could be due to a highly unusual document format or a very poor quality scan. Please try again with a clearer document.")