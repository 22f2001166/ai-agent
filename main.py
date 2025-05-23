from fastapi import FastAPI, Request
from pydantic import BaseModel
from hybrid_agent import handle_query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",  # React dev server origin
    "http://localhost:5173",  # Vite dev server origin
    # add your frontend deployed URL here after deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all (for dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    user_input: str
    user_role: str
    region: str


@app.post("/query/")
async def query_handler(query: Query):
    response = handle_query(query.user_input, query.user_role, query.region)
    return response
