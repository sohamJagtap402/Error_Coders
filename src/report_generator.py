import cv2
import numpy as np
import pandas as pd
import re
from datetime import datetime
from src.image_processor import get_image_from_upload, preprocess_for_ocr
from skimage.metrics import structural_similarity as ssim
import easyocr

# Initialize the EasyOCR reader. This is done once and the models are loaded into memory.
reader = easyocr.Reader(['en'])

def get_signature_cells(row_image, num_cols):
    """Safely splits a student's row image into individual cells for each date."""
    cells = []
    h, w = row_image.shape[:2]
    if w == 0 or h == 0 or num_cols == 0: return []
    col_width = w // num_cols
    for j in range(num_cols):
        cells.append(row_image[:, j*col_width:(j+1)*col_width])
    return cells

def detect_cancelled_columns(header_image, num_cols):
    """Detects attendance columns that have been crossed out."""
    cancelled = [False] * num_cols
    h, w = header_image.shape[:2]
    if w == 0 or h == 0 or num_cols == 0: return cancelled
    col_width = w // num_cols
    for i in range(num_cols):
        col_crop = header_image[:, i*col_width:(i+1)*col_width]
        gray = cv2.cvtColor(col_crop, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        lines = cv2.HoughLinesP(binary, 1, np.pi/180, threshold=20, minLineLength=col_width*0.6, maxLineGap=10)
        if lines is not None:
            cancelled[i] = True
    return cancelled

def analyze_row_consistency(signature_cells):
    """
    Analyzes signatures in a single row to determine attendance status.
    Returns: 'P' (Present), 'AB' (Absent), or 'INV' (Invalid Signature).
    """
    SIMILARITY_THRESHOLD = 0.45

    present_cells = []
    for idx, cell in enumerate(signature_cells):
        if cell is None or cell.size == 0: continue
        gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        density = np.count_nonzero(cv2.adaptiveThreshold(gray_cell, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                        cv2.THRESH_BINARY_INV, 11, 3)) / gray_cell.size
        if density > 0.008:
            present_cells.append({'idx': idx, 'img': gray_cell})

    if not present_cells:
        return ["AB"] * len(signature_cells)

    reference_signature = cv2.resize(present_cells[0]['img'], (100, 50))
    cell_statuses = {cell['idx']: "INV" for cell in present_cells}
    cell_statuses[present_cells[0]['idx']] = "P"

    for i in range(1, len(present_cells)):
        current_signature = cv2.resize(present_cells[i]['img'], (100, 50))
        score, _ = ssim(reference_signature, current_signature, full=True)
        if score > SIMILARITY_THRESHOLD:
            cell_statuses[present_cells[i]['idx']] = "P"
            
    final_statuses = ["AB"] * len(signature_cells)
    for idx, status in cell_statuses.items():
        final_statuses[idx] = status
        
    return final_statuses

def generate_final_report(file_path, output_folder):
    """The main pipeline to generate the final, styled attendance report."""
    original_image = get_image_from_upload(file_path)

    gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    binary_inv = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(binary_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(table_contour)

    student_info_x2 = x + int(w * 0.40)
    student_info_crop = original_image[y:y+h, x:student_info_x2]
    processed_student_info = preprocess_for_ocr(student_info_crop)
    
    student_records = []
    if processed_student_info is not None:
        student_results = reader.readtext(processed_student_info, paragraph=False)
        for i, (_, text, _) in enumerate(student_results):
            if text.strip().isdigit() and len(text.strip()) >= 8:
                name = ""
                if i + 1 < len(student_results):
                    name_candidate = student_results[i+1][1]
                    if not name_candidate.strip().isdigit():
                        name = name_candidate
                student_records.append({"Moodle ID": text.strip(), "Name": name.strip()})

    grid_x1 = student_info_x2
    dates_header_crop = original_image[max(0, y-100):y, grid_x1:x+w]
    num_date_cols = 7
    cancelled_cols = detect_cancelled_columns(dates_header_crop, num_date_cols)
    
    processed_dates_header = preprocess_for_ocr(dates_header_crop)
    extracted_dates = []
    if processed_dates_header is not None:
        date_results = reader.readtext(processed_dates_header, detail=0)
        extracted_dates = [re.sub(r'[^0-9/]', '', d) for d in date_results if re.search(r'\d', d)]
    while len(extracted_dates) < num_date_cols:
        extracted_dates.append(f"Date_{len(extracted_dates)+1}")

    if student_records:
        attendance_grid_crop = original_image[y:y+h, grid_x1:x+w]
        row_height = attendance_grid_crop.shape[0] / len(student_records)
        for i, record in enumerate(student_records):
            row_y1, row_y2 = int(i * row_height), int((i + 1) * row_height)
            student_row_crop = attendance_grid_crop[row_y1:row_y2, :]
            
            signature_cells = get_signature_cells(student_row_crop, num_date_cols)
            statuses = analyze_row_consistency(signature_cells)
            
            for j, date in enumerate(extracted_dates):
                column_name = date if date else f"Date_{j+1}"
                record[column_name] = "AB" if cancelled_cols[j] else statuses[j]

    df = pd.DataFrame(student_records)
    date_cols = [col for col in df.columns if col not in ["Moodle ID", "Name"]]
    
    df['Attended'] = df[date_cols].apply(lambda row: (row == 'P').sum(), axis=1)
    df['Total'] = len(date_cols)
    df['Percentage'] = (df['Attended'] / df['Total'] * 100).round(2)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_folder}/Final_Attendance_Report_{timestamp}.xlsx"

    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Attendance Report', index=False)
    
    workbook = writer.book
    worksheet = writer.sheets['Attendance Report']
    
    formats = {
        'P': workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'}),
        'AB': workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'}),
        'INV': workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
    }
    
    for status, fmt in formats.items():
        worksheet.conditional_format(1, 2, len(df)+1, len(date_cols)+1, 
                                     {'type': 'cell', 'criteria': '==', 'value': f'"{status}"', 'format': fmt})
    
    writer.close()
    return output_path