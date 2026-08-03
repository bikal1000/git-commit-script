# commit-lint

`commit-lint` is a Python rewrite of the original [`git-commit-script`](#legacy-git-commit-script)
bash script. It keeps the same interactive type/scope/message flow and
`<Type>(<scope>): <message> #<task_id>` output format, but now reads your
`git diff --staged` to **suggest** the type, scope, and subject instead of
asking blind — you just confirm or override each one.

## Installation

No cloning needed, not published on PyPI (yet) — install straight from this
repo with [pipx](https://pipx.pypa.io/) (or `pip`), Python 3.9+ required:

```shell
pipx install git+https://github.com/bikal1000/git-commit-script.git
```

That's it — the `commit-lint` command is now on your PATH. Run it from
inside any git repo after `git add`. See [Usage](#usage) below.

To update later to the latest version on `main`:

```shell
pipx upgrade commit-lint
# if that doesn't pick up new commits, force a reinstall:
pipx install --force git+https://github.com/bikal1000/git-commit-script.git
```

### With optional AI subject suggestions

```shell
pipx install "commit-lint[ai] @ git+https://github.com/bikal1000/git-commit-script.git"
# or
pip install "commit-lint[ai] @ git+https://github.com/bikal1000/git-commit-script.git"
```

### Private repo

Same commands, just use an SSH URL instead of HTTPS (requires your SSH key
added to GitHub):

```shell
pipx install git+ssh://git@github.com/bikal1000/git-commit-script.git
```

### From a local clone (editable install, for development)

```shell
git clone https://github.com/bikal1000/git-commit-script.git
cd git-commit-script
pip install -e ".[dev,ai]"
```

Only needed if you're editing the code — regular users don't need to clone.

Once published to PyPI, `pip install commit-lint` / `pipx install commit-lint`
will work directly — this section will be updated then.

## Usage

Stage your changes as usual, then run `commit-lint` (or `commit-lint commit`,
its default subcommand) from inside the repo:

```shell
git add src/auth.py
commit-lint
```

If your current branch is `XP-1548-feature-branch-name`, you'll see
suggestions pulled from the staged diff, and can accept each with Enter or
type an override:

```shell
╭─ commit-lint ─────────────────────╮
│ branch: XP-1548-feature-branch-name│
│ task id: XP-1548                   │
╰────────────────────────────────────╯
Commit type [Update/Add/Change/Fix/Refactor/Remove/Test/Docs] (Add): ⏎
Scope (auth): ⏎
Subject (update auth.py): Implemented new feature
```

```shell
# output
git commit -m "Add(auth): Implemented new feature #XP-1548"
```

### Push after committing

```shell
commit-lint --push
# or
commit-lint -p
```

### AI-assisted subject line

Uses any **OpenAI-compatible** chat completions API — OpenAI itself, Azure
OpenAI, Groq, Together, Ollama, vLLM, LM Studio, etc.

```shell
export OPENAI_API_KEY=sk-...
commit-lint --ai
```

**Where to set it:** commit-lint reads config from real environment
variables only — it does **not** auto-load a `.env` file. Set it one of
these ways:

- One-off: `export` the vars in your current shell session.
- Persistent: add the `export` lines to your shell profile (`~/.bashrc`,
  `~/.zshrc`) so they're set in every new terminal.
- Per-project `.env`: if you keep secrets in a `.env` file, load it with
  [`direnv`](https://direnv.net/) or `set -a; source .env; set +a` before
  running `commit-lint --ai` — commit-lint itself won't read the file
  directly.

Env vars:

- `OPENAI_API_KEY` — required.
- `OPENAI_BASE_URL` — point at your own OpenAI-compatible endpoint (self-hosted,
  Azure, Groq, a local Ollama/vLLM/LM Studio server, etc). **Required if you're
  not using OpenAI's own API** — without it, requests go to
  `https://api.openai.com/v1`.
- `OPENAI_MODEL` — defaults to `gpt-4o-mini`. Set to whatever model name your
  endpoint serves.

If you're pointing at your own endpoint, add all three to your shell profile
so they persist across terminals:

```shell
# ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY=your-key-or-token
export OPENAI_BASE_URL=https://your-own-endpoint/v1
export OPENAI_MODEL=your-model-name
```

```shell
# example: local Ollama server
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama   # any non-empty value
export OPENAI_MODEL=llama3.1
commit-lint --ai
```

Sends the staged diff (truncated to a safe size) for a concise,
imperative-mood subject line. If `OPENAI_API_KEY` isn't set, the `openai`
package isn't installed, or the API call fails, `commit-lint` prints a
warning and falls back to the rule-based subject — AI is never required for
core functionality.

### Git hook: pre-fill the commit message editor

```shell
commit-lint install-hook
```

Installs a `prepare-commit-msg` hook in `.git/hooks/` that runs
`commit-lint suggest` non-interactively (rule-based only, no prompts, no AI
calls) and pre-fills the message when you run plain `git commit` (opens your
editor). It skips merges, amends, and any commit where a message was already
supplied via `-m`/`-F`.

### Version

```shell
commit-lint --version
```

## How suggestions are computed

1. `git diff --staged --name-status` is parsed into `(status, filepath)`
   entries (A/M/D/R).
2. **Type** priority: all files added → `Add`; all files deleted → `Remove`;
   all changed files match test patterns (`test_*.py`, `*_test.py`,
   `tests/`) → `Test`; all match doc patterns (`*.md`, `*.rst`, `docs/`) →
   `Docs`; branch name contains `fix`/`bug`/`hotfix` → `Fix`; otherwise →
   `Change`.
3. **Scope**: most common top-level directory among changed files, the
   filename stem if only one file changed, or `root` if changes are spread
   across unrelated top-level paths.
4. **Subject**: rule-based summary of file changes (e.g. `update auth.py and
   2 other files`), or an AI-generated line with `--ai`.
5. **Task ID**: extracted from the branch name via `^([A-Z]+-\d+)` (e.g.
   `XP-1548-feature-name` → `#XP-1548`). Omitted entirely if the branch name
   doesn't match.

## Migrating from git-commit-script

- Command name changes from `commit` to `commit-lint` (the `commit`
  subcommand is also the default, so `commit-lint` alone works).
- Type/scope/subject are now **pre-filled suggestions** derived from your
  staged diff rather than blank prompts — press Enter to accept or type to
  override, same as before.
- `-p` still pushes after commit; the long form `--push` is now also
  available.
- New: `--ai` for AI-suggested subject lines, and `install-hook` to wire
  suggestions into plain `git commit` via a `prepare-commit-msg` hook.
- Same output format: `<Type>(<scope>): <message> #<task_id>`, task ID
  omitted if the branch doesn't match `[A-Z]+-\d+`.
- Requires Python 3.9+ instead of bash; install via `pip`/`pipx` instead of
  `curl`-ing a script into `/usr/local/bin`.

## Legacy: git-commit-script

The original bash script is still kept in this repo as [`commit`](commit)
for reference / anyone not ready to move to the Python tool. It has the same
core behavior minus diff-based suggestions:

```shell
sudo curl https://raw.githubusercontent.com/bikal1000/git-commit-script/master/commit -o /usr/local/bin/commit && sudo chmod +x /usr/local/bin/commit
```

```shell
commit
# Select commit type:
# 1) Update
# 2) Add
# 3) Change
# 4) Fix
# 5) Refactor
# #? 1
# Enter scope: my-feature
# Enter commit message: Implemented new feature
#
# git commit -m "Add(my-feature): Implemented new feature #XP-1548"
```

## Development

```shell
pip install -e ".[dev]"
pytest
ruff check .
```

## License

MIT. See [LICENSE](LICENSE).
