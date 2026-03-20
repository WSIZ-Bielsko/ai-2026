import os

from dotenv import load_dotenv
from loguru import logger

if __name__ == '__main__':
    load_dotenv()
    XAI_KEY = os.getenv('XAI_KEY')
    logger.info(XAI_KEY)