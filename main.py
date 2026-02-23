from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from generator import generate_storyboard
import os

app = FastAPI(title="Storyboard Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


class StoryboardRequest(BaseModel):
    idea: str
    num_scenes: int = 4


@app.get("/")
def root():
    return {"status": "Storyboard Generator API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
async def generate(req: StoryboardRequest):
    if not req.idea.strip():
        raise HTTPException(status_code=400, detail="Idea cannot be empty")
    if req.num_scenes < 1 or req.num_scenes > 8:
        raise HTTPException(status_code=400, detail="num_scenes must be between 1 and 8")

    try:
        result = generate_storyboard(req.idea, req.num_scenes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))