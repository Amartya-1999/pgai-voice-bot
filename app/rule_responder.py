def get_goal_from_scenario(scenario_text: str) -> str:
    """
    Infers the broad scenario goal from the scenario text.
    """

    text = scenario_text.lower()

    if "refill" in text or "medication" in text:
        return "refill"

    if "office hours" in text or "weekends" in text:
        return "office_hours"

    if "insurance" in text and "schedule" not in text:
        return "insurance"

    if "address" in text or "parking" in text or "arrive early" in text:
        return "location"

    if "cancel" in text:
        return "cancel"

    if "reschedule" in text:
        return "reschedule"

    return "appointment"


def get_opening_goal_reply(scenario_text: str) -> str:
    """
    Returns a natural first goal statement based on the scenario.
    Used after the recording disclosure.
    """

    goal = get_goal_from_scenario(scenario_text)

    if goal == "refill":
        return "That's fine. I'm calling to request a medication refill."

    if goal == "office_hours":
        return "That's fine. I wanted to ask about your office hours this week."

    if goal == "insurance":
        return "That's fine. I wanted to ask if you accept Blue Cross Blue Shield insurance."

    if goal == "location":
        return "That's fine. I wanted to confirm your clinic address and parking information."

    if goal == "cancel":
        return "That's fine. I need to cancel an appointment."

    if goal == "reschedule":
        return "That's fine. I need to reschedule an appointment."

    return "That's fine. I'd like to schedule a routine checkup for next week."


def get_goal_statement(scenario_text: str) -> str:
    """
    Returns the main patient goal without acknowledging the recording disclosure.
    """

    goal = get_goal_from_scenario(scenario_text)

    if goal == "refill":
        return "I'm calling to request a medication refill."

    if goal == "office_hours":
        return "I wanted to ask what your office hours are this week."

    if goal == "insurance":
        return "I wanted to ask if you accept Blue Cross Blue Shield insurance."

    if goal == "location":
        return "I wanted to confirm the clinic address and parking information."

    if goal == "cancel":
        return "I need to cancel an appointment."

    if goal == "reschedule":
        return "I need to reschedule an appointment."

    return "I'd like to schedule a routine checkup for next week."


def _cancel_reply(reply: str, cancel_state: dict) -> str:
    """Remember the last cancellation reply so generic prompts cannot loop forever."""

    if reply != cancel_state.get("last_reply"):
        cancel_state["last_reply"] = reply
        return reply

    fallback_count = cancel_state.get("fallback_count", 0)
    fallbacks = (
        "Could you confirm which upcoming appointment you found so I can cancel the correct one?",
        "I'm unable to resolve the appointment date. Please connect me with a staff member who can help.",
        "Okay, I won't make any changes today. Thank you. Goodbye.",
    )
    reply = fallbacks[min(fallback_count, len(fallbacks) - 1)]
    cancel_state["fallback_count"] = fallback_count + 1
    cancel_state["last_reply"] = reply
    return reply


