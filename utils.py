import openai
import os
from dotenv import load_dotenv, find_dotenv
from jinja2 import Template
import json
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
_ = load_dotenv(find_dotenv())


def transcribe(file):
    deepgram = DeepgramClient(os.environ['DEEPGRAM_API_KEY'])

    with open(file, "rb") as file:
        buffer_data = file.read()

    payload: FileSource = {
        "buffer": buffer_data,
    }

    options = PrerecordedOptions(
        model="nova-2",
        smart_format=True,
        diarize=True,
        punctuate=True, 
        )

    response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

    return response


def extract_transcript(file_content):

    output_text = ""
    current_speaker = None

    words = file_content['results']['channels'][0]['alternatives'][0]['words']

    # Iterate through the content word by word:
    for word in words:
        speaker_label = word['speaker']
        content = word['punctuated_word']
        
        # Start the line with the speaker label:
        if speaker_label is not None and speaker_label != current_speaker:
            current_speaker = speaker_label
            output_text += f"\nspeaker_{current_speaker}: "
        
        output_text += f"{content} "
        
    return output_text


def get_sentimental_result(output):
    if openai.api_key is not os.environ['OPENAI_API_KEY']:
        openai.api_key = os.environ['OPENAI_API_KEY']

    client = openai.OpenAI()

    with open('prompt_template.txt', "r") as file:
        template_string = file.read()

    data = {
    'transcript': output,
    }
    
    template = Template(template_string)
    prompt = template.render(data)

    sentiment_response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    return json.loads(sentiment_response.choices[0].message.content)


def handler(file):
    try:
        transcript = transcribe(file)
        transcript = extract_transcript(transcript)
        result = get_sentimental_result(transcript)
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error occurred: {e}")
        }
    return {
        'statusCode': 200,
        'body': result
    }

