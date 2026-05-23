from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers import words, progress, ai, auth

app = FastAPI(title="CET-6 Vocabulary API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(words.router)
app.include_router(progress.router)
app.include_router(ai.router)


DIST_DIR = Path(__file__).parent / "frontend" / "dist"


@app.get("/")
def root():
    return FileResponse(DIST_DIR / "index.html")


@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    file = DIST_DIR / request.url.path.lstrip("/")
    if file.is_file():
        return FileResponse(file)
    return FileResponse(DIST_DIR / "index.html")


app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
