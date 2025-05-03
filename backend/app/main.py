from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .recommender_v2 import BraFittingRAG
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

recommender = BraFittingRAG()

@app.post("/api/bra-fitting")
async def get_fitting_recommendation(query: Query):
    text = query.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text is empty. Please describe your measurements or issues.")

    try:
        result = recommender.get_recommendation(text)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"[BraFittingRAG] Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
