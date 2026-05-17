from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.routers import data_handler
from fastapi.responses import HTMLResponse
from src.db import init_db
from src.routers import auth
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CAG Project Api Chatwith Your PDF ",
    description="API for uploading PDFs, querying content through LLMs, and managing data.",
    version="0.1.0",
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

app.include_router(
    data_handler.router,
    prefix="/api/v1",
    tags=["Data Handling and chat with your PDF"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173", "http://localhost:4173", "http://127.0.0.1:4173", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

logger.add("logs/app.log", rotation="1 week", retention="4 weeks", level="INFO")
logger.info("Starting CAG Project API application.")


@app.get("/", response_class=HTMLResponse, tags=["Root"])
def read_root():
    """Provide a modern styled HTML Welcome page with a link to Swagger docs."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CAG Project API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(120deg, #f0f8ff, #e6f2ff);
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                color: #333;
                text-align: center;
            }
            h1 {
                font-size: 3em;
                color: #0056b3;
                margin-bottom: 0.5em;
            }
            p {
                font-size: 1.3em;
                max-width: 600px;
                margin: 0.5em 20px;
            }
            a {
                display: inline-block;
                margin-top: 1.5em;
                padding: 12px 24px;
                font-size: 1.1em;
                color: #fff;
                background-color: #007bff;
                border-radius: 6px;
                text-decoration: none;
                transition: background-color 0.3s ease;
            }
            a:hover {
                background-color: #0056b3;
            }
            .footer {
                position: absolute;
                bottom: 20px;
                font-size: 0.9em;
                color: #888;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Welcome to CAG Project API</h1>
        <p>An API for uploading PDFs, querying content through LLMs, and managing document data efficiently.</p>
        <a href="/docs">Go to Swagger Documentation</a>
        <div class="footer">© 2025 CAG Project - All rights reserved.</div>
    </body>
    </html>
    """
    return HTMLResponse(html_content, status_code=200)


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI using Uvicorn
    # You can also test this using tools like curl, Postman, or Insomnia
    uvicorn.run(app, host="127.0.0.1", port=8001)
