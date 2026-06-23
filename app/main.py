from fastapi import FastAPI, Form, Request, Query
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.call_state import (
    create_call_state,
    get_call_state,
    add_to_transcript,
    add_to_history,
)
from app.groq_client import generate_patient_reply
from app.transcript_utils import save_transcript
from app.recording_utils import save_recording_metadata
from app.rule_responder import get_rule_based_reply
from app.scenario_store import get_scenario_by_id

app = FastAPI()


MAX_TURNS = 12


def save_current_transcript(call_sid: str, state: dict):
    """
    Saves the current transcript with scenario metadata.
    This prevents transcripts from being overwritten with Scenario ID: unknown.
    """

    save_transcript(
        call_sid,
        state["transcript"],
        scenario_id=state.get("scenario_id", "unknown"),
        scenario_title=state.get("scenario_title", ""),
    )


@app.get("/")
def home():
    return {"status": "PGAI voice bot server is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/voice/start")
async def voice_start(
    CallSid: str = Form(...),
    scenario_id: str = Query("appointment_basic"),
):
    """
    Twilio hits this endpoint when the call starts.
    """

    scenario_obj = get_scenario_by_id(scenario_id)
    scenario_text = scenario_obj["scenario"]

    create_call_state(
        call_sid=CallSid,
        scenario=scenario_text,
        scenario_id=scenario_obj["id"],
        scenario_title=scenario_obj.get("title", ""),
    )

    first_patient_message = "Hi, I would like some help today."

    add_to_transcript(CallSid, "patient_bot", first_patient_message)
    add_to_history(CallSid, "assistant", first_patient_message)

    state = get_call_state(CallSid)
    save_current_transcript(CallSid, state)

    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/voice/respond",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    gather.say(first_patient_message, voice="alice")
    response.append(gather)

    response.redirect("/voice/respond")

    return Response(content=str(response), media_type="application/xml")


@app.post("/voice/respond")
async def voice_respond(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(None),
):
    """
    Twilio hits this endpoint after it hears the other side speak.
    """

    state = get_call_state(CallSid)
    response = VoiceResponse()

    if state is None:
        response.say("Sorry, something went wrong. Goodbye.", voice="alice")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    if SpeechResult:
        add_to_transcript(CallSid, "pgai_agent", SpeechResult)
        add_to_history(CallSid, "user", SpeechResult)

    state["turn"] += 1

    if state["turn"] >= MAX_TURNS:
        closing_message = "Okay, thank you for your help. Goodbye."

        add_to_transcript(CallSid, "patient_bot", closing_message)
        add_to_history(CallSid, "assistant", closing_message)

        save_current_transcript(CallSid, state)

        response.say(closing_message, voice="alice")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    rule_reply = get_rule_based_reply(SpeechResult, state["scenario"])

    if rule_reply:
        next_patient_message = rule_reply
    else:
        next_patient_message = generate_patient_reply(
            conversation_history=state["history"],
            scenario=state["scenario"],
        )

    add_to_transcript(CallSid, "patient_bot", next_patient_message)
    add_to_history(CallSid, "assistant", next_patient_message)

    save_current_transcript(CallSid, state)

    if "goodbye" in next_patient_message.lower():
        response.say(next_patient_message, voice="alice")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    gather = Gather(
        input="speech",
        action="/voice/respond",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    gather.say(next_patient_message, voice="alice")
    response.append(gather)

    response.redirect("/voice/respond")

    return Response(content=str(response), media_type="application/xml")


@app.post("/recording/status")
async def recording_status(
    CallSid: str = Form(None),
    RecordingSid: str = Form(None),
    RecordingUrl: str = Form(None),
    RecordingStatus: str = Form(None),
):
    """
    Twilio calls this endpoint when the recording is ready.
    """

    print("Recording callback received")
    print("CallSid:", CallSid)
    print("RecordingSid:", RecordingSid)
    print("RecordingUrl:", RecordingUrl)
    print("RecordingStatus:", RecordingStatus)

    save_recording_metadata(
        call_sid=CallSid,
        recording_sid=RecordingSid,
        recording_url=RecordingUrl,
        recording_status=RecordingStatus,
    )

    state = get_call_state(CallSid)

    if state:
        save_current_transcript(CallSid, state)
        print("Final transcript saved from recording callback.")
    else:
        print("No call state found for this CallSid.")

    return {"status": "received"}