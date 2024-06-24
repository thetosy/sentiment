# Generating Insights from Conversation

This project utilizes the [DeepGram Transcribe API](https://developers.deepgram.com/docs/getting-started-with-pre-recorded-audio) and Google Cloud Platform (App Engine and Cloud Storage) for deployment.

The application is deployed as a RESTful API service using [FastAPI](https://fastapi.tiangolo.com) and can be interacted with through the Swagger UI. The application processes an audio file containing the conversation of at least two people and returns relevant information about the individuals and the discussion topics.

Click [here](https://anotherfastapi.uc.r.appspot.com) to use the application.

![screenshot.png](assets/screenshot.png)
<p style="text-align: center;">API documentation page</p>

![try_it.png](assets/try_it.jpeg)
<p style="text-align: center;">Click on try it out</p>

![choose_file.png](assets/choose_file.jpeg)
<p style="text-align: center;">Upload file</p>

![execute.png](assets/execute.png)
<p style="text-align: center;">Execute</p>

To upload a file:
1. Click on the drop-down arrow next to "POST".
2. Select "Try it out".
3. Click on "Choose file" to upload an audio file of a conversation between at least two people from your local computer.
4. Finally, click "Execute".

When the user uploads the file, it is stored in a Google Cloud bucket, which is subsequently accessed by DeepGram to retrieve the audio via its remote file transcribe API. The result is then processed to match a dialogue format such as:


```
speaker_0: Hi. Is this the Crystal Heights Hotel in Singapore? 
speaker_1: Yes, it is. Good afternoon. How may I assist you today? 
```

Using the OpenAI API and prompt engineering, relevant insights from the conversation are obtained using the GPT-4 model. These insights are then displayed to the user.

This API is scalable and flexible, making it usable on other platforms such as Postman or the requests library in application development. 









