#!/usr/bin/env python3
"""Search Danbooru tags by category, subcategory, or keyword.

Usage:
  python search_tags.py --category <name>            # all tags in a category
  python search_tags.py --subcategory <name>         # all tags in a subcategory
  python search_tags.py --keyword <term>             # fuzzy keyword search
  python search_tags.py --list-categories            # list all categories
  python search_tags.py --list-subcategories         # list all subcategories
  python search_tags.py --random --subcategory <name> --count 10  # random samples
  python search_tags.py --suggest <description>      # suggest tags from a text description
"""

import argparse
import csv
import os
import random
import sys
from pathlib import Path

# Default: tags_classified/ alongside the scripts/ directory (i.e. ../tags_classified)
_DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "tags_classified"
DATA_DIR = Path(os.environ.get("TAGS_DATA_DIR", _DEFAULT_DATA_DIR))

# Category config: filename -> (display_name, has_subcategory)
CATEGORIES = {
    "character":       ("人物本身的特征", "人物本身的特征_二级分类.csv", True),
    "expression":      ("表情",           "表情.csv",               False),
    "clothing":        ("服饰",           "服饰_二级分类.csv",       True),
    "action":          ("动作",           "动作.csv",               False),
    "environment":     ("环境/背景",      "环境_背景.csv",           False),
    "object":          ("物品",           "物品.csv",               False),
    "composition":     ("构图",           "构图.csv",               False),
    "other":           ("其他",           "其他.csv",               False),
}

_cache = {}


def load_tags(category_key):
    if category_key in _cache:
        return _cache[category_key]
    _, filename, has_sub = CATEGORIES[category_key]
    path = DATA_DIR / filename
    tags = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = row["tag"].strip()
            sub = row.get("subcategory", "").strip() if has_sub else ""
            tags[tag] = sub
    _cache[category_key] = (tags, has_sub)
    return tags, has_sub


def search_keyword(term, limit=50):
    results = []
    term_lower = term.lower()
    for key in CATEGORIES:
        tags, has_sub = load_tags(key)
        for tag, sub in tags.items():
            if term_lower in tag.lower():
                results.append((tag, sub, key))
                if len(results) >= limit:
                    return results
    return results


def search_subcategory(sub_name, limit=200):
    results = []
    for key in CATEGORIES:
        tags, has_sub = load_tags(key)
        if not has_sub:
            continue
        for tag, sub in tags.items():
            if sub_name in sub:
                results.append((tag, sub, key))
        if len(results) >= limit:
            return results
    return results


def list_categories():
    for key, (name, _, _) in CATEGORIES.items():
        tags, has_sub = load_tags(key)
        subs = set()
        if has_sub:
            subs = {s for s in tags.values() if s}
        print(f"{key} ({name}): {len(tags)} tags", end="")
        if subs:
            print(f", subcategories: {', '.join(sorted(subs))}")
        else:
            print()


def list_subcategories():
    seen = set()
    for key in CATEGORIES:
        tags, has_sub = load_tags(key)
        if has_sub:
            for sub in set(tags.values()):
                if sub and sub not in seen:
                    seen.add(sub)
                    count = sum(1 for s in tags.values() if s == sub)
                    print(f"{sub} [{key}]: {count} tags")


def suggest_tags(description, limit=30):
    """Simple keyword-based suggestion from a description."""
    words = description.lower().replace(",", " ").replace("，", " ").split()
    scored = {}
    for key in CATEGORIES:
        tags, has_sub = load_tags(key)
        for tag, sub in tags.items():
            tag_lower = tag.lower().replace("_", " ")
            score = 0
            for word in words:
                if word in tag_lower:
                    score += 1
                if word in sub:
                    score += 0.5
            if score > 0:
                scored[(tag, sub, key)] = score
    ranked = sorted(scored.items(), key=lambda x: -x[1])[:limit]
    return [(tag, sub, key, score) for (tag, sub, key), score in ranked]


def random_tags(subcategory=None, count=10):
    pool = []
    for key in CATEGORIES:
        tags, has_sub = load_tags(key)
        for tag, sub in tags.items():
            if subcategory is None or subcategory in sub:
                pool.append((tag, sub, key))
    return random.sample(pool, min(count, len(pool)))


def main():
    parser = argparse.ArgumentParser(description="Search Danbooru tags")
    parser.add_argument("--category", type=str, help="Category key to list all tags")
    parser.add_argument("--subcategory", type=str, help="Subcategory name to filter")
    parser.add_argument("--keyword", type=str, help="Keyword to search in tag names")
    parser.add_argument("--suggest", type=str, help="Natural language description to suggest tags")
    parser.add_argument("--list-categories", action="store_true")
    parser.add_argument("--list-subcategories", action="store_true")
    parser.add_argument("--random", action="store_true", help="Return random tags")
    parser.add_argument("--count", type=int, default=30, help="Max results (default 30)")
    parser.add_argument("--format", choices=["text", "csv", "comma"], default="text")
    args = parser.parse_args()

    if args.list_categories:
        list_categories()
        return

    if args.list_subcategories:
        list_subcategories()
        return

    if args.random:
        results = random_tags(args.subcategory, args.count)
    elif args.keyword:
        results = search_keyword(args.keyword, args.count)
    elif args.subcategory:
        results = search_subcategory(args.subcategory, args.count)
    elif args.category:
        tags, has_sub = load_tags(args.category)
        results = [(tag, sub, args.category) for tag, sub in tags.items()]
        if args.count:
            results = results[:args.count]
    elif args.suggest:
        results = suggest_tags(args.suggest, args.count)
    else:
        parser.print_help()
        return

    if args.format == "comma":
        print(", ".join(tag for tag, _, _ in results))
    elif args.format == "csv":
        writer = csv.writer(sys.stdout)
        for tag, sub, cat in results:
            score = results[0][3] if len(results[0]) > 3 else ""
            writer.writerow([tag, sub, cat, score])
    else:
        for row in results:
            tag, sub, cat = row[:3]
            score = f" ({row[3]:.0f})" if len(row) > 3 and row[3] else ""
            print(f"  {tag:<45} [{sub:<20}] ({cat}){score}")


if __name__ == "__main__":
    main()
