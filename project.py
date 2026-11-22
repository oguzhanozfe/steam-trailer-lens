"""Inspect the gameplay visibility of a manually annotated store trailer."""

import math


def items(data, key, *, allow_empty=False):
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, list) or (not value and not allow_empty) or len(value) > 500:
        raise ValueError(f"{key} must be a list of up to 500 entries")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Every entry in {key} must be an object")
    return value


def number(value, field, *, positive=False):
    if type(value) not in (int, float) or not 0 <= value <= 1e12 or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite nonnegative number at most 1e12")
    if positive and value == 0:
        raise ValueError(f"{field} must be greater than zero")
    return value


def label(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()


TITLE = "Steam Trailer Lens"
DESCRIPTION = "Measure how soon a store trailer shows gameplay and preview a six-slice microtrailer plan."
PROMPT = "Give the trailer editor one actionable edit using the opening gameplay exposure and sample windows. Treat the samples as an illustrative storyboard, not an official Steam output. Do not predict purchases or wishlists."
KINDS = {"gameplay", "cinematic", "title", "logo"}


def analyze(data: dict) -> dict:
    shots = items(data, "shots", allow_empty=True)
    duration = number(data.get("duration_seconds"), "duration_seconds", positive=True)
    records = []
    for shot in shots:
        start = number(shot.get("start"), "start")
        end = number(shot.get("end"), "end")
        kind = label(shot.get("type"), "type").lower()
        if not start < end <= duration or kind not in KINDS:
            raise ValueError("Use an in-range shot interval and a supported type")
        records.append((start, end, kind, label(shot.get("description"), "description")))
    records.sort()
    if any(right[0] < left[1] for left, right in zip(records, records[1:])):
        raise ValueError("Shot intervals must not overlap")
    gameplay = [shot for shot in records if shot[2] == "gameplay"]
    opening = min(10, duration)
    exposure = sum(max(0, min(end, opening) - start) for start, end, _, _ in gameplay)
    rows = []
    for index in range(6):
        left, right = duration * index / 6, duration * (index + 1) / 6
        choices = []
        for start, end, kind, description in records:
            a, b = max(left, start), min(right, end)
            if a < b:
                choices.append((a, b, kind, description))
        if choices:
            # Prefer gameplay; within a type take the longest available interval.
            a, b, kind, description = min(choices, key=lambda c: (c[2] != "gameplay", -(c[1] - c[0]), c[0]))
            length = min(1, b - a)
            sample = (a + b - length) / 2
            rows.append({"Slice": index + 1, "Start (s)": round(sample, 3), "Length (s)": round(length, 3),
                         "Content": kind, "Shot": description})
        else:
            rows.append({"Slice": index + 1, "Start (s)": round(left, 3), "Length (s)": 0,
                         "Content": "Unlogged", "Shot": "No annotated shot in this window"})
    first = gameplay[0][0] if gameplay else "Absent"
    seconds = sum(end - start for start, end, _, _ in gameplay)
    return {"summary": f"Gameplay occupies {exposure:g} of the opening {opening:g} seconds. The six slices below are a suggested preview edit.",
            "metrics": {"Trailer length (s)": duration, "First gameplay (s)": first,
                        "Gameplay share (%)": round(seconds * 100 / duration, 1),
                        "Opening gameplay (s)": round(exposure, 3)}, "rows": rows}
