import json
import logging
from pathlib import Path
from typing import Any, Dict

from datapizza.agents import Agent
from datapizza.clients.google import GoogleClient
from datapizza.clients.openai_like import OpenAILikeClient

from .formatter import format_policy_json
from .tools import list_sol_files, read_sol_file

logger = logging.getLogger("policy_agent")


class AgentRunner:
    """Encapsulates the logic for running the Datapizza agent over a set of solidity files.

    Responsibilities:
    - Build a combined prompt that includes the user's prompt and the contents of all
      `.sol` files under a target path.
    - Instantiate a Datapizza `Agent` with the provided LLM client and filesystem tools.
    - Run the agent and post-process its textual response into the canonical policy JSON
      using `format_policy_json`.
    - Persist the resulting JSON to `output_file`.

    Attributes:
        prompt_text: The textual prompt read from the prompt file (system + instructions).
        target_path: Filesystem path to the folder containing `.sol` source files.
        output_file: Path where the resulting JSON policy will be written.
        client: Optional Datapizza client instance used to call the LLM. If None, a
            default `GoogleClient` without an API key is used (caller should provide a
            configured client in production).
    """

    def __init__(
        self, prompt_text: str, target_path: str, output_file: str, client=None
    ):
        """Create an AgentRunner.

        Args:
            prompt_text: The prompt text (system + user instructions) to send to the agent.
            target_path: Directory containing `.sol` files to append to the prompt.
            output_file: File path where the parsed policy JSON will be saved.
            client: Optional Datapizza client instance. If omitted, a bare `GoogleClient`
                will be created (suitable for local testing but not production).
        """
        self.prompt_text = prompt_text
        self.target_path = target_path
        self.output_file = output_file
        self.client = client or GoogleClient(api_key=None)

    def build_combined_prompt(self) -> str:
        """Build the full prompt by concatenating the agent prompt with all `.sol` files.

        Returns:
            A single string containing the prompt followed by labeled file contents for
            each Solidity source file discovered under `target_path`.
        """
        parts = [self.prompt_text, "\n\n"]
        files = list_sol_files(self.target_path)
        for rel in files:
            content = read_sol_file(self.target_path, rel)
            parts.append(f"FILE: {rel}\n{content}\n\n")
        return "".join(parts)

    def run(self) -> Dict[str, Any]:
        """Execute the agent and persist the normalized policy JSON.

        The method will:
        - Instantiate an `Agent` with registered datapizza tools for reading files.
        - Run the agent over the combined prompt.
        - Post-process the agent's final textual response via `format_policy_json`.
        - Write the resulting JSON to `self.output_file` and return it.

        Returns:
            The dictionary representing the canonical policy JSON written to disk.

        Raises:
            Any exceptions raised by the underlying Datapizza client or I/O operations
            will propagate to the caller.
        """
        # Only pass datapizza-decorated tools to the Agent. format_policy_json is a local
        # post-processor and should not be registered as a tool.
        agent = Agent(
            name="policy_agent",
            system_prompt=self.prompt_text,
            client=self.client,
            tools=[list_sol_files, read_sol_file],
        )
        combined = self.build_combined_prompt()
        logger.info("Running agent with prompt length: %d", len(combined))
        res = agent.run(combined)
        # post-process
        out = format_policy_json(res.text)
        # write output
        out_path = Path(self.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2))
        logger.info("Wrote results to %s", out_path)
        return out
