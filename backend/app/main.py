from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.uploads import router as uploads_router

app = FastAPI(
    title="RepoLens API",
    description="Backend API for analysing software repositories.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(uploads_router)

@app.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "healthy"}