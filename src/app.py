import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from datapizza.agents import Agent
from datapizza.clients.google import GoogleClient
from datapizza.clients.openai_like import OpenAILikeClient
from datapizza.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("policy_agent")


# Configuration from environment
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
PROMPT_FILE = os.getenv("PROMPT_FILE", "/prompt.txt")
TARGET_PATH = os.getenv("TARGET_PATH", "/data")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "/output/results.json")


@tool
def list_sol_files(folder: str) -> list:
    """Return a list of .sol file paths under the folder (relative paths)."""
    base = Path(folder)
    if not base.exists():
        return []
    files = [str(p.relative_to(base)) for p in base.rglob("*.sol") if p.is_file()]
    return files


@tool
def read_sol_file(folder: str, relative_path: str) -> str:
    """Read and return the contents of a solidity file given a base folder and relative path."""
    p = Path(folder) / relative_path
    try:
        return p.read_text()
    except Exception as e:
        return f"<error reading {relative_path}: {e}>"


@tool
def format_policy_json(raw_text: str) -> Dict[str, Any]:
    """Post-process raw agent text into the structured policy JSON schema.

    Strategy:
    - If raw_text is valid JSON and already contains 'policy', return it.
    - Otherwise, try to extract pairs of source/destination function names and events using regex.
      This is a heuristic: we look for patterns like `functionName` and event names in square brackets or words like Event/Events.
    """

    # Try to parse JSON directly. First, trim Markdown code fences if present
    def _extract_json_text(s: str) -> str:
        # Look for ```json ... ```
        m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", s, flags=re.IGNORECASE)
        if m:
            return m.group(1)
        # Look for any ``` ... ``` block containing JSON
        m = re.search(r"```[\s\S]*?(\{[\s\S]*?\})[\s\S]*?```", s)
        if m:
            return m.group(1)
        # Fallback: find the first {...} JSON-like substring
        m = re.search(r"(\{[\s\S]*\})", s)
        if m:
            return m.group(1)
        return s

    extracted = _extract_json_text(raw_text)
    try:
        parsed = json.loads(extracted)
        if isinstance(parsed, dict) and "policy" in parsed:
            # Merge duplicate policy entries if any
            parsed_policy = parsed.get("policy", [])
            merged = _merge_policies(parsed_policy)
            return {"policy": merged}
    except Exception:
        # If parsing fails, continue to heuristics below
        pass

    policies: List[Dict[str, Any]] = []

    # Heuristic: find lines that mention source/destination or look like function declarations
    # Find function names (word characters) followed by parentheses or the word 'function'
    fn_pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    # Find Event names (words that end with Event or look like capitalized identifiers)
    event_pattern = re.compile(r"([A-Z][A-Za-z0-9_]*Event)")

    # Split into lines and scan for potential mappings
    lines = raw_text.splitlines()
    for i, line in enumerate(lines):
        # look for a function name on the line
        fn_match = fn_pattern.search(line)
        if fn_match:
            fname = fn_match.group(1)
            # look ahead a few lines for events
            events: List[str] = []
            for j in range(i, min(i + 6, len(lines))):
                events += event_pattern.findall(lines[j])

            # Build a policy entry assuming destination function is same name (heuristic)
            policies.append(
                {
                    "sourceFunction": {"name": fname, "events": events},
                    "destinationFunction": {"name": fname},
                }
            )

    # If nothing found, attempt to extract patterns like 'Function: name' or 'Event: Name'
    if not policies:
        func_label_pattern = re.compile(r"Function[:\s]+([A-Za-z_][A-Za-z0-9_]*)")
        event_label_pattern = re.compile(r"Event[:\s]+([A-Za-z_][A-Za-z0-9_]*)")
        current_funcs: List[str] = func_label_pattern.findall(raw_text)
        current_events: List[str] = event_label_pattern.findall(raw_text)
        for idx, fn in enumerate(current_funcs):
            evts = (
                [current_events[idx]] if idx < len(current_events) else current_events
            )
            policies.append(
                {
                    "sourceFunction": {"name": fn, "events": evts},
                    "destinationFunction": {"name": fn},
                }
            )

    # Merge duplicates before returning
    merged_policies = _merge_policies(policies)
    return {"policy": merged_policies}


def _merge_policies(policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge policy entries that share the same sourceFunction and destinationFunction names.

    Combines 'events' arrays (deduplicating while preserving order) and returns a
    list of unique policy entries.
    """
    merged: Dict[tuple, Dict[str, Any]] = {}
    for entry in policies:
        try:
            src = entry.get("sourceFunction", {})
            dst = entry.get("destinationFunction", {})
            key = (src.get("name"), dst.get("name"))
        except Exception:
            # If malformed, skip merging for this entry by using its id
            key = (None, None)

        if key in merged:
            # extend events, preserving order and avoiding duplicates
            existing_events = merged[key]["sourceFunction"].get("events", [])
            new_events = entry.get("sourceFunction", {}).get("events", []) or []
            for ev in new_events:
                if ev not in existing_events:
                    existing_events.append(ev)
            merged[key]["sourceFunction"]["events"] = existing_events
        else:
            # ensure events list exists
            src_events = entry.get("sourceFunction", {}).get("events") or []
            entry.setdefault("sourceFunction", {})
            entry["sourceFunction"]["events"] = list(dict.fromkeys(src_events))
            merged[key] = entry

    return list(merged.values())


def build_combined_prompt(user_prompt: str, folder: str) -> str:
    """Append contents of .sol files to the provided user_prompt text."""
    base = Path(folder)
    parts = [user_prompt, "\n\n"]
    files = list_sol_files(folder)
    for rel in files:
        content = read_sol_file(folder, rel)
        parts.append(f"FILE: {rel}\n{content}\n\n")

    return "".join(parts)


def main():
    client = GoogleClient(api_key=os.getenv("GOOGLE_API_KEY"))

    # Load system/user prompt from PROMPT_FILE; fall back to a concise default
    try:
        prompt_text = Path(PROMPT_FILE).read_text()
        logger.info(
            "Loaded prompt from %s (length %d): \n%s",
            PROMPT_FILE,
            len(prompt_text),
            prompt_text,
        )
    except Exception:
        prompt_text = (
            "You are an assistant that extracts cross-chain policy recommendations from Solidity source code. "
            "Produce JSON with an array named 'policy'."
        )

    agent = Agent(
        name="policy_agent",
        system_prompt=prompt_text,
        client=client,
        tools=[list_sol_files, read_sol_file, format_policy_json],
    )

    combined_prompt = build_combined_prompt(prompt_text, TARGET_PATH)

    logger.info("Running agent with prompt length: %d", len(combined_prompt))
    logger.debug("Combined prompt: %s", combined_prompt)
    res = agent.run(combined_prompt)

    # Post-process agent output into structured policy JSON using the tool
    try:
        out = format_policy_json(res.text)
    except Exception:
        # Fallback: try direct JSON parse
        try:
            out = json.loads(res.text)
        except Exception:
            out = {"raw": res.text}

    # Ensure output directory exists
    out_path = Path(OUTPUT_FILE)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    logger.info("Wrote results to %s", out_path)


if __name__ == "__main__":
    main()
