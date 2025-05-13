from fastapi import FastAPI, Request, Response
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/voice")
async def voice_response(request: Request):
    form = await request.form()
    user_input = form.get("SpeechResult", "Hello")

    # ChatGPT response
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a polite AI receptionist. Greet the caller and ask how you can help."},
            {"role": "user", "content": user_input}
        ]
    )
    reply = response.choices[0].message["content"]

    # TwiML response with voicemail recording
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{reply}</Say>
    <Pause length="1"/>
    <Say>If you'd like to leave a message, please do so after the beep.</Say>
    <Record maxLength="60" action="/recording" method="POST" />
    <Say>We didn't receive a recording. Goodbye!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.post("/recording")
async def handle_recording(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl")
    caller = form.get("From")

    print(f"New voicemail from {caller}: {recording_url}")

    # Simple acknowledgement TwiML
    return Response(content="""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Thank you. Your message has been recorded. Goodbye!</Say>
</Response>""", media_type="application/xml")
