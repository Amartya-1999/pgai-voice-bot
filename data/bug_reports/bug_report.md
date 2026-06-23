# Bug Report

This document summarizes the main product and conversation-quality issues found while testing the Pretty Good AI phone agent using the automated voice-bot caller.

The tests covered appointment scheduling, medication refill, office-hours questions, insurance questions, location/parking questions, rescheduling, cancellation, demo identity verification, and unclear patient behavior.

---

## Summary of Key Findings

| # | Issue                                                          | Severity | Example Call                         |
| - | -------------------------------------------------------------- | -------- | ------------------------------------ |
| 1 | Agent retained existing appointment/profile state across calls | High     | `CAc44f7742cd747b8a67bf8c54d8ccbbba` |
| 2 | Medication refill flow blocked by DOB verification loop        | High     | `CAd69ce2fcf700ccee265ee680dd542ee3` |
| 3 | Insurance question not answered                                | High     | `CAa7ce7d48fdd4f2718890c05317758b29` |
| 4 | Reschedule flow looped after finding existing appointment      | High     | `CAdf97e70a5b42563b7586709b8eaa5237` |
| 5 | Cancellation flow looped after patient gave reason             | Medium   | `CA289d0bff36cc1f09da5ce0c53f12ac3b` |
| 6 | Patient name was misrecognized and mutated                     | Medium   | `CA4eef08d8bf44055036e5e9b0410e5324` |
| 7 | Agent gave unclear or malformed responses                      | Medium   | `CAcc6ecc36b2802b333d93d2743e5930ae` |

---

# Bug 1: Agent Retains Existing Appointment/Profile State Across Calls

**Severity:** High
**Scenario:** `weekend_appointment_edge`
**Call SID:** `CAc44f7742cd747b8a67bf8c54d8ccbbba`

## What Happened

The patient attempted to schedule a routine checkup and ask about availability. Instead of continuing with a new scheduling flow, the agent said the patient already had a routine checkup appointment booked.

The agent then said it could help reschedule or cancel the existing appointment, but it could not book another appointment of the same type.

## Evidence

The agent said:

> It looks like you already have a routine checkup appointment booked, I can help you reschedule or cancel your current appointment but I can't book another one of the same types.

## Expected Behavior

The agent should either:

1. Clearly explain that an existing appointment already exists and ask whether the patient wants to reschedule it, or
2. Treat the call as a fresh demo interaction if the system is in demo mode.

The agent should not let stale state from previous calls interfere with unrelated test scenarios.

## Impact

This blocks core appointment scheduling flows and makes repeated testing difficult. It also creates a poor patient experience because the patient may not understand why the agent is referencing an appointment they did not mention in the current call.

---

# Bug 2: Medication Refill Flow Blocked by DOB Verification Loop

**Severity:** High
**Scenario:** `med_refill`
**Call SID:** `CAd69ce2fcf700ccee265ee680dd542ee3`

## What Happened

The patient called to request a medication refill. The agent asked for date of birth. The patient provided the DOB multiple times.

The agent repeatedly responded that the birthday did not match the records but would be accepted for demo purposes. However, the agent did not smoothly continue to the medication refill workflow.

## Evidence

The agent said:

> The birthday doesn't match our records, but for demo purposes, I'll accept it.

The bot then repeated:

> January 15th, 1998.

This repeated instead of progressing to the refill request.

## Expected Behavior

Once the agent says the DOB is accepted for demo purposes, it should move forward and ask about the medication refill.

For example:

> Thanks. Which medication do you need refilled?

## Impact

Medication refill is a high-value healthcare workflow. A verification loop prevents the patient from completing the task and increases frustration.

---

# Bug 3: Insurance Question Not Answered

**Severity:** High
**Scenario:** `insurance_question`
**Call SID:** `CAa7ce7d48fdd4f2718890c05317758b29`

## What Happened

The patient asked whether the clinic accepts Blue Cross Blue Shield insurance. Instead of answering the insurance question, the agent moved into identity verification, name spelling, phone-number lookup, and DOB clarification.

The call ended without the insurance question being answered.

## Evidence

The patient asked:

> I wanted to ask if you accept Blue Cross Blue Shield insurance.

The agent later moved into identity verification:

> Please provide your date of birth.

Then:

> Would you like to use your phone number to look up your record...

The insurance question was never answered.

## Expected Behavior

For a general insurance acceptance question, the agent should answer directly if the information is available.

For example:

> We accept many Blue Cross Blue Shield plans, but coverage can vary. Please bring your insurance card or contact the office to confirm your specific plan.

## Impact

A patient asking a basic insurance question should not need to complete a long identity-verification loop unless the question requires account-specific coverage details.

