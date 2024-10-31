from dotenv import load_dotenv

load_dotenv()

import os
import logging

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))