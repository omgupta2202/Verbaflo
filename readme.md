# PDF to HTML Resume Generator

This FastAPI application allows users to upload a LinkedIn PDF resume, extract its text, and generate a professional HTML resume using either the Gemini API or the OpenAI API. The application then provides the generated HTML resume as a downloadable file.

## Features

- Upload PDF resumes
- Extract text from PDF files
- Generate HTML resumes from extracted text
- Download the generated HTML resume

## Technologies

- **FastAPI**: Framework for building APIs
- **pdfplumber**: Library for extracting text from PDF files
- **requests**: Library for making HTTP requests (for Gemini API)
- **openai**: OpenAI API client library (for OpenAI API)
- **aiofiles**: Asynchronous file operations

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install fastapi uvicorn pdfplumber requests openai aiofiles python-multipart
    ```

4. Set up your API keys:

    - For Gemini API, replace `GEMINI_API_KEY` in the code with your actual API key.
    - For OpenAI API, replace `OPENAI_API_KEY` in the code with your actual API key.

## Running the Application

1. Start the FastAPI server:

    ```bash
    uvicorn main:app --reload
    ```

2. Open your web browser and go to `http://127.0.0.1:8000` to access the upload form.

## API Endpoints
- `POST /upload/`: Handles PDF upload, processes the file, generates HTML resume, and provides a download link for the HTML file.

## Example Usage

1. Navigate to `http://127.0.0.1:8000` in your browser.
2. Upload a LinkedIn PDF resume.
3. The application extracts the text, generates an HTML resume, and provides a downloadable HTML file.
