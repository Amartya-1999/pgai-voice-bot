# Pretty Good AI Voice Bot Challenge

This project is an automated Python voice bot built for the Pretty Good AI AI Engineering Challenge.

The bot places real outbound phone calls to the Pretty Good AI phone agent, simulates realistic patient conversations, records the calls, saves transcripts, and helps identify product and conversation-quality issues in the phone agent.

## Project Overview

The goal of this project is to test a healthcare phone agent across common patient workflows, including:

* Appointment scheduling
* Appointment rescheduling
* Appointment cancellation
* Medication refill requests
* Insurance acceptance questions
* Office-hours questions
* Clinic location and parking questions
* Demo patient identity verification
* Edge cases where the patient changes or clarifies intent

The system uses Twilio to place phone calls, FastAPI to serve webhook endpoints, TwiML to speak and listen during calls, and an LLM-backed response layer to generate patient replies.

## Tech Stack

* Python
* FastAPI
* Twilio Programmable Voice
* TwiML
* Groq LLM API
* Python dotenv
* Requests
* ngrok for local webhook tunneling

## Folder Structure

```text
pgai-voice-bot/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── call_state.py
│   ├── groq_client.py
│   ├── scenario_store.py
│   ├── rule_responder.py
│   ├── transcript_utils.py
│   └── recording_utils.py
├── data/
│   ├── scenarios.json
│   ├── call_log.md
│   ├── transcripts/
│   ├── recordings/
│   │   └── audio/
│   └── bug_reports/
│       └── bug_report.md
├── scripts/
│   ├── make_call.py
│   └── download_recordings.py
├── architecture.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pgai-voice-bot
```

### 2. Create a Virtual Environment

On Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Use `.env.example` as a reference:

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
TARGET_PHONE_NUMBER=+18054398008
PUBLIC_BASE_URL=your_ngrok_public_url
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=optional_if_used
```

Important: `.env` should never be committed to GitHub.

## Running the Application

### 1. Start the FastAPI Server

```powershell
uvicorn app.main:app --reload --port 8000
```

The local app will run at:

```text
http://127.0.0.1:8000
```

### 2. Start ngrok

In a separate terminal:

```powershell
.\ngrok.exe http 8000
```

Copy the ngrok forwarding URL and set it in `.env`:

```env
PUBLIC_BASE_URL=https://your-ngrok-url.ngrok-free.app
```

Then restart the FastAPI server.

### 3. Place a Test Call

Run one of the available scenarios:

```powershell
python -m scripts.make_call --scenario office_hours
```

Example scenarios:

```text
appointment_basic
med_refill
office_hours
insurance_question
location_question
reschedule_existing
weekend_appointment_edge
cancel_appointment
demo_profile_identity
unclear_patient_edge
```

## Available Scenarios

Scenarios are stored in:

```text
data/scenarios.json
```

Each scenario defines a patient goal, such as scheduling an appointment, asking about insurance, requesting a refill, or testing an edge case.

## Transcripts

Transcripts are saved automatically after each bot response.

Transcript folder:

```text
data/transcripts/
```

Example transcript filename:

```text
office_hours__CA589a4bd8db8a2bc4cc3b48c903802bbb.txt
```

Each transcript includes:

* Call SID
* Scenario ID
* Scenario title
* Timestamp
* Patient bot messages
* Pretty Good AI agent messages

## Recordings

Twilio recording metadata is saved in:

```text
data/recordings/
```

Actual downloaded audio files are saved in:

```text
data/recordings/audio/
```

To download completed recordings from Twilio metadata files:

```powershell
python -m scripts.download_recordings
```

The audio files are saved as `.mp3`.

## Final Call Log

The final call log is stored here:

```text
data/call_log.md
```

It lists the final calls used for evaluation, including:

* Scenario
* Call SID
* Transcript path
* Recording path
* Notes about what happened in the call

## Bug Report

The bug report is stored here:

```text
data/bug_reports/bug_report.md
```

The main findings include:

* Existing appointment/profile state interfering across calls
* DOB verification loops
* Insurance question not answered
* Reschedule workflow loop
* Cancellation workflow loop
* Patient name mutation during identity verification
* Unclear or malformed agent responses

## Design Notes

The bot uses a hybrid response approach:

1. A deterministic rule layer handles common prompts such as name, date of birth, phone number, insurance, and scenario-specific follow-ups.
2. An LLM fallback handles less predictable agent responses.
3. Transcripts are saved continuously so that partial calls are not lost.
4. Recording metadata is captured through Twilio recording callbacks.
5. A separate script downloads audio recordings from Twilio after calls complete.

## How to Reproduce

1. Start FastAPI.
2. Start ngrok.
3. Update `PUBLIC_BASE_URL` in `.env`.
4. Run a scenario:

```powershell
python -m scripts.make_call --scenario location_question
```

5. Wait for the call to complete.
6. Check transcript:

```powershell
dir data\transcripts
```

7. Check recording metadata:

```powershell
dir data\recordings
```

8. Download audio:

```powershell
python -m scripts.download_recordings
```

## Security Notes

This repository should not contain real API keys or secrets.

Before pushing to GitHub:

* Confirm `.env` is listed in `.gitignore`
* Do not commit Twilio, Groq, or OpenAI credentials
* Rotate any credentials that may have been exposed during development
* Keep only `.env.example` in the repository
