# HTML Resume Generator

## For demo purpose use my Gemini Api Key: 'AIzaSyDpH1VM0-6GbRP6J1R4vhHmkoUxKouCVvA'

## Project Overview

This project involves creating a web application that generates an HTML resume from a LinkedIn PDF using APIs. Due to limitations with API credits, the application uses the Gemini API from Google for content generation. The OpenAI API implementation is also included but not used in the final version.

## Approach

### Gemini API Implementation

Since I did not have access to OpenAI API credits, I utilized the Google Gemini API, which is free. The code for using the Gemini API is included in `main.py`. The Gemini API generates the HTML resume based on the text extracted from the PDF.

### OpenAI API Implementation

The OpenAI API implementation is included in `main2.py`. However, due to a lack of credits, this implementation was not used in the final version. The code for OpenAI is provided for reference and can be activated if you have access to OpenAI credits.

### Project Development

I had prior experience with the OpenAI API, which was useful for understanding how to interact with AI models. For extracting text from PDFs, I used resources on Stack Overflow to solve module-related issues such as pdf to text extractor. I used Gemini, OpenAI documentation. I also used Postman to understand the response format of the Gemini API.

### Project is deployed in AWS

### Note

- **Gemini API**: Deployed and functioning as expected. The code for interacting with Gemini API is in `main.py`.
- **OpenAI API**: The code is available in `main2.py`. Due to insufficient credits, this was not used in the final deployment but can be activated with the appropriate API key.

## Setup

1. **Install Dependencies**: 
   - Install dependencies using:
     ```bash
     pip install -r requirements.txt
     ```

2. **Run the Application**:
   - Start the FastAPI application:
     ```bash
     uvicorn main:app --reload
     ```

   - For the OpenAI version:
     ```bash
     uvicorn main2:app --reload
     ```

3. **Access the Application**:
   - Open your web browser and navigate to `http://127.0.0.1:8000` to access the web interface.


### Use-

## Step1: Enter your API key and hit enter
![Gemini API Example](img/1.png)

## Step2: Click on Upload PDF Resume
![Gemini API Example](img/2.png)

## Step3: Upload resume and hit upload
![Gemini API Example](img/3.png)

## Step4: Wait for 5-7 seconds the html resume will be downloaded.

### Sample Files

- **Sample PDF**: [sample.pdf](sample.pdf)
- **Sample HTML Resume**: [sample.html](sample.html)