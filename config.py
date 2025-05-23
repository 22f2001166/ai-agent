from dotenv import load_dotenv
import os

load_dotenv()

# create .env to add these env variables
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
DB_URI = os.getenv("DB_URI")

# Simulated user metadata
# USER_PROFILE = {
#     "username": "alice",
#     "role": "Planner",  # or 'Finance'
#     "region": "India",
# }
