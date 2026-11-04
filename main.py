"""Entrypoint: `python main.py` for local development, or `uvicorn app.main:app` in production."""

from app.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