def get_cancel_reply(agent_text: str, rule_state: dict) -> str | None:
    """Advance the deterministic cancellation conversation."""

    text = agent_text.lower()
    cancel_state = rule_state.setdefault(
        "cancel",
        {
            "target_date": "tomorrow",
            "reason_given": False,
            "date_conflict_seen": False,
            "confirmed": False,
            "fee_asked": False,
            "reschedule_asked": False,
        },
    )

    # Finish follow-up questions after the cancellation itself is complete.
    if cancel_state["reschedule_asked"]:
        return _cancel_reply("Great, thank you for your help. Goodbye.", cancel_state)

    if cancel_state["fee_asked"] and ("fee" in text or "charge" in text):
        cancel_state["reschedule_asked"] = True
        return _cancel_reply(
            "Understood. Would I be able to call back and reschedule later?",
            cancel_state,
        )

    cancellation_complete = any(
        phrase in text
        for phrase in (
            "has been canceled",
            "has been cancelled",
            "is canceled",
            "is cancelled",
            "successfully canceled",
            "successfully cancelled",
            "cancellation is complete",
        )
    )
    if cancellation_complete:
        cancel_state["fee_asked"] = True
        return _cancel_reply("Thank you. Is there any cancellation fee?", cancel_state)

    asks_for_confirmation = any(
        phrase in text
        for phrase in (
            "confirm",
            "are you sure",
            "before i proceed",
            "want me to cancel",
            "would you like to cancel",
        )
    )

    # Reconcile the scenario's date with the appointment the receptionist found.
    today_conflict = (
        "today" in text
        and ("appointment" in text or "scheduled" in text)
        and not cancellation_complete
    )
    if today_conflict:
        if not cancel_state["date_conflict_seen"]:
            cancel_state["date_conflict_seen"] = True
            return _cancel_reply(
                "I may have the date wrong. Is the appointment with Kelly Noble the only upcoming appointment on my account?",
                cancel_state,
            )

        cancel_state["target_date"] = "today"
        cancel_state["reason_given"] = True
        if asks_for_confirmation:
            cancel_state["confirmed"] = True
            return _cancel_reply(
                "Yes, I confirm that I want to cancel today's appointment with Kelly Noble.",
                cancel_state,
            )
        return _cancel_reply(
            "Then yes, please cancel today's appointment with Kelly Noble. I have a work conflict.",
            cancel_state,
        )

    asks_for_reason = "reason" in text or "why" in text
    if asks_for_reason and ("cancel" in text or "appointment" in text):
        cancel_state["reason_given"] = True
        return _cancel_reply(
            "I have a work conflict, so I need to cancel it.",
            cancel_state,
        )

    if asks_for_confirmation:
        cancel_state["confirmed"] = True
        target = cancel_state["target_date"]
        return _cancel_reply(
            f"Yes, I confirm that I want to cancel the appointment for {target}.",
            cancel_state,
        )

    # If the appointment is found, volunteer the reason instead of restating only the goal.
    if "tomorrow" in text and ("appointment" in text or "scheduled" in text):
        cancel_state["reason_given"] = True
        return _cancel_reply(
            "Yes, that's the appointment. I have a work conflict, so I'd like to cancel it.",
            cancel_state,
        )

    if "reschedule" in text:
        return _cancel_reply(
            "Not right now. I just want to cancel it for now.",
            cancel_state,
        )

    # Keep this broad rule last. Include the reason so it still moves the flow forward.
    if "cancel" in text or "appointment" in text:
        cancel_state["reason_given"] = True
        return _cancel_reply(
            "I need to cancel my appointment for tomorrow because of a work conflict.",
            cancel_state,
        )

    return None


