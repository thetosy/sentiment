from utils import handler
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

def upload_file_to_gcs(file, filename, content_type):
    bucket = client.bucket(os.environ['GC_BUCKET'])
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=content_type)
    return blob

app = FastAPI(title='Conversation-Sentiment-Analysis-API')


@app.get("/")
def home():
    return RedirectResponse(url="/docs")


# This endpoint handles all the logic necessary for the object detection to work.
# It requires the desired model and the image in which to perform object detection.
@app.post("/get-sentiment")
async def sentiment(file: UploadFile = File(...)):
    try:
        filename = file.filename
        fileExtension = filename.split(".")[-1] in SUPPORTED_AUDIO_FILES
        if not fileExtension:
            raise HTTPException(status_code=415, detail="Unsupported file provided.")
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        blob = upload_file_to_gcs(file.file, filename, content_type)

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
            formatted_results = {
                "speaker_1": results['body']['speaker_0'][0]['sentiment_output'],
                "speaker_2": results['body']['speaker_1'][0]['sentiment_output']
            }
            return JSONResponse(
                status_code=200,
                content=formatted_results,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred while processing the file: {e}"})



