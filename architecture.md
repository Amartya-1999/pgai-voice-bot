# Architecture Document

## 1. Objective

The objective of this project is to build an automated voice bot that can call the Pretty Good AI phone agent, simulate realistic patient conversations, collect transcripts and recordings, and identify bugs or quality issues in the agent's behavior.

The system is designed to run repeatable scenario-based calls across common healthcare front-desk workflows.

## 2. High-Level Architecture

```text
User runs scenario
        |
        v
scripts/make_call.py
        |
        v
Twilio outbound call
        |
        v
Pretty Good AI phone agent
        |
        v
Twilio Voice webhook
        |
        v
FastAPI app
        |
        v
Rule responder + LLM fallback
        |
        v
TwiML response back to Twilio
        |
        v
Bot speaks next patient response
```

## 3. Main Components

## 3.1 Twilio Programmable Voice

Twilio is responsible for:

* Placing outbound calls
* Connecting the bot to the Pretty Good AI phone number
* Speaking bot responses using TwiML `<Say>`
* Listening to the phone agent using TwiML `<Gather input="speech">`
* Sending recognized speech back to the FastAPI webhook
* Recording calls
* Sending recording status callbacks

The outbound call is started from:

```text
scripts/make_call.py
```

## 3.2 FastAPI Web Server

The FastAPI app is the webhook server that controls the bot.

Main file:

```text
app/main.py
```

Important endpoints:

```text
POST /voice/start
POST /voice/respond
POST /recording/status
GET /health
```

### `/voice/start`

This endpoint is called when Twilio starts the call.

Responsibilities:

* Load the selected scenario
* Create call state
* Save scenario metadata
* Send the first patient message
* Start listening for the Pretty Good AI agent

### `/voice/respond`

This endpoint is called after Twilio hears speech from the Pretty Good AI agent.

Responsibilities:

* Receive the agent's speech transcript
* Add the agent message to conversation history
* Generate the next patient response
* Save the updated transcript
* Return TwiML instructions to speak the next response
* End the call if the bot says goodbye or reaches the turn limit

### `/recording/status`

This endpoint is called by Twilio when the call recording is completed.

Responsibilities:

* Save recording metadata
* Store the recording URL
* Save the final transcript again if call state is available

## 3.3 Scenario Store

Scenarios are stored in:

```text
data/scenarios.json
```

Each scenario contains:

* Scenario ID
* Scenario type
* Scenario title
* Patient behavior instructions

Example scenario types:

* Appointment scheduling
* Medication refill
* Insurance question
* Office-hours question
* Location and parking
* Rescheduling
* Cancellation
* Identity verification
* Edge-case behavior

The scenario store is loaded through:

```text
app/scenario_store.py
```

## 3.4 Call State

Call state is stored in memory during each active call.

File:

```text
app/call_state.py
```

Each call state includes:

* Call SID
* Scenario text
* Scenario ID
* Scenario title
* Turn count
* Conversation history
* Transcript entries

The call state allows the bot to remember what has happened so far in the current call.

## 3.5 Response Generation

The bot uses a hybrid response system.

File:

```text
app/rule_responder.py
```

File:

```text
app/groq_client.py
```

## Rule-Based Layer

The rule-based layer handles common and high-confidence receptionist prompts.

Examples:

* Recording disclosure
* Name confirmation
* Date of birth
* Phone number
* Insurance
* Appointment type
* Preferred date and time
* Refill request
* Parking follow-up
* Office-hours follow-up
* Reschedule confirmation
* Cancellation request

This layer was added because live phone conversations need short, stable, predictable replies. Deterministic rules help prevent the LLM from over-answering, changing identity details, or drifting away from the scenario.

## LLM Fallback Layer

If no rule matches the agent's message, the bot uses an LLM fallback through Groq.

The LLM is instructed to behave as a realistic patient, not as an assistant or developer. It receives the scenario and conversation history, then produces a short patient-style response.

This fallback helps handle unexpected agent phrasing while keeping the main workflow controlled by rules.

## 3.6 Transcript Saving

Transcript saving is handled by:

```text
app/transcript_utils.py
```

Transcripts are saved in:

```text
data/transcripts/
```

Filename format:

```text
scenario_id__call_sid.txt
```

Example:

```text
location_question__CAcc6ecc36b2802b333d93d2743e5930ae.txt
```

