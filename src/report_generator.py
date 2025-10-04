import pandas as pd
from datetime import datetime
import fitz  # PyMuPDF
import os
import json
from PIL import Image
import io
import google.generativeai as genai

# --- HELPER FUNCTIONS ---

def get_image_from_file(file_path):
    """Loads a high-quality image from a PDF or image file."""
    if str(file_path).lower().endswith('.pdf'):
        doc = fitz.open(str(file_path))
        page = doc.load_page(0) # Process the first page
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img
    else:
        return Image.open(file_path)

# --- THE CORE GEMINI VISION LOGIC ---

def generate_final_report_with_gemini(api_key, file_path, output_folder, subject_name):
    """
    The main pipeline that uses Gemini Vision to analyze the attendance sheet.
    """
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro-vision')

    # Load the attendance sheet as an image
    full_image = get_image_from_file(file_path)

    # --- 1. Holistic Information Extraction with Gemini ---
    # This prompt asks Gemini to read the entire sheet and extract the key information.
    prompt_for_structure = """
    Analyze this image of a student attendance sheet from A.P. Shah Institute of Technology.
    Your task is to extract the following information in a clean JSON format:
    1.  A list of all students, where each student is an object with "moodle_id" and "name".
    2.  A list of the handwritten dates from the attendance column headers. If a date is unreadable, represent it as "Unknown".
    3.  The bounding box coordinates [x_min, y_min, x_max, y_max] for the main attendance grid where the signatures are marked.

    Do not include any students who do not have a Moodle ID.
    The final output should be a single JSON object.
    """

    print("Asking Gemini to understand the document structure...")
    response = model.generate_content([prompt_for_structure, full_image])
    
    # Clean and parse the JSON response from Gemini
    json_response_text = response.text.strip().replace('```json', '').replace('```', '')
    structure_data = json.loads(json_response_text)
    
    students = structure_data.get("students", [])
    dates = structure_data.get("dates", [])
    grid_bbox = structure_data.get("grid_bbox")

    if not students or not dates or not grid_bbox:
        raise ValueError("Gemini could not extract the required structure. The image may be unclear or in an unexpected format.")

    # --- 2. Advanced Cell-by-Cell Analysis with Gemini ---
    attendance_grid_crop = full_image.crop(grid_bbox)
    num_students = len(students)
    num_dates = len(dates)
    row_height = attendance_grid_crop.height / num_students
    col_width = attendance_grid_crop.width / num_dates

    # This is the prompt for analyzing each individual attendance cell
    prompt_for_cell = """
    Analyze this single attendance cell based on these rules, in strict order of priority:
    1.  If you see a red 'AB' or a red strikethrough line, the status is 'Absent'.
    2.  If rule 1 does not apply, look for any handwritten signature (in blue, black, etc.). If a signature is present, the status is 'Present', even if it's on top of other text.
    3.  If neither of the above is true, the status is 'Absent'.

    Respond with only a single word: 'Present' or 'Absent'.
    """

    all_attendance_records = []
    for i, student in enumerate(students):
        print(f"Analyzing row for {student['name']}...")
        student_record = {"Moodle ID": student["moodle_id"], "Name": student["name"]}
        row_y1 = i * row_height
        row_y2 = (i + 1) * row_height

        for j, date in enumerate(dates):
            col_x1 = j * col_width
            col_x2 = (j + 1) * col_width
            
            # Crop the specific cell for one student on one date
            cell_bbox = (col_x1, row_y1, col_x2, row_y2)
            cell_image = attendance_grid_crop.crop(cell_bbox)
            
            # Ask Gemini to analyze the cell
            response = model.generate_content([prompt_for_cell, cell_image])
            status = response.text.strip()
            
            column_name = date if date != "Unknown" else f"Date_{j+1}"
            student_record[column_name] = "P" if "Present" in status else "AB"
        
        all_attendance_records.append(student_record)

    # --- 3. Final Report Generation ---
    df = pd.DataFrame(all_attendance_records)
    date_cols = [col for col in df.columns if col not in ["Moodle ID", "Name"]]
    
    df['Attended'] = df[date_cols].apply(lambda row: (row == 'P').sum(), axis=1)
    df['Total'] = len(date_cols)
    df['Percentage'] = (df['Attended'] / df['Total'] * 100).round(2)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Gemini_Report_{subject_name.replace(' ', '_')}_{timestamp}.xlsx"
    output_path = os.path.join(output_folder, filename)

    df.to_excel(output_path, sheet_name='Attendance Report', index=False)
    
    return output_path