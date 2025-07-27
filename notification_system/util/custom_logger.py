import os
import logging
from dotenv import load_dotenv

load_dotenv()
file_log_path = os.getenv('UNIX_LOG_FILE_PATH')

def getLogger(name='notification_app', log_level='DEBUG'):
    if not os.path.exists(file_log_path):
        with open(file_log_path, 'w') as f:
            f.write("This is some content for the new file.\n")

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if logger.handlers:
        return logger
    else:
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(file_log_path, mode="a", encoding="utf-8")
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        formatter = logging.Formatter(
            "{asctime} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        return logger
