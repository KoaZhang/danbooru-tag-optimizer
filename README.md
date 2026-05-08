# Danbooru Tag Optimizer

A Claude Code skill for generating, optimizing, and maintaining consistent Danbooru-style prompts for ComfyUI / Stable Diffusion character generation.

## Features

- **Character creation** — Generate precise Danbooru tags from a character description, with coverage across all 7 tag categories
- **Tag optimization** — Improve existing tags by replacing generic terms, filling missing categories, and adding distinctive features
- **Character consistency** — Classify tags into anchor (identity-defining) and variable (scene-dependent), with negative prompt recommendations
- **Attribute swapping** — Change expression, clothing, or scene while preserving character identity

## Install

### As a Claude Code skill
Download [danbooru-tag-optimizer.skill](https://github.com/KoaZhang/danbooru-tag-optimizer/releases/latest) and drag it into Claude Code.

### From source
Copy this directory to `~/.claude/skills/danbooru-tag-optimizer/`.

## Usage

After installing, the skill activates automatically when you talk about anime character tags. You can also invoke it explicitly in Claude Code:

```
/danbooru-tag-optimizer
```

### Examples

**Create a character from scratch:**
> 帮我创建一个原创角色：她是白发红瞳的高挑女剑士，左臂是机械义肢，左眼下有一道疤痕

**Optimize vague tags:**
> 这些 tags 太普通了：1girl, brown hair, blue eyes, school uniform, smile, standing

**Build a consistency profile:**
> 为这个角色创建一致性方案，区分锚点 tags 和可变 tags

**Swap attributes while keeping identity:**
> 把 her 表情改成微笑，服饰换成休闲装，但角色特征不变

## Dataset

~35,000 classified Danbooru tags from [Danbooru2024](https://huggingface.co/datasets/Wenaka/danbooru2024_general_tags_classified), organized into 7 categories with subcategories:

| Category | Tags | Subcategories |
|----------|------|--------------|
| 人物本身的特征 (character) | 2,429 | 14 subcategories: hair, eyes, body, skin, race, markings... |
| 表情 (expression) | 581 | — |
| 服饰 (clothing) | 8,966 | 13 subcategories: tops, bottoms, headwear, shoes, socks... |
| 动作 (action) | 4,222 | — |
| 环境/背景 (environment) | 2,398 | — |
| 物品 (objects) | 10,232 | — |
| 构图 (composition) | 614 | — |

## Project structure

```
├── SKILL.md                         # Skill instruction file
├── scripts/
│   └── search_tags.py               # Tag search / suggestion tool
├── references/
│   └── tag_categories.md            # Detailed category reference with examples
├── tags_classified/                 # ~35K classified tags (8 CSV files)
└── README.md
```

## License

Apache 2.0 — same as the source dataset.

中文说明请见 [README.zh-CN.md](README.zh-CN.md)。
