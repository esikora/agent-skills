---
name: hackster-article
description: Write, review or shorten a project article for Hackster.io (maker / electronics / IoT community) from a hardware project repository. Use when the user wants a Hackster project description, story, write-up or tutorial, wants an existing draft checked against Hackster's guidelines, or asks how to format code, parts lists or images for Hackster.
compatibility: Works with any agent that supports Agent Skills (SKILL.md). The optional scripts need Python 3 (standard library only; censoring photos with sanitize_photos.py also needs Pillow, which `uv run` installs automatically).
---

# Authoring Hackster.io project articles

Hackster.io is a community for hardware projects (electronics, microcontrollers, IoT). A project page consists of fields entered in Hackster's project editor (name, pitch, cover image, things, story, schematics, code, ...). The **story** is the article itself. These rules help to produce a story that is accurate, readable in Hackster's editor and appealing to makers.

The rules in this file apply to any draft format (text written directly in the Hackster editor, a word processor, Markdown, ...). Writing the draft as a Markdown file in the repository is recommended: it can be reviewed and versioned together with the code, and checked automatically. For Markdown drafts, also follow the section "Markdown draft" at the end, which adds the file conventions, the checker script and how to transfer the text into the Hackster editor.

## Workflow

0. **Check that the project fits Hackster** (see "Is the project a fit for Hackster?"). If it does not, tell the author before writing anything, and suggest how it could fit (e.g. a different angle or another platform). For a Markdown draft, also check the workspace setup (folder structure, `.gitignore`, preview layout; see "Markdown draft") and suggest what is missing.
1. **Collect facts** from the repository: source code, build configuration, wiring diagram, hardware notes, datasheets, photos, commit history. Ask the author for everything that cannot be derived: dates, actual quantities of parts used, experiences (what went wrong), feedback of users, which details must stay secret.
2. **Agree on the scope**: what the article focuses on (e.g. electronics and software) and what is left out (e.g. game content, private or security relevant details).
3. **Draft** the article in the author's voice and structure (see below). If the author has published articles before, ask for one and adopt its structure and tone.
4. **Verify every technical claim** against the code and the datasheets (see "Accuracy").
5. **Check** the draft against the final checklist at the end of this file (for a Markdown draft, run the checker first, see "Markdown draft").
6. **Report** open points to the author: assumptions, values that are calculated and not measured, statements that are only true after a pending fix, placeholders that must be replaced. When asked for a review or for publish-readiness, use the "Publish-readiness report" format.
7. **Transfer and publish**: enter the meta information in the project editor, insert the story with images, and check the result in Hackster's preview (desktop and phone width) before publishing.

Never invent experiences, measurements or quotes. If a sentence is plausible but not confirmed (e.g. "the brown-out detector reset the board"), ask the author or mark it as an assumption.

## Is the project a fit for Hackster?

