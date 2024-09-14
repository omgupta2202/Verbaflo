import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
import aiofiles
import pdfplumber
import requests
import logging
import traceback

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Variable to store Gemini API key
GEMINI_API_KEY = None

# Serve the HTML form for entering the Gemini API key
@app.get("/")
async def get_key_form():
    html_content = """
    <html>
    <body style="font-family: Arial; text-align: center; background-color: #f7f7f7; padding-top: 50px;">
        <h2 style="color: #4CAF50;">Enter your Gemini API Key</h2>
        <form action="/set-key/" method="post" style="display: inline-block; padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 10px;">
            <input type="text" name="api_key" placeholder="Gemini API Key" required style="margin-bottom: 10px; width: 300px;">
            <br>
            <button type="submit" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Submit</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# Set the Gemini API key
@app.post("/set-key/")
async def set_api_key(api_key: str = Form(...)):
    global GEMINI_API_KEY
    GEMINI_API_KEY = api_key
    return HTMLResponse(content=f"API Key set successfully. <a href='/upload/'>Upload PDF Resume</a>", status_code=200)

# Serve the HTML form for uploading PDFs
@app.get("/upload/")
async def get_upload_form():
    if GEMINI_API_KEY is None:
        return HTMLResponse(content="API Key is not set. <a href='/'>Go back</a>", status_code=400)
    
    html_content = """
    <html>
    <body style="font-family: Arial; text-align: center; background-color: #f7f7f7; padding-top: 50px;">
        <h2 style="color: #4CAF50;">Upload your LinkedIn PDF Resume</h2>
        <form action="/upload-file/" method="post" enctype="multipart/form-data" style="display: inline-block; padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 10px;">
            <input type="file" name="file" accept=".pdf" required style="margin-bottom: 10px;">
            <br>
            <button type="submit" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Upload</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# Extract text from LinkedIn PDF
async def extract_text_from_pdf(pdf_path: str) -> str:
    text = ''
    temp_path = "temp_resume.pdf"
    
    try:
        async with aiofiles.open(pdf_path, 'rb') as pdf_file:
            async with aiofiles.open(temp_path, 'wb') as temp_file:
                content = await pdf_file.read()
                await temp_file.write(content)
        
        # Process the temporary file synchronously
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}\n{traceback.format_exc()}")
        raise

    return text

# Generate HTML resume using Gemini API
async def generate_html_resume(pdf_text: str) -> str:
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'contents': [
            {
                'parts': [
                    {
                        'text': f"Generate a professional HTML resume from this text:\n\n{pdf_text}. Don't include any text other than resume specific in response. Make in Jake's resume template."
                    }
                ]
            }
        ]
    }
    try:
        if GEMINI_API_KEY is None:
            raise ValueError("Gemini API key is not set.")

        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent',
            headers=headers,
            json=payload,
            params={'key': GEMINI_API_KEY}
        )
        response.raise_for_status()  # Raise an error for bad responses
        result = response.json()

        # Extract the text from the response
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0]:
                parts = result['candidates'][0]['content']['parts']
                if len(parts) > 0:
                    return parts[0]['text']
                else:
                    raise ValueError("No 'parts' found in 'content'.")
            else:
                raise ValueError("Response does not contain 'content' key.")
        else:
            raise ValueError("Response does not contain 'candidates' key.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating HTML resume: {str(e)}\n{traceback.format_exc()}")
        raise

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    if GEMINI_API_KEY is None:
        return HTMLResponse(content="API Key is not set. <a href='/'>Go back</a>", status_code=400)

    pdf_path = f"uploaded_resume_{file.filename}"
    html_path = f"resume_{file.filename.rsplit('.', 1)[0]}.html"

    try:
        # Save the uploaded PDF file
        async with aiofiles.open(pdf_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Extract text from the PDF
        pdf_text = await extract_text_from_pdf(pdf_path)

        # Generate HTML from the extracted text
        html_resume = await generate_html_resume(pdf_text)

        # Save the generated HTML resume
        async with aiofiles.open(html_path, 'w') as f:
            await f.write(html_resume)

        # Return the HTML file as a downloadable response
        return FileResponse(html_path, media_type='application/octet-stream', filename=html_path)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}\n{traceback.format_exc()}")
        return HTMLResponse(content=f"An error occurred: {str(e)}", status_code=500)