---

# Bug 4: Reschedule Flow Looped After Existing Appointment Was Found

**Severity:** High
**Scenario:** `reschedule_existing`
**Call SID:** `CAdf97e70a5b42563b7586709b8eaa5237`

## What Happened

The patient asked to reschedule an appointment. The agent found an existing appointment but did not complete the rescheduling process.

The conversation looped around whether the patient wanted to reschedule, and the agent did not clearly offer or confirm a new appointment time.

## Evidence

The agent said:

> You have an appointment scheduled for Tuesday, June 23rd at 10:30 a.m.

The patient replied:

> I need to reschedule my Friday afternoon appointment to next Tuesday morning.

The agent continued with fragmented or repetitive responses instead of completing the reschedule.

## Expected Behavior

After finding an existing appointment, the agent should confirm:

1. Whether this is the appointment the patient wants to reschedule.
2. The new preferred date and time.
3. Whether that new slot is available.
4. Final confirmation or transfer if rescheduling cannot be completed.

## Impact

Rescheduling is a core patient workflow. If the agent can identify the appointment but cannot guide the patient to completion, the workflow is incomplete.

---

# Bug 5: Cancellation Flow Looped After Patient Gave Reason

**Severity:** Medium
**Scenario:** `cancel_appointment`
**Call SID:** `CA289d0bff36cc1f09da5ce0c53f12ac3b`

## What Happened

The patient called to cancel an appointment. The agent found the appointment and asked for a cancellation reason. The patient gave a reason, but the agent continued asking for the reason multiple times.

## Evidence

The patient said:

> I have a work conflict tomorrow, so I'd like to cancel that appointment.

The agent later asked again:

> Can you tell me the reason for canceling your appointment?

This happened multiple times.

## Expected Behavior

Once the patient gives a reason, the agent should accept it and proceed to cancellation confirmation.

For example:

> Got it. I’ll cancel the appointment because of a work conflict. Please confirm you want to cancel.

## Impact

The loop prevents task completion and makes the agent feel unresponsive.

---

# Bug 6: Patient Name Misrecognized and Mutated During Identity Verification

**Severity:** Medium
**Scenario:** `demo_profile_identity`
**Call SID:** `CA4eef08d8bf44055036e5e9b0410e5324`

## What Happened

The patient repeatedly provided and spelled the name Kumar Amartya. The agent misrecognized the name in multiple ways.

## Evidence

The agent used incorrect versions such as:

> Kumar amartia

and:

> Kumar and Marcia

Even after the patient spelled:

> K-U-M-A-R, A-M-A-R-T-Y-A

the agent did not reliably preserve the correct name.

## Expected Behavior

After the patient spells the name, the agent should store and repeat the name accurately.

Correct value:

> Kumar Amartya

## Impact

Identity verification is especially important in healthcare. Misstating or mutating the patient name reduces trust and can block downstream workflows.

---

# Bug 7: Agent Gave Unclear or Malformed Responses

**Severity:** Medium
**Scenario:** `location_question`
**Call SID:** `CAcc6ecc36b2802b333d93d2743e5930ae`

## What Happened

The patient asked about parking. The agent initially responded with an unclear utterance:

> 0.

The patient had to clarify whether that meant no parking was available. The agent then corrected itself and explained that free patient parking was available.

## Expected Behavior

The agent should answer parking questions directly and clearly.

For example:

> Yes, free patient parking is available in the surface lot in front of the building.

## Impact

Unclear responses force the patient to recover the conversation and may cause confusion about logistics such as parking, location, and arrival time.

---

# Additional Observations

## Incorrect or Unclear Language Fragments

Some calls included odd language fragments, such as:

> but Espanol

or incomplete phrases during the recording disclosure.

These did not always block the task, but they made the agent sound less polished.

## Caller ID / Phone Number Confusion

The agent sometimes referenced the Twilio caller ID phone number rather than a patient-provided number. This caused confusion during identity verification.

## Existing Appointment Interference

Several scenarios were affected by the agent referencing an existing routine checkup appointment. This suggests that demo-state isolation may be weak or that caller-ID-based state is being reused across calls.

---

# Overall Recommendation

The agent should improve in four areas:

1. **State isolation:** Avoid stale demo patient or appointment state affecting unrelated calls.
2. **Task progression:** Once verification is accepted, move forward instead of looping.
3. **Intent handling:** Answer simple informational questions directly when account lookup is not required.
4. **Entity accuracy:** Preserve spelled names, DOB, phone numbers, and appointment details reliably.

These improvements would make the agent more reliable across common healthcare phone workflows.
