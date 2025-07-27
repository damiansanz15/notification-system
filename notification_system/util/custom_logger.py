import logging


file_log_path = r'C:\Cursos\Python\notification-system\notification_system\notification-system.log'
def getLogger(name='notification_app', log_level='DEBUG'):
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
