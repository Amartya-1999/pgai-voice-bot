# Final Call Log

This file lists the final calls used for the Pretty Good AI voice-bot challenge. Each call includes the scenario, Call SID, transcript path, recording path, and a short note about the observed outcome.

---

## 1. appointment_basic

**Call SID:** `CA2172a6f494cc3fe582cfb35132781069`
**Transcript:** `data/transcripts/appointment_basic__CA2172a6f494cc3fe582cfb35132781069.txt`
**Recording:** `data/recordings/audio/CA2172a6f494cc3fe582cfb35132781069.mp3`
**Notes:** Appointment scheduling flow tested. Existing appointment state affected the scheduling flow.

---

## 2. med_refill

**Call SID:** `CAd69ce2fcf700ccee265ee680dd542ee3`
**Transcript:** `data/transcripts/med_refill__CAd69ce2fcf700ccee265ee680dd542ee3.txt`
**Recording:** `data/recordings/audio/CAd69ce2fcf700ccee265ee680dd542ee3.mp3`
**Notes:** Medication refill request tested. DOB verification loop blocked the refill flow.

---

## 3. office_hours

**Call SID:** `CA589a4bd8db8a2bc4cc3b48c903802bbb`
**Transcript:** `data/transcripts/office_hours__CA589a4bd8db8a2bc4cc3b48c903802bbb.txt`
**Recording:** `data/recordings/audio/CA589a4bd8db8a2bc4cc3b48c903802bbb.mp3`
**Notes:** Office hours and weekend closure flow completed.

---

## 4. insurance_question

**Call SID:** `CAa7ce7d48fdd4f2718890c05317758b29`
**Transcript:** `data/transcripts/insurance_question__CAa7ce7d48fdd4f2718890c05317758b29.txt`
**Recording:** `data/recordings/audio/CAa7ce7d48fdd4f2718890c05317758b29.mp3`
**Notes:** Insurance question was not answered. The agent moved into an identity verification loop.

---

## 5. location_question

**Call SID:** `CAcc6ecc36b2802b333d93d2743e5930ae`
**Transcript:** `data/transcripts/location_question__CAcc6ecc36b2802b333d93d2743e5930ae.txt`
**Recording:** `data/recordings/audio/CAcc6ecc36b2802b333d93d2743e5930ae.mp3`
**Notes:** Address, parking, and arrival-time flow completed. One unclear parking response was observed.

---

## 6. reschedule_existing

**Call SID:** `CAdf97e70a5b42563b7586709b8eaa5237`
**Transcript:** `data/transcripts/reschedule_existing__CAdf97e70a5b42563b7586709b8eaa5237.txt`
**Recording:** `data/recordings/audio/CAdf97e70a5b42563b7586709b8eaa5237.mp3`
**Notes:** Reschedule flow looped after the agent found an existing appointment.

---

## 7. weekend_appointment_edge

**Call SID:** `CAc44f7742cd747b8a67bf8c54d8ccbbba`
**Transcript:** `data/transcripts/weekend_appointment_edge__CAc44f7742cd747b8a67bf8c54d8ccbbba.txt`
**Recording:** `data/recordings/audio/CAc44f7742cd747b8a67bf8c54d8ccbbba.mp3`
**Notes:** Weekend appointment request was interrupted by existing appointment state.

---

## 8. cancel_appointment

**Call SID:** `CA289d0bff36cc1f09da5ce0c53f12ac3b`
**Transcript:** `data/transcripts/cancel_appointment__CA289d0bff36cc1f09da5ce0c53f12ac3b.txt`
**Recording:** `data/recordings/audio/CA289d0bff36cc1f09da5ce0c53f12ac3b.mp3`
**Notes:** Cancellation flow looped even after the patient gave a cancellation reason.

---

## 9. demo_profile_identity

**Call SID:** `CA4eef08d8bf44055036e5e9b0410e5324`
**Transcript:** `data/transcripts/demo_profile_identity__CA4eef08d8bf44055036e5e9b0410e5324.txt`
**Recording:** `data/recordings/audio/CA4eef08d8bf44055036e5e9b0410e5324.mp3`
**Notes:** Patient name was misrecognized and mutated during identity verification.

---

## 10. unclear_patient_edge

**Call SID:** `CAb71cd57342e5c02fbe28f8014aa95037`
**Transcript:** `data/transcripts/unclear_patient_edge__CAb71cd57342e5c02fbe28f8014aa95037.txt`
**Recording:** `data/recordings/audio/CAb71cd57342e5c02fbe28f8014aa95037.mp3`
**Notes:** Existing appointment and reschedule flow became unclear.
