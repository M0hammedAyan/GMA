# GMA Recording System – Updated UI Design Requirements

## 1. Purpose

Design a **touch-friendly, minimal, and error-proof UI** for a Raspberry Pi-based medical recording system used by doctors/nurses.

The system records video from:

* 1 External Webcam (2D)
* 1 Stereo 3D Camera (stitched view)

The UI must prioritize:

* Simplicity
* Clarity
* Guided workflow
* Zero user confusion

---

## 2. Mandatory Workflow (STRICT)

The system must enforce the following sequence:

1. Enter new / Select Patient
2. Validate required fields
3. Start Recording
4. Stop Recording
5. Preview & Upload Video

⚠️ Recording MUST NOT start without valid patient data.

---

## 3. Layout (Single or minimum Screen Dashboard)

The UI must be a **minimum screens interface** with clearly separated sections:

```
Header
Patient Section
Camera Preview (Compact)
Controls (Primary Action)
Status Panel
	(Uplodes Successful)
	(Uplodes Pending)
	(Uplodes Rejected)

```

---

## 4. Header Bar

Must include:

* App name: **GMA Recording System**
* System status indicator:

  * 🟢 Ready
  * 🔴 Recording
  * 🟡 Processing
* Active UHID display

Example:

```
GMA System    UHID: GMA1023    ● Recording
```

---

## 5. Patient Section (HIGH PRIORITY)

### Features:

* Enter Name/UHID
* Option to:

  * Load existing patient
  * Create new patient ID

### Fields for enterring new Patient:

* Hospital UHID ( auto-generated)
* Name (required)
* Gestational Age {in weeks} (required)
* DOB (required)
* Parent/Guardian Name (optional)
* Parent/Guardian Ph Number
* Parent/Guardian Address
* Location (Hospital/Department/Ward/Villege
* GPS cordinates (detect current Location)

---

### UI Behavior:

* "Start Recording" must be **disabled until required fields are filled**
* When recording starts:

  * All fields become **read-only**
* Patient ID must always be visible

---

## 6. Camera Preview Section (COMPACT)

### Layout:

* Full screen
* Positioned center-right or top-right

### Views:

1. **3D Stereo View (Primary)**

   * Shows stitched LEFT + RIGHT frames
   * Label: "3D Stereo View"

2. **2D Webcam View (Secondary)**

   * Smaller preview
   * Label: "2D Camera"

---

### Visual Behavior:

* Normal state → neutral border
* Recording → RED highlighted border

---

## 7. Recording Control Section (IMPORTANT CHANGE)

### Single Dynamic Button:

Replace multiple buttons with:

```
[ Start Recording ]
→ changes to →
[ Stop Recording ]
```

---

### Behavior:

* Before recording:
  → "Start Recording" (disabled until valid input)

* During recording:
  → "Stop Recording" (RED)

* After recording:
  → "Preview" button appears &
  → "Upload" button appears

---

## 8. Timer Requirement (NEW – CRITICAL)

A **live recording timer must be visible** when recording starts. Next to [ Stop Recording ] Button [00:03:56]

### Placement:

* Inside [ Stop Recording ] Button [00:03:56]
or
* Near header/status area

### Format:

```
00:00:00 → hr:mm:ss
```

### Behavior:

* Starts immediately when recording begins
* Stops when recording stops

---

## 9. Status Panel

Must display:

* Recording timer
* Save confirmation
* File path
* Errors (if any)

Example:

```
Recording: 00:02:18
Saved under Patient Name & UHID: GMA1023
Path: recordings/GMA1023/session_...
```

---

## 10. File Storage Structure

All recordings must be stored under:

```
recordings/UHID/session_DATE_TIMESTAMP/
```

Files:

* webcam.avi
* stereo_raw.avi
* stereo_stitched.avi

⚠️ No multiple folders per output type

---

## 11. Visual Design Guidelines

### Theme:

* Dark theme (low brightness)

### Colors:

Example only

| Element    | Color   |
| ---------- | ------- |
| Background | #121212 |
| Cards      | #1E1E1E |
| Primary    | #2979FF |
| Recording  | #D32F2F |
| Success    | #2E7D32 |

---

### Typography:

* Clean sans-serif font
* Minimum 16px
* Titles bold
* Inputs regular

---

### Layout Rules:

* Clean spacing
* No clutter
* Group related fields
* Large touch-friendly buttons

---

## 12. UX Rules (STRICT)

* No multiple pages
* No technical details (no camera index, logs in UI)
* No complex navigation
* Always guide next action
* Prevent invalid actions

---

## 13. System Feedback

UI must always indicate:

* Current state (Ready / Recording / Saved)
* Errors (clear and readable)
* Success messages

---

## 14. Optional Enhancements

* Blinking red recording dot
* Storage space indicator
* Confirmation popup before recording
* Smooth button transitions

---

## 15. Final Goal

A doctor/nurse should be able to:

1. Enter or select patient
2. Click Start Recording
3. Monitor timer
4. Click Stop Recording
5. Click Upload

With **zero confusion and no training required**
