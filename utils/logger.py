import logging

def setup_logger():
    logger = logging.getLogger("WebShield")
    logger.setLevel(logging.DEBUG)
    
    handler = logging.FileHandler("webshield.log")
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

logger = setup_logger()
