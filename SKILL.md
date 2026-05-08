---
name: danbooru-tag-optimizer
description: >-
  IF user needs anime/illustration character tags to be more
  distinctive/specific, create an original character profile
  (OC/原创角色/オリキャラ), fix character identity drift across
  prompts (角色不一致/キャラ統一), or translate a character
  description into structured Danbooru tags. NOT for: photography,
  realism, ComfyUI nodes/workflows, model training, or prompts
  lacking a character focus. Supports 中文/日本語/English.
---

# Danbooru Tag Optimizer

You have access to a classified dataset of ~35,000 Danbooru tags organized into 7 categories with subcategories. Use it to help the user build precise, distinctive, and consistent character prompts for ComfyUI / Stable Diffusion image generation.

## Tag category system

There are 7 main categories, each covering a different aspect of the image:

| # | Category | Key | Description |
|---|----------|-----|-------------|
| 1 | 人物本身的特征 | `character` | Hair color/style, eyes, body type, skin, race, facial features |
| 2 | 表情 | `expression` | Facial expressions, emotions |
| 3 | 服饰 | `clothing` | Outfits, accessories, shoes, headwear, jewelry |
| 4 | 动作 | `action` | Poses, gestures, actions, body language |
| 5 | 环境/背景 | `environment` | Scenes, locations, backgrounds, settings |
| 6 | 物品 | `object` | Props, tools, held items, objects in scene |
| 7 | 构图 | `composition` | Camera angles, framing, number of characters, perspective |

Use `python3 scripts/search_tags.py` to look up specific tags. Key commands:

```bash
python3 scripts/search_tags.py --list-categories          # Overview of all categories
python3 scripts/search_tags.py --list-subcategories       # All subcategories with tag counts
python3 scripts/search_tags.py --subcategory "头发/发型"   # Tags in a subcategory
python3 scripts/search_tags.py --keyword "braid"          # Search by keyword
python3 scripts/search_tags.py --suggest "white hair red eyes tall"  # Suggest tags from description
python3 scripts/search_tags.py --random --subcategory "表情" --count 15  # Random samples
```

When you need to find the right tags, always use this script rather than guessing. It's fast and authoritative.

## Three core workflows

### Workflow 1: Character creation from description (设定 → Tags)

When the user describes a character concept and wants a complete tag set, follow this process:

1. **Understand the character** — Read the user's description carefully. Note the implied visual traits, personality, and any reference images or concepts mentioned.

2. **Systematically build tags by category** — Go through each of the 7 categories in order. For each:
   - Search for relevant tags using the script (`--suggest` is a good starting point, then refine with `--keyword` or `--subcategory`)
   - Select the most precise tag, not a generic one. For example, prefer `drill_hair` over just `long_hair` if the character has drill-style hair
   - If no existing tag exactly matches, pick the closest one

3. **Prioritize distinctiveness** — A character is recognizable when tags are specific and form a unique combination:
   - **Silhouette**: Hairstyle and clothing shape should be distinctive. A character with `twin_drills` is more recognizable than one with just `long_hair`
   - **Color anchors**: Pick specific hair/eye/skin colors from the dataset — `scarlet_hair` is more distinctive than `red_hair`
   - **Signature element**: Every distinctive character should have 1-2 tags that are unusual or unique combinations — a specific accessory, an unusual eye shape, a body marking
   - **Avoid generic clusters**: A character described only as `1girl, brown_hair, blue_eyes, school_uniform` will be indistinguishable from thousands of others. Push for specificity.

4. **Output format** — Output ONLY the comma-separated tags, no explanation:
   ```
   tag1, tag2, tag3, ...
   ```
   Order: character features first (hair, eyes, body, skin), then clothing, then expression/action, then environment/composition last.

### Workflow 2: Tag optimization (已有的Tags → 优化后的Tags)

When the user provides an existing set of tags to improve:

1. **Audit the tags** — Identify what's missing or imprecise:
   - Which categories are underrepresented or absent?
   - Which tags are too generic and could be more specific?
   - Are there contradictory tags?
   - Are there Danbooru tag conventions being violated?

2. **Search and replace** — For each imprecise tag, use the script to find better alternatives

3. **Fill gaps systematically** — Go through each category and suggest additions

4. **Output** — The optimized comma-separated tag list, followed by a brief change summary:
   ```
   [optimized tags]
   ---
   Added: [new tags]
   Replaced: [old → new]
   Removed: [tags]
   ```

### Workflow 3: Attribute swap while keeping character identity (换属性，保一致)

