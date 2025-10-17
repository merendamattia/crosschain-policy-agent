import json
import re
from typing import Any, Dict, List


def _merge_policies(policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge policy entries that share the same source/destination function pair.

    The canonicalization merges entries keyed by (sourceFunction.name,
    destinationFunction.name). For duplicates the `events` list on the
    `sourceFunction` is extended with any new events (duplicates removed while
    preserving order).

    Args:
        policies: A list of policy mapping dictionaries. Each entry is expected to
            have at least `sourceFunction` and `destinationFunction` dicts with a
            `name` key. If the structure is malformed entries with missing keys may
            be grouped under a (None, None) key.

    Returns:
        A deduplicated list of policy mapping dicts with merged `events` arrays.
    """
    merged: Dict[tuple, Dict[str, Any]] = {}
    for entry in policies:
        try:
            src = entry.get("sourceFunction", {})
            dst = entry.get("destinationFunction", {})
            key = (src.get("name"), dst.get("name"))
        except Exception:
            key = (None, None)

        if key in merged:
            existing_events = merged[key]["sourceFunction"].get("events", [])
            new_events = entry.get("sourceFunction", {}).get("events", []) or []
            for ev in new_events:
                if ev not in existing_events:
                    existing_events.append(ev)
            merged[key]["sourceFunction"]["events"] = existing_events
        else:
            src_events = entry.get("sourceFunction", {}).get("events") or []
            entry.setdefault("sourceFunction", {})
            entry["sourceFunction"]["events"] = list(dict.fromkeys(src_events))
            merged[key] = entry

    # After merging, filter out entries where the sourceFunction has no events.
    result = list(merged.values())
    filtered = []
    for entry in result:
        src_events = entry.get("sourceFunction", {}).get("events") or []
        # Keep only entries that have at least one non-empty event name
        if any(ev for ev in src_events):
            filtered.append(entry)

    return filtered


def format_policy_json(raw_text: str) -> Dict[str, Any]:
    """Convert raw agent output to canonical policy JSON.

    This function attempts multiple strategies:
    1. Extract a JSON object from Markdown-style fenced code blocks (```json ... ```)
       or the first JSON-like substring, parse it and, if it contains a top-level
       `policy` key, normalize and return it.
    2. If parsing fails, apply heuristic extraction by scanning for likely function
       names and event identifiers in the text and synthesize a `policy` array.

    The final result always follows the shape: {"policy": [ ... ]} where each
    element has `sourceFunction` and `destinationFunction` objects.

    Args:
        raw_text: The textual output from the LLM/agent.

    Returns:
        A dictionary with a single `policy` key whose value is a list of mapping
        objects. If no useful content can be extracted the returned list will be
        empty.
    """

    def _extract_json_text(s: str) -> str:
        m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", s, flags=re.IGNORECASE)
        if m:
            return m.group(1)
        m = re.search(r"```[\s\S]*?(\{[\s\S]*?\})[\s\S]*?```", s)
        if m:
            return m.group(1)
        m = re.search(r"(\{[\s\S]*\})", s)
        if m:
            return m.group(1)
        return s

    extracted = _extract_json_text(raw_text)
    try:
        parsed = json.loads(extracted)
        if isinstance(parsed, dict) and "policy" in parsed:
            parsed_policy = parsed.get("policy", [])
            merged = _merge_policies(parsed_policy)
            return {"policy": merged}
    except Exception:
        pass

    # fallback heuristics (simplified)
    fn_pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    event_pattern = re.compile(r"([A-Z][A-Za-z0-9_]*Event)")
    policies = []
    lines = raw_text.splitlines()
    for i, line in enumerate(lines):
        fn_match = fn_pattern.search(line)
        if fn_match:
            fname = fn_match.group(1)
            events = []
            for j in range(i, min(i + 6, len(lines))):
                events += event_pattern.findall(lines[j])
            policies.append(
                {
                    "sourceFunction": {"name": fname, "events": events},
                    "destinationFunction": {"name": fname},
                }
            )

    merged = _merge_policies(policies)
    return {"policy": merged}
