CALLS = {}


def create_call_state(
    call_sid: str,
    scenario: str,
    scenario_id: str = "unknown",
    scenario_title: str = "",
):
    CALLS[call_sid] = {
        "scenario": scenario,
        "scenario_id": scenario_id,
        "scenario_title": scenario_title,
        "turn": 0,
        "history": [],
        "transcript": [],
    }


def get_call_state(call_sid: str):
    return CALLS.get(call_sid)


def add_to_transcript(call_sid: str, speaker: str, text: str):
    if not text:
        return

    CALLS[call_sid]["transcript"].append(
        {
            "speaker": speaker,
            "text": text,
        }
    )


def add_to_history(call_sid: str, role: str, text: str):
    if not text:
        return

    CALLS[call_sid]["history"].append(
        {
            "role": role,
            "content": text,
        }
    )