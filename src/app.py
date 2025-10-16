import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

if __name__ == "__main__" and __package__ is None:
    # add repo root to sys.path so absolute imports like `src.agent_runner` work
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))

from datapizza.clients.google import GoogleClient
from dotenv import load_dotenv

from src.agent_runner import AgentRunner

load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("policy_agent")


# Configuration from environment
PROMPT_FILE = os.getenv("PROMPT_FILE", "prompts/agent_prompt.md")
TARGET_PATH = os.getenv("TARGET_PATH", "test/THORChain20210723/source-code")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "output/results.json")


def main():
    # Load prompt
    try:
        prompt_text = Path(PROMPT_FILE).read_text()
        logger.info("Loaded prompt from %s (length %d)", PROMPT_FILE, len(prompt_text))
    except Exception:
        prompt_text = (
            "You are an assistant that extracts cross-chain policy recommendations from Solidity source code. "
            "Produce JSON with an array named 'policy'."
        )

    client = GoogleClient(api_key=os.getenv("GOOGLE_API_KEY"))
    runner = AgentRunner(
        prompt_text=prompt_text,
        target_path=TARGET_PATH,
        output_file=OUTPUT_FILE,
        client=client,
    )
    runner.run()


if __name__ == "__main__":
    main()
