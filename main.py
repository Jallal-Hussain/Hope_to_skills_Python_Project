import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from src.routers import data_handler
from src.db import init_db
from src.routers import auth
from src.config import APP_ENV, FRONTEND_ORIGINS, HOST, PORT, DEBUG
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CAG Project Api Chatwith Your PDF ",
    description="API for uploading PDFs, querying content through LLMs, and managing data.",
    version="0.1.0",
    debug=DEBUG,
)


@app.middleware("http")
async def add_security_headers_and_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; "
        "img-src 'self' data:; style-src 'self' 'unsafe-inline';"
    )
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    logger.warning(f"HTTP exception for {request.url.path} [{correlation_id}]: {exc.status_code} {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail if exc.status_code < 500 else "Request failed.", "correlation_id": correlation_id},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    logger.exception(f"Unhandled server exception [{correlation_id}] for path {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred.", "correlation_id": correlation_id},
    )


app.include_router(
    data_handler.router,
    prefix="/api/v1",
    tags=["Data Handling and chat with your PDF"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
)

init_db()

logger.add("logs/app.log", rotation="1 week", retention="4 weeks", level="INFO")
logger.info(f"Starting CAG Project API application in {APP_ENV} mode.")


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
