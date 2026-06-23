from pathlib import Path
from datetime import datetime


RECORDING_DIR = Path("data/recordings")
RECORDING_DIR.mkdir(parents=True, exist_ok=True)


def save_recording_metadata(
    call_sid: str,
    recording_sid: str | None,
    recording_url: str | None,
    recording_status: str | None,
):
    """
    Saves Twilio recording metadata for one call.
    This does not download the audio yet.
    It stores the recording URL and status so we can retrieve it later.
    """

    file_path = RECORDING_DIR / f"{call_sid}_recording.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"Call SID: {call_sid}\n")
        file.write(f"Saved At: {datetime.now().isoformat()}\n")
        file.write(f"Recording SID: {recording_sid}\n")
        file.write(f"Recording Status: {recording_status}\n")
        file.write(f"Recording URL: {recording_url}\n")

    print(f"Recording metadata saved to {file_path}")
    return file_path