
import os
from dotenv import load_dotenv
load_dotenv()

GH_KEY  = os.getenv("GH_KEY")
DB_NAME  = os.getenv("DB_NAME")

# Used for testing
OFFLINE_MODE=True