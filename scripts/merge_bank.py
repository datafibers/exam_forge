#!/usr/bin/env python3
"""Merge multiple question bank JSON files (or batch fragments) into a single deduplicated, validated bank."""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_bank import normalize_question, validate


def merge_banks(input_paths, output_path, profile_path=None, deduplicate=True):
    merged = []
    seen_ids = set()
    seen_stems = set()
    skipped_dups = 0

    for p in input_paths:
        path = Path(p)
        if not path.exists():
            print(f"ERROR: Input file not found: {path}")
            return False
        try:
            items = json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"ERROR: Failed to parse JSON from {path}: {e}")
            return False

        if not isinstance(items, list):
            print(f"ERROR: {path} must contain a top-level JSON array of question objects.")
            return False

        for raw_q in items:
            if not isinstance(raw_q, dict):
                continue
            q = normalize_question(raw_q)
            qid = q.get('id', '')
            stem = ' '.join(str(q.get('en', '')).lower().split())

            if deduplicate and (qid in seen_ids or (stem and stem in seen_stems)):
                skipped_dups += 1
                continue

            if qid:
                seen_ids.add(qid)
            if stem:
                seen_stems.add(stem)
            merged.append(raw_q)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Merged {len(merged)} questions from {len(input_paths)} file(s) into {out} (skipped {skipped_dups} duplicate(s)).\n")

    return validate(out, profile_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Merge multiple batch question JSON files into a unified question bank and run validation."
    )
    parser.add_argument('inputs', nargs='+', help="Input JSON batch files (or existing questions.json + new batch)")
    parser.add_argument('--out', '-o', required=True, help="Output merged questions.json path")
    parser.add_argument('--profile', help="Optional exam_profile.json to validate against", default=None)
    parser.add_argument('--no-dedup', action='store_true', help="Disable automatic ID/stem deduplication")
    args = parser.parse_args()

    ok = merge_banks(args.inputs, args.out, args.profile, deduplicate=not args.no_dedup)
    sys.exit(0 if ok else 1)
