import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import io
import pdfplumber
import requests
import logging
import traceback

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory store for API key
api_key_store = {}

# Serve the form for entering the API key
@app.get("/api_key/")
async def get_api_key_form():
    html_content = """
    <html>
    <body style="font-family: Arial; text-align: center; background-color: #f7f7f7; padding-top: 50px;">
        <h2 style="color: #4CAF50;">Enter Your OpenAI API Key</h2>
        <form action="/set_api_key/" method="post" style="display: inline-block; padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 10px;">
            <input type="text" name="api_key" required style="margin-bottom: 10px; width: 300px;">
            <br>
            <button type="submit" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Set API Key</button>
        </form>
    </body>
</html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# Set the API key
@app.post("/set_api_key/")
async def set_api_key(api_key: str = Form(...)):
    api_key_store['key'] = api_key
    return HTMLResponse(content=f"API Key set. <a href='/'>Go to Upload Form</a>", status_code=200)

# Serve the HTML form for uploading PDFs
@app.get("/")
async def get_upload_form():
    if 'key' not in api_key_store:
        return HTMLResponse(content="API Key is not set. <a href='/api_key/'>Set OpenAI API Key</a>", status_code=400)

    html_content = """
    <html>
    <body style="font-family: Arial; text-align: center; background-color: #f7f7f7; padding-top: 50px;">
        <h2 style="color: #4CAF50;">Upload your LinkedIn PDF Resume</h2>
        <form action="/upload/" method="post" enctype="multipart/form-data" style="display: inline-block; padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 10px;">
            <input type="file" name="file" accept=".pdf" required style="margin-bottom: 10px;">
            <br>
            <button type="submit" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Upload</button>
        </form>
    </body>
</html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# Extract text from LinkedIn PDF
async def extract_text_from_pdf(file: UploadFile) -> str:
    text = ''
    try:
        # Read the file in memory
        file_content = await file.read()
        with io.BytesIO(file_content) as pdf_file:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}\n{traceback.format_exc()}")
        raise

    return text

# Generate HTML resume using OpenAI API
async def generate_html_resume(pdf_text: str) -> str:
    headers = {
        'Authorization': f'Bearer {api_key_store.get("key")}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'text-davinci-003',
        'prompt': f"Generate a professional HTML resume from this text:\n\n{pdf_text}. Don't include any text other than resume specific in response. Make in Jake's resume template.",
        'max_tokens': 1500
    }
    try:
        api_key = api_key_store.get('key')
        if not api_key:
            raise ValueError("API Key not set")

        response = requests.post(
            'https://api.openai.com/v1/completions',
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # Raise an error for bad responses
        result = response.json()

        # Extract the text from the response
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['text'].strip()
        else:
            raise ValueError("Response does not contain 'choices' key.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating HTML resume: {str(e)}\n{traceback.format_exc()}")
        raise

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        if 'key' not in api_key_store:
            raise HTTPException(status_code=400, detail="API Key is not set")

        # Extract text from the PDF
        pdf_text = await extract_text_from_pdf(file)

        # Generate HTML from the extracted text
        html_resume = await generate_html_resume(pdf_text)

        # Return the HTML as a downloadable response
        return StreamingResponse(io.StringIO(html_resume), media_type='text/html', headers={"Content-Disposition": "attachment; filename=resume.html"})

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}\n{traceback.format_exc()}")
        return HTMLResponse(content=f"An error occurred: {str(e)}", status_code=500)
