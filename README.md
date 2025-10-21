# EVM cross-chain Policy Agent

_A tool to extract cross-chain policies from Solidity contracts._

This project scans a folder containing Solidity (`.sol`) files, uses a language model (via [Datapizza](https://github.com/datapizza-labs/datapizza-ai) clients) to analyze the code, and produces a canonical JSON representation of cross-chain policy mappings.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Latest Release](https://img.shields.io/github/v/release/merendamattia/crosschain-policy-agent?label=release)](https://github.com/merendamattia/crosschain-policy-agent/releases)
[![Actions Status](https://github.com/merendamattia/crosschain-policy-agent/actions/workflows/check-docker-image.yaml/badge.svg)](https://github.com/merendamattia/crosschain-policy-agent/actions)
[![Actions Status](https://github.com/merendamattia/crosschain-policy-agent/actions/workflows/conventional-commits-check.yaml/badge.svg)](https://github.com/merendamattia/crosschain-policy-agent/actions)
[![Actions Status](https://github.com/merendamattia/crosschain-policy-agent/actions/workflows/python-unit-tests.yaml/badge.svg)](https://github.com/merendamattia/crosschain-policy-agent/actions)

## Key features

- Automatic analysis of Solidity contracts to identify cross-chain calls, related events and destination functions.
- Normalized JSON output for easy integration with security pipelines or audits.
- Command-line interface and Docker support.

## Requirements

- Python 3.11+ (recommended)
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

Edit `.env` to set required API keys and/or configure Ollama.

> Note: the stronger the model, the higher the quality.

Set models in `.env` (e.g., `GOOGLE_MODEL=gemini-2.0-flash`) based on your quality/cost/latency trade-offs.

### Using Ollama (local models)

To use Ollama with local models, you need to:

1. Install Ollama: Download and install from [ollama.com](https://ollama.com/) for your operating system.
2. Start the Ollama server.
3. Pull a model that supports function [tools](https://ollama.com/search?c=tools).
4. Configure environment variables in `.env`:

```bash
OLLAMA_MODEL=deepseek-r1:1.5b
OLLAMA_URL=http://localhost:11434/v1
```

5. Then, run the agent with `--client ollama`.

## Usage (CLI)

Minimum required flags: a target path with Solidity files and an output JSON file.

```bash
python3 src/app.py \
  --target-path /path/to/sol \
  --output-file /path/to/out/policy.json \
  --client <client>
```

Useful options:

- `--target-path`: directory containing `.sol` files to analyze.
- `--output-file`: destination JSON file.
- `--client`: LLM client to use (`google`, `openai`, or `ollama`).


## Running with Docker

You can run the agent inside Docker to avoid installing dependencies locally.

1. Pull the published image from Docker Hub:

```bash
docker pull merendamattia/crosschain-policy-agent:latest
```

2. Run the container (example mounting `sol` and outputting to `output`):

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/sol:/data/sol" \
  -v "$(pwd)/output:/app/output" \
  merendamattia/crosschain-policy-agent:latest \
  --client google \
  --target-path /data/sol \
  --output-file /app/output/policy.json
```

> Make sure to supply the `.env` with any required API keys.

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
