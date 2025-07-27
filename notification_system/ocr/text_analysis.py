import cv2
import re
import pytesseract
import os
from dotenv import load_dotenv
from util.custom_logger import getLogger

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_INSTALLATION_PATH')
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
load_dotenv()
extracted_dates = []
extracted_amounts = []
logger = getLogger()

def image_preprocessing(filename):
    logger.info(f"Operation [image_preprocessing] started filaname {filename}")
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    logger.info("Operation [image_preprocessing] finished ")
    return thresh

def get_text_from_image(image):
    logger.info("Operation [get_text_from_image] started ")
    text = pytesseract.image_to_string(image, lang='spa')
    logger.debug(f"Operation [get_text_from_image] text {text} ")
    logger.info("Operation [get_text_from_image] finished ")
    return text


def find_dates(text):
    logger.info("Operation [find_dates] started ")

    meses = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"

    date_pattern = rf"""
            \b(
                \d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}} |                    # 01/07/2025 or 1-7-25
                \d{{1,2}}\s*(?:de\s*)?{meses}(?:\s*de)?\s*\d{{4}} |      # 1 de julio de 2025
                \d{{1,2}}[-\s]{meses}[-\s]\d{{4}}                        # 01-julio-2025
            )\b
            """
    # Compile with verbose mode to allow multi-line pattern
    date_regex = re.compile(date_pattern, re.IGNORECASE | re.VERBOSE)
    dates = date_regex.findall(text)

    clean_dates = [''.join(d).strip() for d in dates]
    logger.info(f"Clean Dates {clean_dates} Dates {dates}")
    logger.info("Operation [find_dates] finished ")
    return clean_dates

def find_amounts(text):
    logger.info("Operation [find_amounts] started ")

    amount_pattern = r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2}))"
    amounts = re.findall(amount_pattern, text)
    clean_amounts = [re.sub(r'[,]', '', s) for s in amounts] #re.sub(,'',amounts)
    clean_amounts = [int(float(s)) for s in clean_amounts]
    logger.info(f"amounts {clean_amounts}")
    logger.info("Operation [find_amounts] finished ")
    return clean_amounts

def run_image_analysis(filename):
    image = image_preprocessing(filename)
    text = get_text_from_image(image)
    extracted_dates = find_dates(text)
    extracted_amounts = find_amounts(text)

    return {"dates":extracted_dates, "amounts":extracted_amounts}
