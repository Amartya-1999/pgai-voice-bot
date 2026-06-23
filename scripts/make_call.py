import argparse
from urllib.parse import urlencode

from twilio.rest import Client
from app.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    PUBLIC_BASE_URL,
    TARGET_PHONE_NUMBER,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scenario",
        default="appointment_basic",
        help="Scenario ID from data/scenarios.json",
    )

    args = parser.parse_args()

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    query_string = urlencode({"scenario_id": args.scenario})
    voice_url = f"{PUBLIC_BASE_URL}/voice/start?{query_string}"

    call = client.calls.create(
        to=TARGET_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url=voice_url,
        method="POST",
        record=True,
        recording_status_callback=f"{PUBLIC_BASE_URL}/recording/status",
        recording_status_callback_method="POST",
        time_limit=180,
    )

    print(f"Started call: {call.sid}")
    print(f"Scenario: {args.scenario}")
    print(f"Voice URL: {voice_url}")


if __name__ == "__main__":
    main()