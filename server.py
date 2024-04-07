from utils import handler, upload_file_to_gcs, format_results
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv, find_dotenv
from google.cloud import storage
import mimetypes
import uvicorn
import shutil
import os
import json

SUPPORTED_AUDIO_FILES = ['mp3', 'mp4', 'mp2', 'aac', 'wav', 'flac', 'pcm', 'm4a', 'ogg', 'opus', 'webm']
_ = load_dotenv(find_dotenv())

client = storage.Client()
app = FastAPI(title='Insight-API')

# By using @app.get("/") you are allowing the GET method to work for the / endpoint.
@app.get("/")
def home():
    return RedirectResponse(url="/docs")


# This endpoint handles all the logic necessary for the object detection to work.
# It requires the desired model and the image in which to perform object detection.
@app.post("/get_insight")
async def insight(file: UploadFile = File(...)):
    try:
        filename = file.filename
        fileExtension = filename.split(".")[-1] in SUPPORTED_AUDIO_FILES
        if not fileExtension:
            raise HTTPException(status_code=415, detail="Unsupported file provided.")
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        blob = upload_file_to_gcs(client, file.file, filename, content_type)

        # read from google cloud storage
        file_path = os.environ['PUBLIC_URL']+"/"+filename
        print(file_path)
        results = handler(file_path)
        #print(results)
        if results['statusCode'] != 200:
            return JSONResponse(
                status_code=results['statusCode'],
                content=json.dumps(results['body']),
            )
        if results['statusCode'] == 200:
            formatted_results = format_results(results['body']['num_speakers'], results)
            return JSONResponse(
                status_code=200,
                content=formatted_results,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred while processing the file: {e}"})



