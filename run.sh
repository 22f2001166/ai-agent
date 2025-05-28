# Clone and install packages mentioned in requirements.txt
# create .env for config.py variables

# for backend (in one terminal)
python -c "from vectorstore import build_vector_index; build_vector_index()"
python -c "from db import load_csv_to_sqlite; load_csv_to_sqlite()"
uvicorn main:app --reload 

# for frontend (in another terminal)
cd frontend
npm install
npm install axios
npm run dev