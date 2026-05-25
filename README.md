# CAG Project: Chat with Your PDF

## Landing Page

![Landing Page Screenshot](./Landing.png)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Frontend](#frontend)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Welcome to the **CAG Project: Chat with Your PDF**! This project provides a robust backend API built with FastAPI that allows users to upload PDF documents, extract their content, and interact with them using a Large Language Model (LLM). It supports user authentication, document management, conversational AI, and document summarization.

## Features

- **User Authentication**: Secure user registration and login with JWT-based authentication.
- **PDF Upload & Management**: Upload PDF files, extract text content, and manage them by unique UUIDs.
- **Document Querying**: Ask questions about the content of uploaded PDFs using an integrated LLM.
- **Conversational AI**: Engage in multi-turn conversations with your documents, maintaining chat history.
- **Document Summarization**: Generate concise summaries of your PDF documents.
- **File Download**: Download previously uploaded PDF files.
- **Database Integration**: Uses SQLAlchemy for ORM with support for SQLite (default) and MySQL.
- **CORS Enabled**: Configured for seamless integration with frontend applications.
- **Logging**: Comprehensive logging using `loguru` for application monitoring.

## Project Structure

The project is organized into `backend` (Python FastAPI) and `frontend` (React/Vite) components. This `README.md` focuses primarily on the backend.

```
project/
├── .gitignore
├── .vscode/                  # VS Code settings
├── README.md                 # This documentation file
├── frontend/                 # Frontend application (React/Vite)
│   ├── ...
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── src/                      # Backend source code
    ├── __init__.py
    ├── db.py                 # Database initialization and session management
    ├── models.py             # SQLAlchemy ORM models (User, Document, Conversation, ChatMessage)
    ├── routers/              # API endpoint definitions
    │   ├── __init__.py
    │   ├── auth.py           # Authentication routes (register, login)
    │   └── data_handler.py   # Document and chat handling routes
    └── utils/                # Utility functions
        ├── auth.py           # Password hashing, JWT token creation/decoding
        ├── llm_client.py     # LLM (Google Gemini) integration for querying and summarization
        └── pdf_processor.py  # PDF text extraction utility
```

## Installation

To set up the backend, follow these steps:

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd project
    ```

2.  **Create a Python virtual environment** (recommended):

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:

    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

This project uses environment variables for sensitive information and configuration. Create a `.env` file in the root directory of the project (e.g., `project/.env`).

### Required Environment Variables:

-   `GEMINI_API_KEY`: Your API key for Google Gemini. Obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).
-   `JWT_SECRET_KEY`: A strong, random secret key for JWT token signing. You can generate one using Python:
    ```python
    import os
    print(os.urandom(24).hex())
    ```

### Optional Environment Variables:

-   `MYSQL_DATABASE_URL`: If you want to use MySQL instead of the default SQLite, provide your MySQL connection string here (e.g., `mysql+mysqlconnector://user:password@host:port/database`).

Example `.env` file:

```
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
JWT_SECRET_KEY="YOUR_RANDOM_SECRET_KEY"
# MYSQL_DATABASE_URL="mysql+mysqlconnector://user:password@localhost:3306/your_database"
```

## Running the Application

After installation and configuration, you can run the FastAPI application:

```bash
python main.py
```

The application will run on `http://127.0.0.1:8001` by default. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8001/docs`.

## API Endpoints

The API provides the following main functionalities:

### Authentication (`/api/v1/auth`)

-   `POST /api/v1/auth/register`: Register a new user.
    -   **Request Body**: `{"username": "string", "password": "string"}`
    -   **Response**: `{"message": "User registered successfully"}`
-   `POST /api/v1/auth/login`: Log in an existing user and receive an access token.
    -   **Request Body**: `{"username": "string", "password": "string"}`
    -   **Response**: `{"access_token": "string", "token_type": "bearer"}`

### Document and Chat Handling (`/api/v1`)

*(All endpoints under `/api/v1` require a valid JWT `Bearer` token in the `Authorization` header.)*

-   `POST /api/v1/upload/{uuid}`: Upload a new PDF document.
    -   **Path Parameter**: `uuid` (UUID of the document)
    -   **Request Body**: `file` (PDF file)
    -   **Response**: `{"message": "PDF uploaded and text extracted successfully.", "uuid": "string"}`
-   `PUT /api/v1/update/{uuid}`: Update an existing PDF document.
    -   **Path Parameter**: `uuid` (UUID of the document to update)
    -   **Request Body**: `file` (New PDF file)
    -   **Response**: `{"message": "PDF updated and text extracted successfully.", "uuid": "string"}`
-   `GET /api/v1/query/{uuid}`: Query the content of a specific PDF document using an LLM.
    -   **Path Parameter**: `uuid` (UUID of the document)
    -   **Query Parameter**: `query` (The question to ask)
    -   **Response**: `{"uuid": "string", "query": "string", "llm_response": "string"}`
-   `DELETE /api/v1/delete/{uuid}`: Delete a PDF document.
    -   **Path Parameter**: `uuid` (UUID of the document to delete)
    -   **Response**: `{"message": "Data for UUID {uuid} deleted successfully."}`
-   `GET /api/v1/list_uuids`: List all uploaded PDF documents for the current user.
    -   **Response**: `{"pdfs": [{"uuid": "string", "filename": "string"}, ...]}`
-   `GET /api/v1/download/{uuid}`: Download a specific PDF document.
    -   **Path Parameter**: `uuid` (UUID of the document to download)
    -   **Response**: File download

### Chat Endpoints (`/api/v1/chat`)

-   `POST /api/v1/chat/start/{document_uuid}`: Start a new conversation with a document.
    -   **Path Parameter**: `document_uuid` (UUID of the document)
    -   **Request Body**: `{"message": "string"}` (Initial user message)
    -   **Response**: `ConversationResponse` object including initial messages.
-   `POST /api/v1/chat/continue/{conversation_uuid}`: Continue an existing conversation.
    -   **Path Parameter**: `conversation_uuid` (UUID of the conversation)
    -   **Request Body**: `{"message": "string"}` (New user message)
    -   **Response**: `ChatMessageResponse` object for the assistant's reply.
-   `GET /api/v1/chat/conversations`: Get a list of all active conversations for the current user.
    -   **Response**: List of conversation summaries.
-   `GET /api/v1/chat/conversation/{conversation_uuid}`: Get a specific conversation with all messages.
    -   **Path Parameter**: `conversation_uuid` (UUID of the conversation)
    -   **Response**: `ConversationResponse` object with full message history.
-   `DELETE /api/v1/chat/conversation/{conversation_uuid}`: Soft delete a conversation.
    -   **Path Parameter**: `conversation_uuid` (UUID of the conversation)
    -   **Response**: `{"message": "Conversation deleted successfully."}`

### Summarization Endpoints (`/api/v1/summarize`)

-   `POST /api/v1/summarize/{document_uuid}`: Generate a summary for a document.
    -   **Path Parameter**: `document_uuid` (UUID of the document)
    -   **Response**: `DocumentSummaryResponse` object with the generated summary.
-   `GET /api/v1/summary/{document_uuid}`: Get the existing summary for a document.
    -   **Path Parameter**: `document_uuid` (UUID of the document)
    -   **Response**: `DocumentSummaryResponse` object with the summary.

## Frontend

The `frontend/` directory contains a React application built with Vite. Refer to its `README.md` for specific instructions on setting up and running the frontend.

## Logging

Application logs are stored in the `logs/` directory, with a new log file generated weekly and retained for four weeks. The log level is set to `INFO`.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.