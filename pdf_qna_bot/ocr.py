import pdf2image
import pytesseract
from pytesseract import Output
import tempfile
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
# Function to extract text from PDF using OCR
def extract_text_from_pdf(uploaded_file):
    try:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_pdf_path = temp_file.name  # Get the temporary file path
        
        # Convert PDF to images
        images = pdf2image.convert_from_path(temp_pdf_path)
        
        # Extract text from each page using OCR
        full_text = ""
        for pil_im in images:
            ocr_dict = pytesseract.image_to_data(pil_im, lang='eng', output_type=Output.DICT)
            text = " ".join([line for line in ocr_dict['text'] if line.strip() != ''])
            full_text += text + "\n"  # Add text from each page

        return full_text
    except Exception as e:
        raise ValueError(f"Error during OCR: {e}")
