# EVM cross-chain Policy Agent

_A tool to extract cross-chain policies from Solidity contracts._

This project scans a folder containing Solidity (`.sol`) files, uses a language model (via [Datapizza](https://github.com/datapizza-labs/datapizza-ai) clients) to analyze the code, and produces a canonical JSON representation of cross-chain policy mappings.

Repository contents:

- a Datapizza-based agent that queries an LLM;
- local utilities to read and normalize Solidity sources (`src/tools.py`, `src/formatter.py`);
- a post-processor that converts the model output into a stable JSON schema (`src/agent_runner.py`, `src/app.py`).

## Key features

- Automatic analysis of Solidity contracts to identify cross-chain calls, related events and destination functions.
- Normalized JSON output for easy integration with security pipelines or audits.
- Command-line interface and Docker support.

## Requirements

- Python 3.10+ (recommended)
- Virtual environment (venv) or similar
- Environment variables for any external APIs used (see `.env`)

## Quick installation

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Prepare environment variables:

```bash
cp .env.example .env
```

Edit `.env` to set required API keys (e.g., `GOOGLE_API_KEY`).

> Note: the stronger the model, the higher the quality.

Set `GOOGLE_MODEL` in `.env` (e.g., `gemini-2.0-flash`) based on your quality/cost/latency trade-offs.

## Usage (CLI)

Minimum required flags: a target path with Solidity files and an output JSON file.

```bash
python3 src/app.py --target-path /path/to/sol --output-file /path/to/out/policy.json
```

Useful options:

- `--target-path`: directory containing `.sol` files to analyze.
- `--output-file`: destination JSON file.


## Running with Docker

You can run the agent inside Docker to avoid installing dependencies locally.

1. Build the image:

```bash
docker build -t crosschain-agent:latest .
```

2. Run the container (example mounting `sol` and outputting to `output`):

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/sol:/data/sol" \
  -v "$(pwd)/output:/app/output" \
  crosschain-agent:latest \
  --target-path /data/sol \
  --output-file /app/output/policy.json
```

Make sure to supply the `.env` with any required API keys.

## Output format

The agent produces a JSON document with a stable schema that maps source
functions to destination functions. Example:

```json
{
  "policy": [
    {
      "sourceFunction": {
        "name": "initGenesisBlock",
        "events": ["InitGenesisBlockEvent"]
      },
      "destinationFunction": {
        "name": "initGenesisBlock"
      }
    }
  ]
}
```

The structure is intended to be easy to parse and integrate into auditing or CI tools.

## Development and testing

Run the test suite with pytest:

```bash
source .venv/bin/activate
pytest -q
```

Tests are under `test/` and cover formatter behavior and local utilities.

## Contributing

This project follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). Install the commit hooks before
committing:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

Open a pull request targeting `main` (or `develop` for feature branches) and
ensure the tests pass.

## License

This project is licensed under the terms contained in the `LICENSE` file.
