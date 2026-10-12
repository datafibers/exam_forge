#!/usr/bin/env python3
"""Validate question bank JSON and optional exam profile for integrity, schema, and quality gates."""
import argparse, collections, json, re, sys
from pathlib import Path

def validate(bank_path, profile_path=None):
    try:
        bank = json.loads(Path(bank_path).read_text(encoding='utf-8'))
    except Exception as e:
        print(f"ERROR: Cannot read or parse question bank JSON: {e}")
        return False
        
    if not isinstance(bank, list):
        print('ERROR: Question bank must be a top-level JSON array of objects.')
        return False

    ids = set()
    stems = set()
    errors = []
    warnings = []
    topics = collections.Counter()
    types_count = collections.Counter()
    diff_count = collections.Counter()
    concepts = set()
    variants = 0

    required_fields = [
        'id', 'topic', 'difficulty', 'en', 'zh',
        'choices_en', 'choices_zh', 'answer',
        'explanation_en', 'explanation_zh'
    ]

    for i, q in enumerate(bank):
        row_id = q.get('id', f'item_{i}')
        # Check required fields
        for f in required_fields:
            if f not in q:
                errors.append(f"[{row_id}] missing required field '{f}'")
        if any(f not in q for f in required_fields):
            continue

        # Check duplicate ID
        if q['id'] in ids:
            errors.append(f"[{row_id}] duplicate question ID")
        ids.add(q['id'])

        # Check duplicate English stem (normalized)
        stem = ' '.join(q['en'].lower().split())
        if stem in stems:
            errors.append(f"[{row_id}] duplicate or near-duplicate English question stem")
        stems.add(stem)

        # Check non-empty text fields and draft residues
        for k in ['en', 'zh', 'explanation_en', 'explanation_zh']:
            val = q[k]
            if not isinstance(val, str) or not val.strip():
                errors.append(f"[{row_id}] field '{k}' is empty or not a string")
            elif re.search(r'\b(TODO|Wait:|Draft:)\b', val, re.IGNORECASE):
                errors.append(f"[{row_id}] field '{k}' contains unreviewed draft markers ('{val[:40]}...')")

        # Check unclosed math delimiters
        for k in ['en', 'zh', 'explanation_en', 'explanation_zh']:
            text = q.get(k, '')
            if text.count(r'\(') != text.count(r'\)'):
                errors.append(f"[{row_id}] unclosed \\( ... \\) math delimiter in '{k}'")
            if text.count(r'\[') != text.count(r'\]'):
                errors.append(f"[{row_id}] unclosed \\[ ... \\] math delimiter in '{k}'")
            if text.count('$$') % 2 != 0:
                errors.append(f"[{row_id}] unclosed $$ ... $$ math block in '{k}'")

        # Question type handling
        qtype = q.get('type', 'single')
        if qtype not in ('single', 'multiple', 'boolean'):
            errors.append(f"[{row_id}] invalid type '{qtype}' (must be single, multiple, or boolean)")
        types_count[qtype] += 1

        # Check choices
        ch_en, ch_zh = q['choices_en'], q['choices_zh']
        if not isinstance(ch_en, list) or not isinstance(ch_zh, list):
            errors.append(f"[{row_id}] choices_en and choices_zh must be lists")
            continue
        if len(ch_en) != len(ch_zh):
            errors.append(f"[{row_id}] choices_en count ({len(ch_en)}) != choices_zh count ({len(ch_zh)})")
            continue
        if qtype == 'boolean' and len(ch_en) != 2:
            errors.append(f"[{row_id}] boolean question must have exactly 2 choices")
        elif qtype in ('single', 'multiple') and len(ch_en) < 2:
            errors.append(f"[{row_id}] question must have at least 2 choices")

        # Check duplicate choice text within question
        if len(set(x.strip().lower() for x in ch_en)) != len(ch_en):
            errors.append(f"[{row_id}] duplicate option text detected in choices_en")

        # Check answer format
        ans = q['answer']
        if qtype in ('single', 'boolean'):
            if not isinstance(ans, int) or ans < 0 or ans >= len(ch_en):
                errors.append(f"[{row_id}] single/boolean answer index ({ans}) out of bounds [0..{len(ch_en)-1}]")
        elif qtype == 'multiple':
            if not isinstance(ans, list) or len(ans) == 0:
                errors.append(f"[{row_id}] multiple-choice answer must be a non-empty list of indices")
            elif any(not isinstance(x, int) or x < 0 or x >= len(ch_en) for x in ans):
                errors.append(f"[{row_id}] multiple-choice answer indices {ans} out of bounds")
            elif len(set(ans)) != len(ans):
                errors.append(f"[{row_id}] duplicate indices in multiple-choice answer: {ans}")

        # Check difficulty
        if q['difficulty'] not in (1, 2, 3):
            errors.append(f"[{row_id}] invalid difficulty {q['difficulty']} (must be 1, 2, or 3)")
        diff_count[q['difficulty']] += 1

        # Check distractor explanations
        for dist_key in ('why_wrong_en', 'why_wrong_zh'):
            if dist_key in q and q[dist_key] is not None:
                if not isinstance(q[dist_key], list):
                    errors.append(f"[{row_id}] {dist_key} must be a list")
                elif len(q[dist_key]) != len(ch_en):
                    errors.append(f"[{row_id}] {dist_key} length ({len(q[dist_key])}) does not match choices count ({len(ch_en)})")

        topics[q['topic']] += 1
        concepts.add(q.get('concept_id', q['id']))
        if q.get('variant_of'):
            variants += 1

    # Optional Exam Profile verification
    profile_info = ""
    if profile_path:
        try:
            prof = json.loads(Path(profile_path).read_text(encoding='utf-8'))
            req_prof = ['exam_name', 'passing_score_pct', 'exam_duration_mins']
            for rf in req_prof:
                if rf not in prof:
                    errors.append(f"Exam profile missing required field '{rf}'")
            target_mock = prof.get('mock_questions_count', 100)
            if len(bank) < target_mock:
                warnings.append(f"Question bank ({len(bank)} items) is smaller than mock target ({target_mock} items). Mocks will reuse or scale.")
            
            verified = prof.get('verified_rules', False)
            verified_tag = "[Official Rules Verified]" if verified else "[Unofficial Practice Settings]"
            profile_info = f"\nProfile: {prof.get('exam_name')} {verified_tag}\nDuration: {prof.get('exam_duration_mins')}m | Benchmark: {prof.get('passing_score_pct')}%"
        except Exception as e:
            errors.append(f"Cannot load profile file {profile_path}: {e}")

    # Summary report
    print(f"=== Question Bank Validation Summary ===")
    print(f"Total Questions : {len(bank)}")
    print(f"Question Types  : {dict(types_count)}")
    print(f"Difficulties    : {dict(diff_count)}")
    print(f"Unique Concepts : {len(concepts)}")
    print(f"Marked Variants : {variants}")
    print(f"Topics Coverage : {dict(topics)}")
    if profile_info:
        print(profile_info)

    if warnings:
        print(f"\n[!] Warnings ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"  - {w}")

    if errors:
        print(f"\n[X] Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False

    print("\n[✓] Schema, logic, math delimiters, and translation checks passed successfully.")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate exam question bank and profile.")
    parser.add_argument('bank', help="Path to questions.json")
    parser.add_argument('--profile', help="Path to optional exam_profile.json", default=None)
    args = parser.parse_args()

    success = validate(args.bank, args.profile)
    sys.exit(0 if success else 1)