Transcripts are saved after every bot response so that progress is not lost if the call ends unexpectedly.

Each transcript includes:

* Call SID
* Scenario ID
* Scenario title
* Save timestamp
* Patient bot turns
* Pretty Good AI agent turns

## 3.7 Recording Metadata and Audio

Recording metadata is handled by:

```text
app/recording_utils.py
```

Metadata files are stored in:

```text
data/recordings/
```

Audio recordings are downloaded using:

```text
scripts/download_recordings.py
```

Downloaded audio files are stored in:

```text
data/recordings/audio/
```

The download script reads each Twilio recording metadata file, extracts the recording URL, authenticates with Twilio credentials, and downloads the audio as `.mp3`.

## 4. Call Flow

## Step 1: Start Local Server

```powershell
uvicorn app.main:app --reload --port 8000
```

## Step 2: Start ngrok

```powershell
.\ngrok.exe http 8000
```

## Step 3: Run Scenario

```powershell
python -m scripts.make_call --scenario office_hours
```

## Step 4: Twilio Places Call

Twilio calls the target Pretty Good AI phone number and uses the FastAPI webhook URL to control what the bot says.

## Step 5: Bot Speaks

FastAPI returns TwiML with a `<Say>` command and a `<Gather>` block.

## Step 6: Agent Responds

The Pretty Good AI phone agent speaks. Twilio transcribes the speech and sends it to `/voice/respond`.

## Step 7: Bot Generates Next Reply

The FastAPI app:

1. Adds the agent message to the transcript
2. Checks deterministic rules
3. Falls back to the LLM if needed
4. Saves the transcript
5. Sends the next TwiML response

## Step 8: Call Ends

The call ends when:

* The bot says goodbye
* The maximum turn count is reached
* The remote agent ends the call

## 5. Design Decisions

## 5.1 Why Use Twilio?

Twilio provides a practical way to make real phone calls, use speech input, speak responses, and capture recordings. It allowed the bot to test the Pretty Good AI agent through the same interface a real patient would use: a phone call.

## 5.2 Why Use FastAPI?

FastAPI is lightweight, quick to develop with, and works well for webhook-based applications. It also provides automatic API docs and simple request handling.

## 5.3 Why Use Rules Plus an LLM?

A pure LLM bot can drift, repeat itself, or give inconsistent identity details. A pure rule-based bot can fail when the agent says something unexpected.

The hybrid approach balances both:

* Rules provide stability for known healthcare prompts.
* The LLM provides flexibility for unexpected turns.

## 5.4 Why Save Transcripts Continuously?

Phone calls can end unexpectedly. Saving after every bot response protects against data loss and makes debugging easier.

## 5.5 Why Store Scenario Metadata in Filenames?

Scenario-based filenames make it easier to review final results.

Example:

```text
insurance_question__CAa7ce7d48fdd4f2718890c05317758b29.txt
```

This is easier to understand than a filename containing only the Call SID.

## 6. Limitations

## 6.1 In-Memory State

The current implementation stores call state in memory. This is acceptable for local testing, but a production version should use persistent storage such as Redis or a database.

## 6.2 Speech Recognition Errors

Some names and phrases were transcribed incorrectly, such as "Kumar" becoming "Kamar" or "Amartya" becoming "Marcia." The bot includes some rule handling for these errors, but this remains a limitation of live voice testing.

## 6.3 Scenario State Interference

Some Pretty Good AI agent responses appeared to reference previous appointment or profile state associated with the caller ID. This became one of the main bugs discovered during testing.

## 6.4 Local ngrok Dependency

The current webhook setup depends on ngrok. If the ngrok URL changes, the `.env` file must be updated and the FastAPI server restarted.

## 7. Testing Performed

The bot was used to run at least 10 real call scenarios. For each final call, the project includes:

* Transcript file
* Audio recording
* Scenario label
* Call SID
* Notes in `data/call_log.md`

The main bug findings are documented in:

```text
data/bug_reports/bug_report.md
```

## 8. Future Improvements

Potential improvements include:

* Store call state in Redis or a database
* Add automated transcript quality scoring
* Add scenario success/failure classification
* Add automatic bug extraction from transcripts
* Add better handling for repeated verification prompts
* Add configurable patient profiles per scenario
* Add support for multiple voice providers
* Build a small dashboard for call results
