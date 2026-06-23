from pathlib import Path
from datetime import datetime
import re


TRANSCRIPT_DIR = Path("data/transcripts")
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(value: str) -> str:
    """
    Converts text into a safe filename.
    Example: 'Medication Refill!' -> 'medication_refill'
    """

    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")

    return value or "unknown"


def save_transcript(
    call_sid: str,
    transcript: list[dict],
    scenario_id: str = "unknown",
    scenario_title: str = "",
):
    """
    Saves the transcript of one call into a text file.

    Filename format:
    scenario_id__call_sid.txt
    """

    safe_scenario_id = safe_filename(scenario_id)

    file_path = TRANSCRIPT_DIR / f"{safe_scenario_id}__{call_sid}.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"Call SID: {call_sid}\n")
        file.write(f"Scenario ID: {scenario_id}\n")
        file.write(f"Scenario Title: {scenario_title}\n")
        file.write(f"Saved At: {datetime.now().isoformat()}\n")
        file.write("=" * 60 + "\n\n")

        for turn in transcript:
            speaker = turn.get("speaker", "unknown")
            text = turn.get("text", "")

            file.write(f"{speaker}:\n")
            file.write(f"{text}\n\n")

    print(f"Transcript saved to {file_path}")
    return file_path