def get_rule_based_reply(
    agent_text: str,
    scenario_text: str,
    rule_state: dict | None = None,
) -> str | None:
    """
    Returns a deterministic patient reply for common receptionist prompts.
    If no rule matches, return None and let the LLM handle it.
    """

    if not agent_text:
        return None

    text = agent_text.lower()
    goal = get_goal_from_scenario(scenario_text)
    rule_state = rule_state if rule_state is not None else {}

    # Identity confirmation must happen before generic greeting.
    if (
        "am i speaking with kumar" in text
        or "am i speaking with kamar" in text
        or "speaking with kumar" in text
        or "speaking with kamar" in text
        or "is this kumar" in text
        or "is this kamar" in text
        or "with kumar" in text
        or "with kamar" in text
):
        return "Yes, this is Kumar."

    # Recording disclosure
    if "recorded" in text or "quality and training" in text:
        return get_opening_goal_reply(scenario_text)

    # General greeting / intro
    if (
        "how can i help" in text
        or "what can i help" in text
        or "thanks for calling" in text
        or "calling pivot point" in text
        or "pretty good ai" in text
    ):
        return get_goal_statement(scenario_text)

    # Demo patient profile
    if "create a demo patient" in text or "demo patient profile" in text:
        return "Yes, please create a demo patient profile."

    # Spelling prompts should be handled before DOB-only prompts.
    if "spell" in text:
        return "K-U-M-A-R, A-M-A-R-T-Y-A, and my date of birth is January 15th, 1998."

    # Name
    if "first and last name" in text or "what name" in text or "your name" in text:
        return "Kumar Amartya."

    # Date of birth
    if "date of birth" in text or "birth date" in text or "dob" in text or "birthday" in text:
        if "july" in text or "2000" in text:
            return "No, my date of birth is January 15th, 1998."
        return "January 15th, 1998."

    # Phone number
    if "phone number" in text or "full phone" in text or "area code" in text:
        if "229" in text or "6398" in text:
            return "Yes, that phone number is correct."
        return "229-800-6398."

    # Insurance
    if "insurance" in text:
        if "upload" in text or "text" in text or "link" in text or "card" in text:
            return "Yes, please text me the link."
        return "Blue Cross Blue Shield."

    # Refill-specific flow
    if goal == "refill":
        if "birthday doesn't match" in text or "demo purposes" in text:
            return "Okay, thanks. I am calling to request a refill for my blood pressure medication."

        if "medication" in text or "prescription" in text or "refill" in text:
            return "I need a refill for my blood pressure medication."

        if "pharmacy" in text:
            return "Please send it to my usual pharmacy."

        if "how many" in text or "days left" in text or "how much" in text:
            return "I have about three days left."

        if "support team" in text or "representative" in text or "operator" in text:
            return "If you can't process the refill, please have the clinic support team follow up with me."

    # Office-hours flow
    if goal == "office_hours":
        # If the agent already answered weekend availability, wrap up.
        if (
            "not open on weekends" in text
            or "closed on weekends" in text
            or "closed on both saturday and sunday" in text
            or "monday through friday only" in text
            or "closed on both saturday and sunday" in text
            or "closed on weekends" in text
        ):
            return "Okay, thank you for clarifying. Goodbye."

        # If the agent gave weekday hours, ask the weekend follow-up once.
        if (
            "9:00" in text
            or "9 a.m" in text
            or "4:00" in text
            or "monday" in text
            or "tuesday" in text
            or "wednesday" in text
            or "thursday" in text
            or "friday" in text
        ):
            return "Do you have any hours on weekends?"

        if "weekend" in text or "saturday" in text or "sunday" in text:
            return "Are you open on weekends?"

        if "hours" in text or "open" in text or "closed" in text:
            return "What are your office hours this week?"

    # Insurance question flow
    if goal == "insurance":
        if "accept" in text or "take" in text or "blue cross" in text:
            return "Great, do I need to bring my insurance card with me?"

        if "card" in text or "bring" in text:
            return "Okay, thank you. Goodbye."

    # Location / parking flow
    if goal == "location":
        if "parking" in text and ("available" in text or "yes" in text):
            return "Great, how early should I arrive before the appointment?"

        if "address" in text or "location" in text:
            return "Can you confirm the clinic address?"

        if "parking" in text:
            return "Is parking available at the clinic?"

        if "arrive" in text or "early" in text:
            return "Okay, thank you. Goodbye."

    # Cancel appointment flow
    if goal == "cancel":
        return get_cancel_reply(agent_text, rule_state)

    # Reschedule appointment flow
    if goal == "reschedule":
        if "is this the appointment" in text:
           return "Yes, please reschedule that appointment to next Tuesday morning if available."

        if "1 upcoming appointment" in text or "one upcoming appointment" in text:
           return "Yes, please reschedule that appointment to next Tuesday morning if available."

        if "you have an appointment scheduled" in text:
            return "Yes, please reschedule that appointment to next Tuesday morning if available."

        if "tuesday" in text and ("10:30" in text or "appointment" in text):
            return "Yes, please reschedule that appointment to next Tuesday morning if available."

        if "what day" in text or "what time" in text or "preferred time" in text:
            return "Next Tuesday morning, if available."

        if "confirm" in text or "does that work" in text or "would you like me to book" in text:
            return "Yes, that works for me."

        if "reschedule" in text or "appointment" in text:
            return "I need to reschedule my appointment to next Tuesday morning."

    # Location offer during appointment flow.
    # Do not challenge Nashville/Pivot Point during final runs; accept it.
    if "nashville" in text and (
        "book" in text or "appointment" in text or "openings" in text or "visit" in text
    ):
        return "Yes, that location works for me."

    # Existing appointment conflict
    if "already have" in text and ("appointment" in text or "office visit" in text):
        return "Okay, please help me reschedule that appointment to Wednesday morning at 9:00 AM."

    if "can't book a second" in text or "second one" in text:
        return "Okay, please help me reschedule the existing appointment to Wednesday morning at 9:00 AM."

    # General appointment scheduling
    if "what would you like to schedule" in text:
        return "A routine checkup."

    if "what type" in text and ("visit" in text or "appointment" in text):
        return "A routine checkup."

    if "office visit" in text and ("use" in text or "reason" in text):
        return "Yes, office visit is fine."

    if "morning or afternoon" in text:
        return "Morning, preferably Tuesday."

    if "what day" in text or "what time" in text or "preferred time" in text:
        return "Tuesday morning, if available."

    if "tuesday morning" in text and (
        "book" in text or "confirm" in text or "appointment" in text
    ):
        return "Yes, Tuesday morning works for me."

    if "wednesday morning" in text:
        return "Wednesday morning at 9:00 AM works for me."

    if "confirm" in text or "does that work" in text or "would you like me to book" in text:
        return "Yes, that works for me."

    # Transfer / support
    if "support team" in text or "representative" in text or "operator" in text:
        return "I'd prefer to continue with you if possible."

    return None