When the user wants to change specific attributes (expression, clothing, pose, background) while keeping the character recognizable:

1. **Identify anchor tags** — Parse the input tags and separate them into anchor (identity) and variable (scene):
   - Anchor: hair color/style, eye color, body type, skin, markings, race/species, signature accessories
   - Variable: expression, clothing, action/pose, held objects, environment, composition

2. **Keep all anchor tags unchanged** — None of the character-defining tags should be touched

3. **Swap only the requested variable tags** — Use the search script to find the right replacement tags for what the user asked to change. If the user says "smile", search for the most appropriate smile-related expression tag. If they say "casual clothes", search for casual clothing tags consistent with the character

4. **Prune conflicting variable tags** — After swapping, remove any variable tags that conflict with the new ones. For example, if swapping to `casual`, remove combat-related clothing and objects (like `holding_sword`)

5. **Output** — The full comma-separated tag list with changes, followed by a change summary:
   ```
   [complete tag list with anchors preserved + new variable tags]
   ---
   Preserved: [anchor tags kept unchanged]
   Replaced: [old → new]
   Removed: [conflicting tags]
   ```

## Character consistency system

The key to character consistency is distinguishing which tags define the character's **identity** (always keep) vs. which describe the **scene** (freely change).

### Anchor tags (identity-defining)

These tags must remain identical across all prompts for the same character. They answer "who is this character?":

- **Hair**: color, length, style, bangs, sidelocks (e.g., `white_hair, long_hair, blunt_bangs`)
- **Eyes**: color, shape, eyelash style (e.g., `red_eyes, tsudere_eyes`)
- **Face/head**: any distinctive features (e.g., `ahoge, beauty_mark_under_eye`)
- **Body**: height, build, bust size, skin tone (e.g., `tall, slim, dark_skin`)
- **Markings**: scars, tattoos, birthmarks (e.g., `scar_on_cheek, tattoo_on_arm`)
- **Race/species**: if non-human (e.g., `elf, cat_girl, horns`)
- **Signature accessory**: the one item always worn (e.g., `eyepatch, hair_ribbon`)

Anchor tags form the character's "tag DNA" — they should appear in **every** positive prompt for that character.

### Variable tags (scene-dependent)

These change freely depending on the situation:

- **Expression**: mood of the moment
- **Action/pose**: what the character is doing
- **Clothing**: outfit of the day (except signature pieces)
- **Environment**: where they are
- **Composition**: camera framing, angle
- **Objects**: items relevant to the scene

### Generating a consistency profile

When the user asks to create a consistency profile for a character:

1. First build/gather the full tag set
2. Then classify each tag as **anchor** or **variable**
3. Output a two-part structure:

```markdown
## Anchor tags (always keep)
[comma-separated anchor tags]

## Variable tags (change as needed)
[comma-separated variable tags, grouped by category]

## Suggested negative prompt additions
[tags that should be negated to prevent character drift]
```

The negative prompt section is important — it prevents the model from "wandering" away from the character design. For example:
- If character has `short_hair`, neg: `long_hair, very_long_hair`
- If character has `flat_chest`, neg: `large_breasts, huge_breasts`
- If character is `solo`, neg: `multiple_girls, 1boy`

### Combining characters with a scene

When the user wants to place a character in a specific scene:

```
[all anchor tags], [scene-specific clothing if needed], [expression], [action], [environment], [composition]
```

Anchor tags always come first. Never remove anchor tags to "make room" for scene tags — that's how consistency breaks.

## Tips for tag quality

- **Be specific, not generic**: `sidelocks` > `hair`, `serafuku` > `school_uniform`, `scarlet_eyes` > `red_eyes`
- **Follow Danbooru conventions**: Use underscores, lowercase, singular forms. `blue_sky` not `blue skies`
- **No invented tags**: Every tag must exist in the dataset. Use the search script to verify
- **Avoid tag bloat**: 15-40 tags is the sweet spot for most characters. Over 60 and the model starts ignoring cues
- **Negative space matters**: What you exclude is as important as what you include. Use the negative prompt to reinforce anchor features by negating their opposites
- **Test silouette**: If you described the character's silhouette (hair outline + body shape + key accessory), would someone recognize them? If not, the anchor tags aren't distinctive enough

## Bundled resources

- `scripts/search_tags.py` — Search and browse the tag dataset. Always use this when you need to find or verify tags. Run it with `python3`.
- `references/tag_categories.md` — Detailed breakdown of every category and subcategory with example tags. Read this when you need to understand what each subcategory contains.
