import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_URI

# Create engine
engine = create_engine(DB_URI)


# Function to load CSV into SQLite
def load_csv_to_sqlite():
    df = pd.read_csv("data/DataCoSupplyChainDataset.csv", encoding="ISO-8859-1")
    df.to_sql("inventory", engine, if_exists="replace", index=False)
    print("Database loaded with supply chain data.")


# Function to query the database
def query_sql(sql_query: str):
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        return [dict(row._mapping) for row in result]  # safer dict conversion
