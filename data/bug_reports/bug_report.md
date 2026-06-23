# Bug Report

## Bug 1: Agent created or referenced incorrect demo patient details

**Severity:** High

**Call SID:** CAd4cd1fac120ef037c14eb862af5edba2

**Transcript:** `data/transcripts/CAd4cd1fac120ef037c14eb862af5edba2.txt`

**What happened:**  
During a routine checkup scheduling call, the patient bot agreed to create a demo patient profile. The agent then stated that the patient’s date of birth was July 4th, 2000, even though the patient had not provided that date of birth. The patient corrected the DOB to January 15th, 1998. Later, when the patient provided the phone number 412-555-0198, the agent repeated it back incorrectly as 412-555-5198. The agent also referenced a number ending in 6398, which appeared to come from the caller ID rather than the patient-provided phone number.

**Why this is a problem:**  
In a healthcare scheduling flow, incorrect patient identity details can cause scheduling errors, patient matching issues, or privacy concerns. The agent should not invent or assume DOB/phone information without confirmation.

**Expected behavior:**  
The agent should ask for missing patient details, repeat them back accurately, and clearly distinguish caller ID from patient-provided contact information.

**Evidence:**  
See transcript around the demo patient profile creation and phone number confirmation sections.