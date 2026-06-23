from pathlib import Path
import re
import requests

from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN


RECORDINGS_DIR = Path("data/recordings")
AUDIO_DIR = RECORDINGS_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def extract_value(text: str, label: str) -> str | None:
    pattern = rf"^{label}:\s*(.+)$"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def main():
    print("Starting recording download script...")

    metadata_files = list(RECORDINGS_DIR.glob("*_recording.txt"))

    print(f"Found {len(metadata_files)} recording metadata files.")

    if not metadata_files:
        print("No recording metadata files found in data/recordings.")
        return

    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    for metadata_file in metadata_files:
        print("-" * 80)
        print(f"Reading metadata file: {metadata_file.name}")

        content = metadata_file.read_text(encoding="utf-8")

        call_sid = extract_value(content, "Call SID")
        recording_url = extract_value(content, "Recording URL")
        recording_status = extract_value(content, "Recording Status")

        print(f"Call SID: {call_sid}")
        print(f"Recording Status: {recording_status}")
        print(f"Recording URL found: {'yes' if recording_url else 'no'}")

        if not call_sid or not recording_url:
            print("Skipping: missing Call SID or Recording URL.")
            skipped_count += 1
            continue

        if recording_status and recording_status.lower() != "completed":
            print(f"Skipping: recording status is {recording_status}, not completed.")
            skipped_count += 1
            continue

        audio_url = recording_url + ".mp3"
        output_path = AUDIO_DIR / f"{call_sid}.mp3"

        if output_path.exists():
            print(f"Already downloaded: {output_path}")
            skipped_count += 1
            continue

        print(f"Downloading MP3 from Twilio for call {call_sid}...")

        try:
            response = requests.get(
                audio_url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=60,
            )

            if response.status_code == 200:
                output_path.write_bytes(response.content)
                print(f"Saved audio file: {output_path}")
                downloaded_count += 1
            else:
                print(f"Failed download. Status code: {response.status_code}")
                print(response.text[:300])
                failed_count += 1

        except Exception as error:
            print(f"Error downloading {call_sid}: {error}")
            failed_count += 1

    print("=" * 80)
    print("Download summary")
    print(f"Downloaded: {downloaded_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Failed: {failed_count}")
    print(f"Audio folder: {AUDIO_DIR}")


if __name__ == "__main__":
    main()