import sys
from ocr_processing import extract_table_from_file
from data_preprocessing import preprocess_image
from normalization import normalize_attendance_marks
from anomaly_detection import detect_anomalies
from attendance_calculation import calculate_attendance
from excel_export import export_to_excel

def main(file_path, output_path):
    """
    Pipeline entry point for processing attendance sheets.
    :param file_path: Path to input scanned image/PDF file
    :param output_path: Path to final output Excel file
    """

    print("Starting preprocessing...")
    preprocessed_data = preprocess_image(file_path)

    print("Extracting table data via OCR...")
    extracted_data = extract_table_from_file(preprocessed_data)

    print("Normalizing attendance marks...")
    normalized_data = normalize_attendance_marks(extracted_data)

    print("Detecting anomalies and proxies...")
    anomalies = detect_anomalies(normalized_data)

    print("Calculating attendance percentages...")
    attendance_summary = calculate_attendance(normalized_data, anomalies)

    print(f"Exporting final report to {output_path}...")
    export_to_excel(attendance_summary, anomalies, output_path)

    print("Processing complete!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_file_path> <output_excel_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    main(input_file, output_file)
