from utils import handler
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn
import shutil
import os
import json

SUPPORTED_AUDIO_FILES = ['mp3', 'mp4', 'mp2', 'aac', 'wav', 'flac', 'pcm', 'm4a', 'ogg', 'opus', 'webm']

UPLOAD_DIR = './uploaded_files'

dir_name = UPLOAD_DIR
if not os.path.exists(dir_name):
    os.mkdir(dir_name)

app = FastAPI(title='Conversation-Sentiment-Analysis-API')

# By using @app.get("/") you are allowing the GET method to work for the / endpoint.
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
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as audio_file:
            shutil.copyfileobj(file.file, audio_file)

        print('here-1')
        results = handler(file_path)
        print('here-2')
        formatted_results = {
            "speaker_1": results['body']['speaker_0'][0]['sentiment_output'], 
            "speaker_2": results['body']['speaker_1'][0]['sentiment_output']
        }
        print('here-3')
        if results['statusCode'] == 200:
            return JSONResponse(
                status_code=200,
                content=formatted_results,
            )
        else:
            return JSONResponse(
                status_code=results['statusCode'],
                content=json.dumps(results['body']),
            ) 
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An error occurred while processing the file: {e}"}) 



if __name__ == "__main__":
    uvicorn.run(app, host = "127.0.0.1", port=8000)