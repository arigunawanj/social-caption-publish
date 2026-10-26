# Social Caption Publish

Caption & publishing package for short-form content on **TikTok, Instagram Reels, and Facebook Reels**: understand the content, research current platform rules, pick hashtags with a reason for each, write a different caption per platform, audit it with a rubric + hard checks, then wait for approval before anything is published.

**Brand- and language-neutral.** Works for any brand, creator, or agency. Brand name, handle, branded hashtags, language, region, persona, banned words, and selling mode come from a per-project brand profile. Use it on its own or as the last step of a production skill (e.g. [motion-reels-agj](https://github.com/arigunawanj/motion-reels-agj)).

Portable agent skill (`SKILL.md` standard). Works in **Claude Code, Codex, Gemini CLI, Antigravity, Cursor, GitHub Copilot, Windsurf, ChatGPT Projects**, and any agent that can read a markdown instruction file.

## What you get
```
publishing/
├── tiktok-caption.md        caption (copy-paste) · keywords · hashtags + reasons · cover title · CTA · alt hooks · rule-verified date
├── instagram-caption.md
├── facebook-caption.md
├── hashtags-research.md     candidates, scoring, rejected tags, sources & dates
├── publishing-checklist.md  hard checks + rubric table + approval status
├── content-metadata.json    brand profile + per-platform summary + analytics slot
├── caption-qc.md            output of `scp.py check`
└── approval.json            written only after the user approves
```

## Workflow
```
Content QC Passed → Brand Profile → Content Analysis → Platform Research → Keyword Research
→ Caption Drafting → Hashtag Filtering → Caption QC → Publishing Package → User Approval → Ready to Publish
```

## Rules it enforces
| Platform | Rule | Type |
|---|---|---|
| Instagram (posts & reels) | max **5 hashtags** | Official (Instagram @creators, Dec 2025) |
| TikTok Content Posting API | caption ≤ **2,200 UTF-16 units** | Official (TikTok for Developers) |
| TikTok | 3–5 relevant hashtags | Internal preset |
| Facebook Reels | 0–3 relevant hashtags | Internal preset (no official cap found) |

Plus: no auto #fyp / #viral / #reels / #explore, no engagement bait (Indonesian + English patterns such as "wajib komen", "tag 3 teman", "comment YES", "smash that like"), no brand-banned words, no identical caption across platforms, every hashtag must have a reason, rubric score ≥ 85. Rules were last verified **2026-10-26**; sources are in [`references/caption-guide.md`](skills/social-caption-publish/references/caption-guide.md). The rubric is an editorial tool, not a prediction of reach or FYP.

## Install

### One command, all agents (recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/arigunawanj/social-caption-publish/main/install.sh | sh
```
Installs globally to `~/.claude/skills/`, `~/.agents/skills/`, `~/.gemini/skills/`, and `~/.gemini/antigravity/skills/`.

Per project (writes `.claude/`, `.agents/`, `.gemini/`, `.agent/` skill folders):
```bash
curl -fsSL https://raw.githubusercontent.com/arigunawanj/social-caption-publish/main/install.sh | sh -s -- --project
```

Or with the [skills CLI](https://skills.sh): `npx skills add arigunawanj/social-caption-publish`

### Per agent
- **Claude Code (plugin)**: `/plugin marketplace add arigunawanj/social-caption-publish` then `/plugin install social-caption-publish@social-caption-publish`.
- **Gemini CLI (extension)**: `gemini extensions install https://github.com/arigunawanj/social-caption-publish`.
- **Codex**: copy `skills/social-caption-publish/` to `~/.agents/skills/` (or `.agents/skills/` in a repo). Optionally merge [`adapters/AGENTS.md`](adapters/AGENTS.md).
- **Antigravity**: copy `skills/social-caption-publish/` to `~/.gemini/antigravity/skills/` or `.agent/skills/`.
- **Cursor / GitHub Copilot / Windsurf**: copy the matching folder from [`adapters/`](adapters) plus `skills/` into your repo.
- **ChatGPT Projects**: paste [`CHATGPT_PROJECT_INSTRUCTIONS.md`](CHATGPT_PROJECT_INSTRUCTIONS.md) into Project Instructions and attach `SKILL.md`.
- **Anything else**: paste [`skills/social-caption-publish/SKILL.md`](skills/social-caption-publish/SKILL.md) as custom instructions, or use [`prompts/CAPTION_PROMPT.md`](prompts/CAPTION_PROMPT.md).

## Usage
Ask naturally (or `/social-caption-publish` where slash-skills exist):

> Bikinin caption TikTok, IG Reels, dan FB Reels buat video ini. Brand: Toko Rina (@tokorina), bahasa Indonesia, persona santai, jangan pakai kata "termurah". Ini transkripnya: …

CLI (Python 3, no dependencies):
```bash
S=~/.claude/skills/social-caption-publish/scripts/scp.py
python3 $S init my-post --brand "Toko Rina" --handle @tokorina --lang id --region ID
python3 $S check my-post        # validate → publishing/caption-qc.md
python3 $S approve my-post      # only after the user approves
python3 $S utf16 "caption text" # TikTok API length
```

## Examples
- [`examples/agj-vibe-coding/`](examples/agj-vibe-coding) — Indonesian, tech education + soft selling (brand: AGJ Labs)
- [`examples/kopi-senja-iced-latte/`](examples/kopi-senja-iced-latte) — English (MY), recipe reel (fictional brand)

## Notes
- Instructions are written in Indonesian; captions follow the brand profile's language.
- The skill never publishes on its own and never claims trends, volumes, or rankings it did not verify. Live rule checks need the agent's own web tools.
- Platform rules change — re-verify before API integrations or if the verified date is older than ~3 months.

## License
MIT
