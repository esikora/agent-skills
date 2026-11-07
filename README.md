# Agent Skills

A collection of [Agent Skills](https://agentskills.io): folders with a `SKILL.md` (instructions with a name and a description) and optional scripts, which AI coding agents load when a task matches. The skills are tool-independent and work with Claude Code, OpenAI Codex, GitHub Copilot and other agents that support the format.

## Skills

| Skill | Description |
|---|---|
| [hackster-article](skills/hackster-article/) | Write, review or shorten a project article for [Hackster.io](https://www.hackster.io) from a hardware project repository: structure, parts lists, meta information, content, technical depth, length, editor formatting constraints, style. Includes a checker for Markdown drafts and a tool that strips photo metadata and optionally pixelates areas of photos. |

## Installation

Copy (or symlink) a skill folder from `skills/` into the skills directory of your agent, e.g.:

| Agent | Project skill | Personal skill (all projects) |
|---|---|---|
| Cross-tool convention | `.agents/skills/<skill>/` | – |
| Claude Code | `.claude/skills/<skill>/` | `~/.claude/skills/<skill>/` |
| GitHub Copilot | `.github/skills/<skill>/` | `~/.copilot/skills/<skill>/` |
| OpenAI Codex | `.agents/skills/<skill>/` or `.codex/skills/<skill>/` | `~/.codex/skills/<skill>/` |

These locations may change; check the current documentation of your tool. Each skill's README describes its requirements and usage.

## Repository layout

```
skills/<skill>/SKILL.md      instructions (frontmatter: name, description, compatibility)
skills/<skill>/README.md     description for humans: contents, installation, usage
skills/<skill>/scripts/      optional helper scripts
tests/                       automated tests of the scripts
```

## Development

Run the tests (Python 3, standard library only; tests that need Pillow are skipped without it):

```sh
python -m unittest discover -s tests -v
uv run --with pillow python -m unittest discover -s tests -v   # including the Pillow tests
```

Rules for skills in this repository:

- Keep skills agent-independent: use the folder layout and frontmatter fields of the Agent Skills specification, and avoid agent-specific frontmatter fields, tool names or slash commands unless there is a good reason (then keep the skill usable without them). State external requirements (e.g. Python, packages) in the `compatibility` field.
- The folder name must match the `name` in the frontmatter (lowercase, hyphens).
- Scripts use only the Python standard library and print their usage when called without arguments. Exception: an optional feature may need a package (e.g. Pillow for censoring photos). Declare it as inline script metadata (PEP 723) so that `uv run` installs it, import it only where the feature needs it, and keep everything else working without it.
- One line per paragraph or list item in Markdown files (no hard wrapping inside formatting spans).

## License

[MIT](LICENSE)
