# 📅 Calendar Conflict Detector

> A lightweight Python CLI tool that scans your scheduled events, detects time conflicts and tight gaps between meetings, and delivers a structured report with actionable resolution suggestions — no external dependencies required.

---

## ✨ Features

- **Overlap detection** — flags events that share overlapping time slots
- **Buffer gap checks** — warns when meetings are scheduled too close together (default: < 10 minutes apart)
- **Severity classification** — ranks conflicts as `high` or `medium` based on event priority
- **Smart resolution suggestions** — recommends rescheduling lower-priority or flexible events first
- **Multiple datetime formats** — supports `YYYY-MM-DD HH:MM`, ISO 8601, and `DD/MM/YYYY HH:MM`
- **Dual output** — saves results to both `conflicts.json` and `conflicts.txt`
- **Resilient parsing** — skips malformed rows with warnings instead of crashing
- **Zero dependencies** — built entirely on the Python standard library
---
## 🛠️ Requirements

- Python 3.8+
- No external packages needed

---

## 🚀 Installation

```bash
git clone https://github.com/Crevatec/Calendar-Conflict-Detector.git
cd Calendar-Conflict-Detector
```

That's it — no `pip install` required.

---

## 📖 Usage

1. Populate `calendar.csv` with your events (see [CSV format](#-csv-format) below).
2. Run the agent:

```bash
python agent.py
```

3. Review your results:
   - `conflicts.json` — machine-readable conflict data
   - `conflicts.txt` — human-readable summary report
   - Terminal — formatted summary printed directly to stdout

---

## 📋 CSV Format

Create a `calendar.csv` file in the project root with the following columns:

| Column | Required | Format | Example |
|---|---|---|---|
| `title` | ✅ | Text | `Team Standup` |
| `start_time` | ✅ | `YYYY-MM-DD HH:MM` | `2025-07-01 09:00` |
| `end_time` | ✅ | `YYYY-MM-DD HH:MM` | `2025-07-01 09:30` |
| `priority` | ✅ | `low` / `medium` / `high` | `high` |
| `type` | ✅ | Any label | `meeting` |
| `flexible` | ✅ | `yes` / `no` | `no` |

### Example

```csv
title,start_time,end_time,priority,type,flexible
Team Standup,2025-07-01 09:00,2025-07-01 09:30,high,meeting,no
Client Call,2025-07-01 09:25,2025-07-01 10:00,high,meeting,no
Code Review,2025-07-01 10:05,2025-07-01 11:00,medium,meeting,yes
Lunch Break,2025-07-01 11:00,2025-07-01 12:00,low,personal,yes
```

---

## 📤 Output

### `conflicts.json`

```json
{
  "generated_on": "2025-07-01",
  "conflicts": [
    {
      "event_a": "Team Standup",
      "event_b": "Client Call",
      "event_a_end": "2025-07-01 09:30",
      "event_b_start": "2025-07-01 09:25",
      "type": "overlap",
      "severity": "high",
      "overlap_minutes": 5,
      "gap_minutes": 0,
      "suggestion": "Requires human decision — neither event is flexible"
    }
  ]
}
```

### Terminal Report

```
Calendar Conflict Report (2025-07-01)
=============================================
Total events loaded : 4
Conflicts detected  : 2
  - Overlaps        : 1
  - No buffer (<10m) : 1
  - High severity   : 1

Conflicts
---------------------------------------------

[1] Team Standup  →  Client Call
    Type     : Overlap
    Severity : HIGH
    Overlap  : 5 minutes
    Action   : Requires human decision — neither event is flexible
```

---

## ⚙️ Configuration

You can adjust the following constants at the top of `agent.py`:

| Variable | Default | Description |
|---|---|---|
| `BUFFER_MINUTES` | `10` | Minimum gap required between events (minutes) |
| `CALENDAR_INPUT_PATH` | `calendar.csv` | Path to the input CSV file |
| `JSON_OUTPUT_PATH` | `conflicts.json` | Path for the JSON output file |
| `TXT_OUTPUT_PATH` | `conflicts.txt` | Path for the plain text output file |

---

## 🔍 Conflict & Severity Reference

### Conflict Types

| Type | Description |
|---|---|
| `overlap` | Two events share overlapping time slots |
| `no_buffer` | Gap between consecutive events is less than `BUFFER_MINUTES` |

### Severity Logic

| Condition | Severity |
|---|---|
| Either event has `priority = high` | `high` |
| Both events are `medium` or `low` priority | `medium` |

---

## 🗂️ Project Structure

```
Calendar-Conflict-Detector/
├── agent.py          # Main detection script
├── calendar.csv      # Your input events (user-provided)
├── conflicts.json    # Generated JSON output
├── conflicts.txt     # Generated plain-text report
└── README.md
```
---
## 🙈 Recommended `.gitignore`

```gitignore
conflicts.json
conflicts.txt
calendar.csv
__pycache__/
*.pyc
```
---
## 📄 License

MIT — free to use, modify, and distribute.