Hackster curates the published projects. Projects that do not meet its content guidelines are set aside until they are improved, or rejected (then they are only reachable by direct link and on the author's profile). Check these criteria from Hackster's content guidelines first:

- **Topic**: hardware, electronics or IoT (Internet of Things) projects. Apps and software-only projects are accepted only if they are directly related to hardware or IoT (e.g. firmware, a companion app, a tool for makers). Unrelated software, pure 3D printing or pure crafting without electronics does not fit.
- **Original work**: the author must own the intellectual property of the project. No plagiarism: projects based on someone else's design, code or tutorial must say so clearly, link the source, and add the author's own contribution. Third-party content (photos, diagrams, longer code) only with permission or under a license that allows it, with attribution. Short quotes (e.g. user feedback) are fine with a reference to their origin; do not name private persons without consent.
- **No sales pitch**: not simply an advertisement for a commercial product. For a product, Hackster suggests a platform hub, or an article that shows how to use the component in a real project. Store links are fine as part of the parts list, but no ads, discount codes or promotional language.
- **Language**: no strong, hateful or pornographic language.
- **Open source** is welcome (code, schematics, CAD), but not required. If parts cannot be published (e.g. an active game, commercial reasons), say so and share as much as possible.
- **Quality**: the project must be complete enough to learn from: a working result, photos, explanations, parts list, and schematics/code or a reason why they are missing.

Also consider:

- **Contests**: if the author wants to enter a Hackster contest, read the contest's rules; they often add requirements (e.g. specific hardware, deadline, mandatory sections, video).
- **Safety**: projects with mains voltage, high currents, lasers, lithium batteries or similar need clear safety notes.

## Hackster fields and meta information

Collect this information together with the author while writing the draft (in a Markdown draft as a meta block at the top, see "Markdown draft"):

- **Name** (required): descriptive and catchy; say what the project *does*, not what it is made of. No URL. A code name is fine. Components in the name only when the project is about using them.
- **Pitch** (required): one short sentence that says it all; must not repeat the name; no URL.
- **Cover image** (required): photo of the end result, high resolution, good lighting, no text, 4:3 format with the subject centered. No breadboard tangle. A GIF is possible.
- **Difficulty**: honest (Easy / Intermediate / Advanced / Hard).
- **Categories**: at most 3, describing what the project achieves, not components (not "Arduino", "ESP32"; better "Games", "Lights", "Monitoring").
- **Tags**: topics and technologies, neither too broad nor too specific, no component names.
- **Platform**: select it in the editor if there is one (e.g. Espressif ESP32).
- **Team**: real team members as members, not in "work attribution".
- **Things**: see "Parts and tools" below.
- **Schematics**: only schematics or wiring diagrams (e.g. Fritzing PNG plus `.fzz` source), each with a title and a short description. No placeholders.
- **CAD**: only CAD files.
- **Code**: attach code files with the correct language selected, or link a repository. No placeholder files to complete the checklist. If the source must not be published (e.g. active game, commercial reasons), say so in the story and show excerpts instead; attaching non-sensitive files (build configuration, reusable modules) later is a good compromise.
- **Media**: photos and optionally a short embedded video of the project in action (videos are very effective for moving parts and lights). Embed videos with the editor's video function instead of pasting a bare link.

## Parts and tools ("Things")

- Three lists: **hardware components**, **software apps and online services**, **hand tools and fabrication machines**. Software and tools go into their own lists, not the hardware list.
- One line per item: quantity actually used, then the name as on the store page, then the key specs in brackets, e.g. `- 2 × Micro switch with roller lever`. Pack sizes are not quantities. Ask the author for the actual counts.
- List **only things that are actually used** (check tools with the author), but list **all** of them, including power supply, cables, mounting material and the base object being modified.
- Give the brand and model where it matters (servo, relay, LED strip, board revision).
- Prefer store links from one source, or parts from Hackster's database. Avoid links that look like advertising where they are not needed.
- Keep the list in the draft as a bulleted list (no table) and enter it in Hackster's Things section, which links the parts to their pages.

## Structure of the story

Use this order and adapt it to the project. The editor offers **one heading level only**: use headings for the main sections and **bold paragraph titles** (a bold first phrase) for subsections.

1. **Story / introduction**: the motivation and the idea in a few sentences, a photo of the end result, the timeline (start date, completion or publication date as absolute dates), and optionally short user feedback quotes. If the project belongs to a niche (e.g. geocaching), add a short explanation for outsiders ("... for muggles").
2. **Key features**: a bulleted list, ordered by topic (what the user experiences first, then the main functions, then operation and maintenance).
3. **Development environment**: IDE, framework, build environments, the build configuration (e.g. `platformio.ini`), pinned versions and why, and one line per library explaining **what it is used for in this project**.
4. **Overview**: wiring diagram, pin assignment as a list, power supply, mounting, firmware structure (tasks, loops, cycle times). See "Wiring and power supply" below.
5. **Deep-dive sections**, one per subsystem (e.g. lighting, motor control, networking). Start each with a photo; for software-only sections, use a screenshot (e.g. of the web page or app), as long as it reveals no secrets or spoilers.
6. **Robustness / long-term operation** if relevant (watchdogs, updates, memory, settings).
7. **Lessons learned**: honest, specific, each with a bold one-line title.

Do not repeat the same information in several sections; refer to the other section instead ("see Power Supply").

## Wiring and power supply

Readers who rebuild the project need the key electrical facts, but hardly anybody wants to read pages about the voltage and current of each part. Give the essentials, concisely:

- **Wiring**: the wiring diagram (in the Schematics section and inline), plus a short list of the pin assignment (`- **GPIO 13:** servo signal`). Mention non-obvious connections in one sentence each (e.g. a relay that switches the motor supply, a series resistor, logic level 3.3 V vs. 5 V).
- **Power supply**: in a few sentences, how the project is powered (power supply rating, input used, cable), which rail feeds which parts, and the limit that matters most (e.g. the current rating of a protection diode or regulator), with the source.
- **Voltage and current**: one sentence or one short list with the main consumers and a total (e.g. "below about 1 A continuously: ESP32 about 80 mA, LED strip at most 300 mA, ..."). Mention peaks only if they matter (e.g. motor stall current) and how they are handled.
- **Logic levels**: state when signals must stay below a voltage (e.g. 3.3 V inputs) and how this is ensured.
- Keep detailed specifications, derivations and board internals (diode types, forward voltages, regulator dissipation) in the repository's hardware documentation, not in the article. If the power design was a real challenge, tell it briefly as a lesson learned instead.

## Picking the right content

- **Focus on what makers can learn or reuse**: non-obvious design decisions, constraints and their solutions, failures and how they were fixed. Leave out content that is not about hardware or software (e.g. game hints, organizational details).
- **Every term must be introduced before it is used.** Check that items in lists (features, libraries) appear in the introduction or earlier text.
- **Explain domain terms** for outsiders and **spell out each acronym once** (GPIO, PWM, OTA, SSE, RSSI, TTL, CC, PD, ...), unless it is very common (LED, USB, WiFi).
- **Avoid statements that become outdated** soon (e.g. "found by 50 users so far").
- **Credit reused work**, including the author's own earlier projects, with a link.
- **Be transparent** about tools such as AI assistants if the author wants to mention them.
- **Do not publish** (check with the author):
  - secrets: passwords, password hashes, keys, IP addresses, admin or update URLs;
  - security weaknesses that are not fixed yet (hide the relevant lines with `...`);
  - private information: names of users, exact locations, home photos with identifying details;
  - spoilers of games or puzzles the project belongs to (including photos that reveal answers and code that maps inputs to solutions);
  - links to private repositories.
- **Images**: strip metadata (GPS location, time, camera) from photos and videos **before** uploading; do not rely on the platform to remove it. Check the backgrounds and the file names. For JPEGs, use `scripts/sanitize_photos.py <src_dir> <dst_dir>`: it writes copies without any metadata and without re-encoding, and checks every copy (it fails if metadata is left). Keep the originals out of version control. For PNG, HEIC and videos use other tools (e.g. ExifTool, `ffmpeg -i in.mp4 -map_metadata -1 -c copy out.mp4`). Verify the result (no GPS data in the file properties) and never quote the coordinates. To hide parts of a photo (spoilers, names, license plates), list the areas in `censor.txt` next to the source folder (e.g. `photos/censor.txt`; one photo per line: `photo.jpg x0,y0,x1,y1 [...]`, pixels of the upright image) and keep this file in version control: the script then pixelates them on every run (only these photos are re-encoded, after stripping; needs Pillow, so run it with `uv run`). Check visually that the hidden content cannot be recognized. If the uncensored photo was ever committed or pushed, it stays in the Git history (and in the LFS storage of the remote): tell the author.

## Achieving depth on selected topics

Pick the 4 to 8 most interesting technical topics and treat each of them like this:

1. **Problem and constraint**: what had to be achieved and what made it hard (e.g. a limit switch blocks the motor, so the stall current must be cut quickly).
2. **Solution**: the idea in plain words.
3. **Code excerpt**: the essential lines only (see "Code blocks").
4. **Numbers**: cycle times, currents, voltages, delays, with the source (datasheet, code, measurement). Show how a total is derived ("debouncing 15 ms + loop 50 ms → typically below 100 ms").
5. **Pitfalls and alternatives**: what did not work and why (e.g. "Stop" signal still creeps, therefore a relay).

Topics that makers typically find interesting: power budget and supply limits, timing and task structure, debouncing, motor control (soft start, end positions, timeouts), wireless setup (access point, captive portal, channel selection), browser–device communication (both directions, sender and receiver), over-the-air updates, watchdogs and long-term operation, memory usage, overflow-safe time comparisons, version pinning.

For protocols with two directions, structure the section by direction and show sender and receiver for each.

## Accuracy

- Verify each claim against the source code: values, cycle times, pin numbers, conditions, the order of operations. Read the library or framework source when behavior depends on it.
- Use the correct terms (e.g. a MOSFET is voltage-controlled and fully on in the "ohmic" region; "saturation" means something else for MOSFETs).
- Separate **general facts** (from sources) from **findings on the author's specimen** of a generic part ("on my board, the diode is ..."). Generic boards exist in variants.
- Mark calculated or estimated values as such ("about", "typically", "calculated from the datasheet"); prefer "typically" over absolute claims when timing depends on load.
- Cite sources for specifications as clickable links.
- When the review uncovers bugs, describe the **intended** behavior only if the fix is planned, tell the author which statements depend on the fix, and keep the details of the bug out of the article.

## Length

- Keep each paragraph to one idea and at most about 5 sentences; split longer ones.
- Shorten a section when it repeats other sections, lists specifications that belong in a hardware document, or explains general background the audience knows. Keep the key numbers and the decisive reason, move the rest to the repository documentation.
- Code excerpts: typically 5 to 25 lines. Leave out irrelevant lines with `...`.
- When the author shortens a section, adopt their wording and only fix language errors and missing transitions.

## Formatting (constraints of the Hackster editor)

- **Headings**: one level only (main sections). Subsections as bold paragraph titles.
- **No tables**: the editor does not support them. Use bulleted lists with a bold label at the start of each item (e.g. "**GPIO 13:** servo signal").
- **Code blocks** (Hackster wraps long lines at a fixed width, about 84 characters, and its highlighter greys out everything after a comment or `%` up to the end of the block):
  - at most **76 characters per line**, including indentation; break after an operator or comma, split long string literals; do not rename identifiers;
  - **no comments** in code blocks (neither trailing nor full-line, also no `;` comments in ini files); explain in the text before or after the block;
  - **no `%`** in code; rewrite equivalently (`if (++i >= n) i = 0;`) and say "slightly condensed" if the excerpt differs from the original;
  - set the language of each block and check it in the Hackster preview (desktop and phone);
- **Inline code sparingly**: Hackster renders inline code as boxes with a light background in a monospace font. The editor does not show this, but in the published article several of them make a paragraph look restless and hard to read. Use inline code only for identifiers that also appear in a code block or that readers would type or search for (function names, file names such as `platformio.ini`), ideally at most one per paragraph (the checker warns from two on). Write host names, values, units, single characters and general terms as plain text, or in quotes ("the wildcard *"). Prefer describing a function ("the DNS task calls the DNS server regularly") over naming it in code formatting.
- **Images**: each with a meaningful caption, one short line:
  - say what the reader sees and why it matters (e.g. "Limit switch at the bottom of the shaft: the cabin stops here"), not "Photo 3", "The elevator" or the section title again;
  - point to details in busy images (e.g. "left: servo with winch spool, right: relay module");
  - add context the image cannot show, if relevant (when it was taken, prototype vs. final build, what is still missing);
  - no information that the text does not contain, no spoilers and no private details: many readers only skim the images and captions.
- **Links**: clickable, no bare URLs; none in name and pitch.
- **Units**: number, space, unit (`5 V`, `300 mA`, `50 ms`); consistent spelling (US or UK).

## Style

- First person, as the maker telling the story ("I", "my board").
- Short sentences, mixed with a few longer ones. No comma splices; avoid walls of text.
- Explain *why*, not only *what*.
- A little humor helps, e.g. a wink about messy wiring ("the crossing wires reflect the creative chaos of the building phase").
- Concrete user feedback quotes (translated if needed, anonymous) make the story come alive.
- Honest lessons learned (things that broke, would be done differently) are often the most valuable part for readers.

## Markdown draft

**Workspace setup** (recommended; suggest it once, apply it only after the author agrees):

- **Folder structure**:
  - `doc/hackster.md`: the draft (any name; one file per article).
  - `doc/photos/original/`: the original photos and videos. They usually contain GPS location, time and camera model. Add the folder to `.gitignore`; never commit, publish or upload these files.
  - `doc/photos/web/`: copies without metadata (`python scripts/sanitize_photos.py doc/photos/original doc/photos/web`, or `uv run ...` if photos are censored). The draft references only these.
  - `doc/photos/censor.txt` (optional): areas to pixelate in the copies (spoilers, names, license plates).
  - Wiring diagrams and screenshots (no metadata) next to the draft or in `doc/`.
- **Preview layout like on Hackster**: the skill ships `assets/hackster-preview.css` (story column width, images scaled to the column, code font size; layout only, no fonts or colors). With it, the preview shows where text and code lines wrap and how large images appear on Hackster.
  - **VS Code, VSCodium, Cursor** (the forks use the same built-in Markdown preview and the same workspace settings): copy the stylesheet into the project, e.g. `.vscode/hackster-preview.css`, and add `"markdown.styles": [".vscode/hackster-preview.css"]` to `.vscode/settings.json`. Copy it rather than referencing the skill folder: a skill installed in the home directory is outside the workspace, and the preview may refuse to load files from there. Reopen the preview afterwards (or reload the window).
  - **Other editors**: use the same file if the editor supports a custom preview stylesheet (e.g. Typora themes, Obsidian CSS snippets); otherwise skip this step. It only affects the preview.
- **Git LFS** (optional): consider it when the repository holds more than a few images or any videos (e.g. `git lfs track "*.jpg" "*.png" "*.mp4"`, which writes `.gitattributes`). It keeps clones small, since every committed version of a binary file otherwise stays in the history. Trade-offs: everyone who clones needs `git lfs install` (otherwise they get small pointer files instead of the images), hosting services limit the free LFS storage and download traffic, and not every host or CI setup supports it. For a few small photos, plain Git is fine. LFS does not protect originals: files in LFS are still uploaded to the server and kept in the history, so originals with metadata stay out of Git in any case.
- **Python 3** for the scripts (standard library only, `python` or `python3`); censoring photos (`censor.txt`) also needs Pillow (`uv run` installs it).

When applying the setup:

- **Never overwrite**: merge the `markdown.styles` entry into an existing `.vscode/settings.json` (keep other settings and existing stylesheets), append to `.gitignore`, and do not replace an existing stylesheet without asking.
- **New article**: create the folders and files as described.
- **Existing project**: first check what is already there and report only what is missing or different. Suggest moving files into the recommended structure (e.g. photos with GPS data that are tracked by Git, photos mixed with other documents, a draft without image references) only where it has a real advantage, and name it: e.g. originals out of Git history, the checker finds the images, one place for the stripped copies. Keep an existing structure that already separates originals from stripped copies. Move files only after the author agrees, then update all references (draft image paths, `README.md`, agent instructions, scripts) and run the checker to confirm that every image is found. If original photos have already been committed, tell the author that removing them from the folder does not remove them from the Git history.

Conventions for a draft written as a Markdown file (e.g. `doc/hackster.md`):

- **Meta block**: the Hackster fields (see "Hackster fields and meta information") as a blockquote at the top, starting with `> **Hackster meta information** (enter in the project editor, do not copy into the story)`. It stays in the draft as documentation. Reference the cover image there as an image (`> - **Cover image:** ![The finished house with lights on](photos/web/cover.jpg)`), so that the checker verifies it, counts it as used and lists it with `--publish`.
- **Things lists**: under their own `##` heading before the story; they are entered in Hackster's Things section, not copied into the story.
- **Headings**: `#` for the project name (title of the draft only), `##` for the main sections of the story. Subsections as a bold line of its own (`**Power Supply**`), never `###`.
- **Lists instead of tables**: `- **GPIO 13:** servo signal`; parts as `- 2 × Micro switch with roller lever`.
- **Code**: fenced code blocks with the language (` ```cpp `, ` ```javascript `, ` ```ini `).
- **Images**: real image references with the caption as alt text, `![Limit switch at the bottom of the shaft](photos/web/switch.jpg)`, with paths relative to the draft and pointing to the copies without metadata. The preview then shows the images in place. Use placeholders `[Figure: file.jpg — caption]` only while an image does not exist yet.
- **One line per paragraph or list item**: do not hard-wrap the text, otherwise bold and code spans can be split across lines.

**Checker** (`scripts/check_article.py`, Python 3, standard library only):

- `python scripts/check_article.py <draft.md> --terms` while drafting: reports errors (tables, several heading levels, code lines over 76 characters, comments or `%` in code, code blocks without language, bare URLs, image files that do not exist, JPEGs that still contain metadata such as GPS), warnings for paragraphs with more than 5 sentences or more than one inline code span, for images or placeholders without a meaningful caption, for unused images in the folders the draft takes images from (e.g. `photos/web/`) and for originals in a sibling `original/` folder without a stripped copy, and the first occurrence of each abbreviation. Fix all errors, review the warnings, and make sure each abbreviation is spelled out or explained at its first occurrence (or earlier).
- `python scripts/check_article.py <draft.md> --publish` before transferring: additionally reports figure placeholders and TODO markers as errors, and prints a list of all images in article order (section, file, caption) to work through in the editor. Transfer the story only when it reports no errors. The meta block may stay in the draft.

**Transfer into the Hackster editor**: the Hackster editor is a rich-text editor and does not interpret Markdown. Pasting the raw Markdown source leaves `#`, `**` and backticks as plain characters in the text.

- Copy from a **rendered view** instead: e.g. the Markdown preview of VS Code (Ctrl+Shift+V), the rendered file on GitHub/GitLab, or an HTML export opened in a browser (`pandoc draft.md -o draft.html`). Copy section by section rather than everything at once.
- Copy **only the story**: from the first story section (e.g. "Story") to the end. The meta block and the Things lists go into their own fields of the project editor.
- Pasting from the rendered preview keeps headings and code blocks (tested with the VS Code preview). After pasting, check that bold titles, lists, links and inline code survived as well.
- **Code blocks**: check the selected language of each block and its indentation. Only if a block arrives broken, insert it with the editor's code block function and paste the code from the Markdown source.
- **Images**: expect to upload each image manually at its position in the editor and to enter its caption there (use the image list of `check_article.py --publish`: it names the section, the file and the caption of each image). Do not add the caption as an extra text line below the image in the draft: it would be pasted into the story as a paragraph and appear twice. Images in the preview refer to local files, which a browser-based editor usually cannot upload from the clipboard. Upload only the copies without metadata.
- Check the result in Hackster's preview at desktop and phone width.

## Publish-readiness report

Use this format when the author asks for a review or whether the article is ready. It combines must-fix checks and four scores in **one table**, so that nothing important is overlooked. The reasons and the suggested improvements are the actual value; the scores only summarize them.

Keep strengths and open points in **separate columns**: "Already good" names what works (also in rows with a low score or a must-fix item), "Needs attention → next step" names each open point followed by the concrete action ("–" if nothing is open). Do not mix both in one cell, and do not use line breaks inside cells (`<br>` is not rendered in every viewer, e.g. terminals).

**Must-fix checks** (each "✅ OK" or "❗ Must fix"; must-fix items always come first, because good scores cannot compensate them):

- **Fit**: the project meets Hackster's content guidelines (see "Is the project a fit for Hackster?").
- **Confidentiality**: no secrets, unfixed security weaknesses, private data or spoilers; photo metadata stripped.
- **Truthfulness**: no claim that is known to be false or only true after a pending change; no invented experiences, measurements or quotes.
- **Completeness**: required fields available (name, pitch, cover image, Things, story); for publishing also no placeholders (Markdown draft: `--publish` without errors).

**Scores** (always written with the maximum, e.g. "8/10"; use the anchors, interpolate between them, and do not give 10/10 if a concrete improvement is known):

1. **Content and depth**
   - 0/10: a list of parts and features without explanations.
   - 5/10: all subsystems described, but few reasons, numbers or pitfalls; key topics lack depth.
   - 10/10: the most interesting topics follow problem → solution → excerpt → numbers → pitfalls; honest lessons learned; makers learn something reusable.
2. **Accuracy**
   - 0/10: many claims unverified or contradicting the code.
   - 5/10: main claims verified, but some values, terms or estimates unchecked or unmarked.
   - 10/10: every claim verified against code and sources; estimates marked; specifications linked; general facts separated from findings on the author's specimen.
3. **Readability**
   - 0/10: walls of text, unexplained jargon, no structure.
   - 5/10: clear structure, but long paragraphs, repetitions, unexplained terms or heavy inline code.
   - 10/10: logical order, short paragraphs (checker: no warnings), every term and acronym explained at first use, concise power and wiring facts, engaging first-person style.
4. **Hackster readiness**
   - 0/10: tables, several heading levels, broken code blocks, no meta information.
   - 5/10: checker errors fixed, but meta information, Things details (quantities, store names), captions or images incomplete.
   - 10/10: checker without errors and warnings, meta information complete, Things lists exact, every section with an image and a caption, transfer instructions followed.

Do not add up the scores; a total hides weak categories.

**Stage** instead of a yes/no verdict, to show progress and keep the author motivated:

- **Ready to publish**: all must-fix checks OK, every score at least 7/10.
- **Almost there**: at most two must-fix items open, and each of them can be resolved with a clear, small action (a decision, a quantity to confirm, a sentence to change); or all must-fix checks OK, but a score below 7/10.
- **Work in progress**: more must-fix items, or items that need substantial work.

Structure: a heading with an icon (so it is recognized as a heading even where Markdown headings render plainly), the table, the checker result, and then the conclusion: the overall stage (highlighted as a quote line), the main strengths of the article as a whole (not a repetition of the table cells), and the next steps. The must-fix checks are the first four rows, named by their check only (no "Must-fix:" prefix; the result column shows whether a fix is needed). Phrase must-fix items as concrete actions, not as failures.

**Output template**:

```markdown
## 📋 Publish-readiness report

| Area | Result | ✅ Already good | ⚠️ Needs attention → next step |
|---|---|---|---|
| Fit | ✅ OK | ... | – |
| Confidentiality | ❗ Must fix | ... | ... → ... |
| Truthfulness | ✅ OK | ... | – |
| Completeness | ✅ OK | ... | – |
| Content and depth | 8/10 | ... | ... → ... |
| Accuracy | 7/10 | ... | ... → ... |
| Readability | 6/10 | ... | ... → ... |
| Hackster readiness | 5/10 | ... | ... → ... |

**Checker:** <n> errors, <n> warnings (<summary>).

> 🏁 **Overall: <stage>** (<n> of 4 must-fix checks OK, scores <min>–<max>/10)

**Main strengths:** <one or two sentences on what makes the article worth reading>

**Next steps:** <the 3 most important actions, in order; must-fix items first>.
```

The report is for the author, not part of the article; it may use a table.

## Final checklist

- [ ] Project fits Hackster: hardware/electronics/IoT topic, original work with sources credited, no sales pitch or ads, appropriate language, safety notes where needed.
- [ ] Hackster fields complete (name, pitch, cover, difficulty, max. 3 categories, tags, platform).
- [ ] Things lists complete, actual quantities, store names, only used items.
- [ ] Wiring diagram, pin list, power supply, main consumers and limits covered, concisely.
- [ ] Every technical claim verified; estimates marked; sources linked.
- [ ] Every term introduced, every acronym spelled out once.
- [ ] No secrets, unfixed weaknesses, private data, spoilers; photo metadata stripped (`scripts/sanitize_photos.py`) and verified.
- [ ] One heading level, no tables, code blocks follow the formatting rules (Markdown draft: `scripts/check_article.py --terms` reports no errors, warnings reviewed).
- [ ] Open points and placeholders listed for the author (figures, video, meta information).
- [ ] Before transferring: images ready, meta information entered in the project editor (Markdown draft: `scripts/check_article.py --publish` reports no errors).
- [ ] After transferring: formatting checked in Hackster's preview (desktop and phone).
- [ ] Spelling and grammar checked; consistent spelling variant.
