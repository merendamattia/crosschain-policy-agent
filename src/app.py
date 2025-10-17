import argparse
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

from dotenv import load_dotenv

from src.agent_runner import AgentRunner
from src.clients import get_client

load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("policy_agent")


# Configuration from environment
PROMPT_FILE = os.getenv("PROMPT_FILE")
OUTPUT_FILE_DEFAULT = os.getenv("OUTPUT_FILE")


def main(argv: List[str] | None = None):
    """Entry point for the CLI.

    This function reads optional command-line flags to override the environment
    configuration for the prompt file, the target folder containing `.sol` files,
    and the output JSON path. If flags are not provided, environment variables
    (or hard-coded defaults) are used.

    Flags:
        --target-path: Path to the folder with Solidity files to analyze.
        --output-file: Path where the agent's resulting JSON will be written.
    """
    parser = argparse.ArgumentParser(description="Run the cross-chain policy agent")
    parser.add_argument(
        "--target-path",
        required=True,
        help="Path to folder containing .sol files (required)",
    )
    parser.add_argument(
        "--client",
        required=True,
        choices=["google", "openai"],
        help="Which LLM client to use (required): 'google' or 'openai'",
    )
    parser.add_argument(
        "--output-file",
        required=False,
        default=OUTPUT_FILE_DEFAULT,
        help=f"Path to write JSON output (default: {OUTPUT_FILE_DEFAULT})",
    )
    args = parser.parse_args(argv)

    # Load prompt
    if PROMPT_FILE:
        try:
            prompt_text = Path(PROMPT_FILE).read_text()
            logger.info(
                "Loaded prompt from %s (length %d)", PROMPT_FILE, len(prompt_text)
            )
        except Exception:
            prompt_text = (
                "You are an assistant that extracts cross-chain policy recommendations from Solidity source code. "
                "Produce JSON with an array named 'policy'."
            )
    else:
        prompt_text = (
            "You are an assistant that extracts cross-chain policy recommendations from Solidity source code. "
            "Produce JSON with an array named 'policy'."
        )
    # Select client implementation using the client registry/factory
    try:
        client = get_client(args.client)
    except KeyError as ke:
        raise RuntimeError(str(ke)) from ke
    except Exception:
        # Provide a helpful hint for optional dependencies (e.g. openai client)
        raise
    runner = AgentRunner(
        prompt_text=prompt_text,
        target_path=args.target_path,
        output_file=args.output_file,
        client=client,
    )
    runner.run()


if __name__ == "__main__":
    main()
