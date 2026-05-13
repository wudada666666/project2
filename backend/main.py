from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import words, progress, ai

app = FastAPI(title="CET-6 Vocabulary API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(words.router)
app.include_router(progress.router)
app.include_router(ai.router)


@app.get("/")
def root():
    return {"service": "CET-6 Vocabulary API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
