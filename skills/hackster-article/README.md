# hackster-article (Agent Skill)

Rules and tools for writing, reviewing and shortening project articles for [Hackster.io](https://www.hackster.io): structure, parts lists, meta information, content, technical depth, length, formatting constraints of the Hackster editor, and style.

The skill uses the open [Agent Skills](https://agentskills.io) format (a folder with `SKILL.md` plus optional `scripts/`), so it works with Claude Code, OpenAI Codex, GitHub Copilot and other agents that support this format. The instructions in `SKILL.md` are tool-independent; humans can read them as a guide as well.

## Contents

| File | Purpose |
|---|---|
| `SKILL.md` | The instructions (frontmatter with name and description, then the rules and a final checklist) |
| `scripts/check_article.py` | Checks a Markdown draft for formatting problems (tables, heading levels, code block layout, inline code, long paragraphs, abbreviations, unused photos; `--publish` for leftovers before publishing) |
| `scripts/sanitize_photos.py` | Writes copies of JPEG photos without metadata (GPS location, time, camera), without re-encoding; optionally pixelates areas listed in `censor.txt` (needs Pillow) |
| `assets/hackster-preview.css` | Stylesheet for the Markdown preview that approximates the Hackster story column (width, images, code font) |

The scripts need Python 3 and use only the standard library (censoring photos with `sanitize_photos.py` also needs Pillow; `uv run` installs it). Depending on the system, call them with `python` or `python3`.

## Setup

The agent suggests this setup when you start an article (and checks it in an existing project). To set it up by hand:

- `doc/hackster.md` for the draft, `doc/photos/original/` for the original photos (add it to `.gitignore`, it contains GPS data), `doc/photos/web/` for the copies without metadata.
- Preview like on Hackster in VS Code, VSCodium or Cursor: copy `assets/hackster-preview.css` to `.vscode/hackster-preview.css` and add to `.vscode/settings.json`:

  ```json
  "markdown.styles": [".vscode/hackster-preview.css"]
  ```

  Other editors: use the stylesheet if they support custom preview CSS.
- Optional: Git LFS for images and videos, if there are more than a few (see "Workspace setup" in `SKILL.md` for the trade-offs). It does not make it safe to commit original photos.

## Installation

Copy (or symlink) the folder `hackster-article` into the skills directory of your agent. Common locations (check the current documentation of your tool, as these paths may change):

| Agent | Project skill | Personal skill (all projects) |
|---|---|---|
| Cross-tool convention | `.agents/skills/hackster-article/` | – |
| Claude Code | `.claude/skills/hackster-article/` | `~/.claude/skills/hackster-article/` |
| GitHub Copilot | `.github/skills/hackster-article/` | `~/.copilot/skills/hackster-article/` |
| OpenAI Codex | `.agents/skills/hackster-article/` or `.codex/skills/hackster-article/` | `~/.codex/skills/hackster-article/` |

The agent loads the skill automatically when a request matches its description (e.g. "write a Hackster article for this project"), or when you ask for it by name.

Agents without skill support can still use it: reference `SKILL.md` from the project's agent instructions (e.g. `AGENTS.md`, `CLAUDE.md` or `.github/copilot-instructions.md`), e.g. "When writing the Hackster article, follow `path/to/SKILL.md`".

## Usage examples

- "Write a Hackster.io article for this project. My previous article is attached for the style."
- "Review `doc/hackster.md` against the Hackster guidelines and report major findings."
- "Shorten the power supply section, keep the key numbers."
- `python scripts/check_article.py doc/hackster.md --terms` while drafting, `python scripts/check_article.py doc/hackster.md --publish` before pasting into Hackster.
- `python scripts/sanitize_photos.py photos/original photos/web` before uploading photos.
