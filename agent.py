import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Dict

# ----------------------------
# Configuration
# ----------------------------
PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}
BUFFER_MINUTES = 10
CALENDAR_INPUT_PATH = "calendar.csv"
JSON_OUTPUT_PATH = "conflicts.json"
TXT_OUTPUT_PATH = "conflicts.txt"


@dataclass
class Event:
    title: str
    start: datetime
    end: datetime
    priority: int
    event_type: str
    flexible: bool

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() / 60)

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError(f"Event '{self.title}': end time must be after start time.")


def parse_datetime(s: str) -> datetime:
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: '{s}'. Use format YYYY-MM-DD HH:MM")


def parse_effort(s: str) -> int:
    s = (s or "M").strip().upper()
    defaults = {"S": 15, "M": 45, "L": 90}
    if s in defaults:
        return defaults[s]
    try:
        return max(5, int(s.replace("min", "").replace("m", "").strip()))
    except ValueError:
        return defaults["M"]


def read_calendar(path: str = CALENDAR_INPUT_PATH) -> List[Event]:
    events: List[Event] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            title = (row.get("title") or "").strip()
            if not title:
                continue
            try:
                start = parse_datetime(row.get("start_time") or "")
                end = parse_datetime(row.get("end_time") or "")
                priority_str = (row.get("priority") or "medium").strip().lower()
                priority = PRIORITY_MAP.get(priority_str, 2)
                event_type = (row.get("type") or "general").strip()
                flexible = (row.get("flexible") or "no").strip().lower() in {"yes", "true", "1", "y"}
                events.append(Event(
                    title=title,
                    start=start,
                    end=end,
                    priority=priority,
                    event_type=event_type,
                    flexible=flexible,
                ))
            except (ValueError, KeyError) as e:
                print(f"  Warning: Skipping row {i} ('{title}'): {e}")

    return sorted(events, key=lambda e: e.start)


def detect_conflicts(events: List[Event]) -> List[Dict]:
    conflicts = []

    for i in range(len(events) - 1):
        a = events[i]
        b = events[i + 1]

        overlap = a.end > b.start
        gap = b.start - a.end
        no_buffer = not overlap and gap < timedelta(minutes=BUFFER_MINUTES)

        if overlap or no_buffer:
            conflict_type = "overlap" if overlap else "no_buffer"
            severity = "high" if (a.priority == 3 or b.priority == 3) else "medium"

            if overlap:
                overlap_minutes = int((a.end - b.start).total_seconds() / 60)
            else:
                overlap_minutes = 0

            suggestion = suggest_resolution(a, b)

            conflicts.append({
                "event_a": a.title,
                "event_b": b.title,
                "event_a_end": a.end.strftime("%Y-%m-%d %H:%M"),
                "event_b_start": b.start.strftime("%Y-%m-%d %H:%M"),
                "type": conflict_type,
                "severity": severity,
                "overlap_minutes": overlap_minutes,
                "gap_minutes": int(gap.total_seconds() / 60) if not overlap else 0,
                "suggestion": suggestion,
            })

    return conflicts


def suggest_resolution(a: Event, b: Event) -> str:
    if a.priority > b.priority and b.flexible:
        return f"Reschedule '{b.title}' — lower priority and flexible"
    if b.priority > a.priority and a.flexible:
        return f"Reschedule '{a.title}' — lower priority and flexible"
    if a.flexible and b.flexible:
        return "Either event can be rescheduled — both are flexible"
    if a.flexible:
        return f"Reschedule '{a.title}' — it is flexible"
    if b.flexible:
        return f"Reschedule '{b.title}' — it is flexible"
    return "Requires human decision — neither event is flexible"


def render_summary(conflicts: List[Dict], events: List[Event]) -> str:
    lines = [
        f"Calendar Conflict Report ({date.today()})",
        "=" * 45,
        f"Total events loaded : {len(events)}",
        f"Conflicts detected  : {len(conflicts)}",
        f"  - Overlaps        : {sum(1 for c in conflicts if c['type'] == 'overlap')}",
        f"  - No buffer (<{BUFFER_MINUTES}m) : {sum(1 for c in conflicts if c['type'] == 'no_buffer')}",
        f"  - High severity   : {sum(1 for c in conflicts if c['severity'] == 'high')}",
    ]

    if not conflicts:
        lines.append("\nNo conflicts found. Your calendar looks clean!")
        return "\n".join(lines)

    lines.append("\nConflicts\n" + "-" * 45)
    for i, c in enumerate(conflicts, 1):
        lines.append(f"\n[{i}] {c['event_a']}  →  {c['event_b']}")
        lines.append(f"    Type     : {c['type'].replace('_', ' ').title()}")
        lines.append(f"    Severity : {c['severity'].upper()}")
        if c["type"] == "overlap":
            lines.append(f"    Overlap  : {c['overlap_minutes']} minutes")
        else:
            lines.append(f"    Gap      : {c['gap_minutes']} minutes (buffer required: {BUFFER_MINUTES}m)")
        lines.append(f"    Action   : {c['suggestion']}")

    return "\n".join(lines)


def main() -> None:
    print("Loading calendar...")
    events = read_calendar()

    if not events:
        print("No events found in calendar.csv — nothing to analyse.")
        return

    print(f"Loaded {len(events)} events. Detecting conflicts...")
    conflicts = detect_conflicts(events)

    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"generated_on": date.today().isoformat(), "conflicts": conflicts}, f, indent=2)

    summary = render_summary(conflicts, events)

    with open(TXT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(summary)

    print(summary)
    print(f"\nSaved: {JSON_OUTPUT_PATH} and {TXT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()