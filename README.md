# Lore

A Python learning project for an agent that extracts engineering decisions from
code. Right now, it only sends one prompt through a provider adapter and prints the response.

## Run

`uv` manages Python, the local `.venv`, and the dependencies pinned in `uv.lock`.

```sh
uv sync
export OPENROUTER_API_KEY="your-key"
uv run lore hello --model openrouter/free
uv run lore hello "Say hello to someone learning to build agents." --model openrouter/free
```

OpenRouter is the default provider. Choose a model explicitly with `--model` or
`LORE_MODEL`; there is no implicit model default. Copy a free model's exact ID
(including its `:free` suffix) from the [model catalog](https://openrouter.ai/models).
The example `openrouter/free` is OpenRouter's
[free-model router](https://openrouter.ai/docs/guides/routing/routers/free-router):
it selects an available free model, so the underlying model can vary per request.
Select a specific model ID for repeatable experiments. Free models have quotas
and may be unavailable; the CLI reports errors without retrying or choosing a
paid fallback. Explicitly selecting a paid model can incur charges.

Provider and model can be selected through environment variables or CLI flags;
flags take precedence:

```sh
export LORE_PROVIDER=openrouter
export LORE_MODEL=openrouter/free
uv run lore hello "Hello!"
```

Gemini remains available with `--provider gemini --model YOUR_GEMINI_MODEL` and
`GEMINI_API_KEY`. Only OpenRouter and Gemini are implemented.
Keys are read from the environment, not from files automatically. If you prefer
an ignored `.env` file, `uv run --env-file .env lore hello` loads it explicitly.

## Read the code

1. `src/lore/cli.py`: parse arguments, choose a provider, print the response.
2. `src/lore/providers/__init__.py`: the provider protocol and adapter selection.
3. `src/lore/providers/openrouter.py`: translate that interface into an HTTP request.
4. `src/lore/providers/gemini.py`: the alternative Google SDK adapter.

The initial provider contract is intentionally just `generate(prompt) -> str`.
Add another adapter and a factory branch to support another provider. Extend the
contract when conversation messages, tool calls, or structured output are actually
needed. SDK types stay inside adapters.

Pydantic is installed for the future decision schema, but no schema or extraction
workflow is implemented yet. There are no repository tools, routing rules,
conversation persistence, or decision writes.

## Verify locally

```sh
uv run python -m unittest discover -s tests -v
uv run lore --help
```

Tests run the real CLI and adapters against in-memory HTTP fixtures. They
never call an external model or require an API key. A live hello-world call is a
separate manual check.
