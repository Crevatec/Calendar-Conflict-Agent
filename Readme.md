# Calendar Conflict Detector

A Python CLI agent that reads scheduled events from a CSV file, detects time conflicts and insufficient gaps between meetings, and outputs a structured conflict report with actionable resolution suggestions.

## Features

- Detects **overlapping events** and **events with insufficient buffer time**
- Classifies conflict **severity** (high / medium) based on event priority
- Suggests smart resolutions — reschedule lower-priority or flexible events first
- Supports **multiple datetime formats** (`YYYY-MM-DD HH:MM`, ISO 8601, `DD/MM/YYYY HH:MM`)
- Outputs results to `conflicts.json` and `conflicts.txt`
- Prints a formatted summary report to the terminal
- Gracefully **skips malformed rows** with warnings instead of crashing

## Requirements

- Python 3.8+
- No external dependencies — standard library only

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Crevatec/Calendar-Conflict-Detector.git
   cd Calendar-Conflict-Detector
   ```

2. **No pip install needed** — uses only Python standard library.

## Usage

1. Add your events to `calendar.csv` (see format below).

2. Run the agent:

   ```bash
   python agent.py
   ```

3. Results are saved to:
   - `conflicts.json` — structured conflict data
   - `conflicts.txt` — human-readable report

## Calendar CSV Format

Create a `calendar.csv` file with these columns:

| Column       | Required | Format                          | Example                  |
|--------------|----------|---------------------------------|--------------------------|
| `title`      | Yes      | Text                            | Team Standup             |
| `start_time` | Yes      | `YYYY-MM-DD HH:MM`              | 2025-07-01 09:00         |
| `end_time`   | Yes      | `YYYY-MM-DD HH:MM`              | 2025-07-01 09:30         |
| `priority`   | Yes      | `low` / `medium` / `high`       | high                     |
| `type`       | Yes      | Any label                       | meeting                  |
| `flexible`   | Yes      | `yes` / `no`                    | no                       |

### Example `calendar.csv`

```csv
title,start_time,end_time,priority,type,flexible
Team Standup,2025-07-01 09:00,2025-07-01 09:30,high,meeting,no
Client Call,2025-07-01 09:25,2025-07-01 10:00,high,meeting,no
Code Review,2025-07-01 10:05,2025-07-01 11:00,medium,meeting,yes
Lunch Break,2025-07-01 11:00,2025-07-01 12:00,low,personal,yes
```

## Output Format

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

## Configuration

Edit these constants at the top of `agent.py`:

| Variable              | Default          | Description                            |
|-----------------------|------------------|----------------------------------------|
| `BUFFER_MINUTES`      | `10`             | Minimum gap required between events    |
| `CALENDAR_INPUT_PATH` | `calendar.csv`   | Path to the input CSV file             |
| `JSON_OUTPUT_PATH`    | `conflicts.json` | Path for JSON output                   |
| `TXT_OUTPUT_PATH`     | `conflicts.txt`  | Path for plain text output             |

## Conflict Types

| Type        | Description                                              |
|-------------|----------------------------------------------------------|
| `overlap`   | Two events share overlapping time slots                  |
| `no_buffer` | Gap between events is less than `BUFFER_MINUTES`         |

## Severity Logic

| Condition                            | Severity |
|--------------------------------------|----------|
| Either event has `priority = high`   | High     |
| Both events are medium or low        | Medium   |

## Project Structure

```
Calendar-Conflict-Detector/
├── agent.py          # Main script
├── calendar.csv      # Input events (you provide this)
├── conflicts.json    # Generated JSON output
├── conflicts.txt     # Generated text report
└── README.md         # This file
```

## .gitignore Recommendation

```
conflicts.json
conflicts.txt
calendar.csv
__pycache__/
*.pyc
```

## License

MIT