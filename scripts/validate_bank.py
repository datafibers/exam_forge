#!/usr/bin/env python3
"""Validate question bank JSON and optional exam profile for integrity, schema, and quality gates."""
import argparse, collections, copy, json, re, sys
from pathlib import Path


def difficulty_ok(q):
    return q.get('difficulty') in (1, 2, 3)


def normalize_question(raw_q):
    """Return a normalized copy of a question with single-language fallbacks applied."""
    q = copy.deepcopy(raw_q)
    qtype = q.get('type', 'single')
    q['type'] = qtype

    # Stem fallback (en <-> zh)
    en_stem = (q.get('en') or '').strip() if isinstance(q.get('en'), str) else ''
    zh_stem = (q.get('zh') or '').strip() if isinstance(q.get('zh'), str) else ''
    if en_stem and not zh_stem:
        q['zh'] = q['en']
    elif zh_stem and not en_stem:
        q['en'] = q['zh']

    # Explanation fallback
    en_exp = (q.get('explanation_en') or '').strip() if isinstance(q.get('explanation_en'), str) else ''
    zh_exp = (q.get('explanation_zh') or '').strip() if isinstance(q.get('explanation_zh'), str) else ''
    if en_exp and not zh_exp:
        q['explanation_zh'] = q['explanation_en']
    elif zh_exp and not en_exp:
        q['explanation_en'] = q['explanation_zh']

    # Choices & distractor fallback for choice-based types
    if qtype in ('single', 'multiple', 'boolean'):
        ch_en = q.get('choices_en')
        ch_zh = q.get('choices_zh')
        if isinstance(ch_en, list) and not isinstance(ch_zh, list):
            q['choices_zh'] = list(ch_en)
        elif isinstance(ch_zh, list) and not isinstance(ch_en, list):
            q['choices_en'] = list(ch_zh)

        ww_en = q.get('why_wrong_en')
        ww_zh = q.get('why_wrong_zh')
        if isinstance(ww_en, list) and not isinstance(ww_zh, list):
            q['why_wrong_zh'] = list(ww_en)
        elif isinstance(ww_zh, list) and not isinstance(ww_en, list):
            q['why_wrong_en'] = list(ww_zh)

    # Short-answer & Fill-in fallback
    if qtype == 'short':
        if 'answer' in q and isinstance(q['answer'], str):
            q.setdefault('answer_en', q['answer'])
            q.setdefault('answer_zh', q['answer'])
        a_en = (q.get('answer_en') or '').strip() if isinstance(q.get('answer_en'), str) else ''
        a_zh = (q.get('answer_zh') or '').strip() if isinstance(q.get('answer_zh'), str) else ''
        if a_en and not a_zh:
            q['answer_zh'] = q['answer_en']
        elif a_zh and not a_en:
            q['answer_en'] = q['answer_zh']

        r_en = q.get('rubric_en')
        r_zh = q.get('rubric_zh')
        if isinstance(r_en, list) and not isinstance(r_zh, list):
            q['rubric_zh'] = list(r_en)
        elif isinstance(r_zh, list) and not isinstance(r_en, list):
            q['rubric_en'] = list(r_zh)

    elif qtype == 'fill':
        # Fill-in-the-blank can specify `answer` (number, string, or list of accepted values)
        # or `answer_en` / `answer_zh`
        if 'answer' not in q:
            if 'answer_en' in q:
                q['answer'] = q['answer_en']
            elif 'answer_zh' in q:
                q['answer'] = q['answer_zh']

    return q


def validate(bank_path, profile_path=None):
    try:
        raw_bank = json.loads(Path(bank_path).read_text(encoding='utf-8'))
    except Exception as e:
        print(f"ERROR: Cannot read or parse question bank JSON: {e}")
        return False

    if not isinstance(raw_bank, list):
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
    single_lang_count = 0

    for i, raw_q in enumerate(raw_bank):
        row_id = raw_q.get('id', f'item_{i}')
        if not isinstance(raw_q, dict):
            errors.append(f"[{row_id}] question entry must be a JSON object")
            continue

        # Detect single-language fallback usage
        has_en = bool(isinstance(raw_q.get('en'), str) and raw_q.get('en').strip())
        has_zh = bool(isinstance(raw_q.get('zh'), str) and raw_q.get('zh').strip())
        if has_en != has_zh:
            single_lang_count += 1

        q = normalize_question(raw_q)
        qtype = q.get('type', 'single')

        base_req = ['id', 'topic', 'difficulty', 'en', 'zh', 'explanation_en', 'explanation_zh']
        if qtype == 'short':
            req = base_req + ['answer_en', 'answer_zh']
        elif qtype == 'fill':
            req = base_req + ['answer']
        else:
            req = base_req + ['choices_en', 'choices_zh', 'answer']

        for f in req:
            if f not in q:
                errors.append(f"[{row_id}] missing required field '{f}'")
        if any(f not in q for f in req):
            continue

        # Check duplicate ID
        if q['id'] in ids:
            errors.append(f"[{row_id}] duplicate question ID")
        ids.add(q['id'])

        # Check duplicate stem (normalized)
        stem = ' '.join(str(q['en']).lower().split())
        if stem in stems:
            errors.append(f"[{row_id}] duplicate or near-duplicate question stem")
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
        if qtype not in ('single', 'multiple', 'boolean', 'fill', 'short'):
            errors.append(f"[{row_id}] invalid type '{qtype}' (must be single, multiple, boolean, fill, or short)")
        types_count[qtype] += 1

        # Difficulty & metadata tracking
        if difficulty_ok(q):
            diff_count[q['difficulty']] += 1
        else:
            errors.append(f"[{row_id}] invalid difficulty {q.get('difficulty')} (must be 1, 2, or 3)")
        topics[q['topic']] += 1
        concepts.add(q.get('concept_id', q['id']))
        if q.get('variant_of'):
            variants += 1

        if qtype == 'short':
            for k in ('answer_en', 'answer_zh'):
                if not isinstance(q[k], str) or not q[k].strip():
                    errors.append(f"[{row_id}] field '{k}' is empty or not a string")
            for k in ('rubric_en', 'rubric_zh'):
                if k in q and (not isinstance(q[k], list) or not all(isinstance(x, str) and x.strip() for x in q[k])):
                    errors.append(f"[{row_id}] {k} must be a list of non-empty strings")
            if 'choices_en' in q or 'choices_zh' in q:
                warnings.append(f"[{row_id}] short-answer question ignores choices_en/choices_zh")
            continue

        if qtype == 'fill':
            ans = q['answer']
            valid_ans = False
            if isinstance(ans, (int, float)) and not isinstance(ans, bool):
                valid_ans = True
            elif isinstance(ans, str) and ans.strip():
                valid_ans = True
            elif isinstance(ans, list) and len(ans) > 0 and all(
                (isinstance(x, (int, float)) and not isinstance(x, bool)) or (isinstance(x, str) and x.strip())
                for x in ans
            ):
                valid_ans = True
            if not valid_ans:
                errors.append(f"[{row_id}] fill-in answer must be a non-empty string, number, or list of accepted strings/numbers")
            if 'tolerance' in q and q['tolerance'] is not None:
                tol = q['tolerance']
                if not isinstance(tol, (int, float)) or isinstance(tol, bool) or tol < 0:
                    errors.append(f"[{row_id}] fill-in tolerance must be a non-negative number")
            continue

        # Choice-based questions ('single', 'multiple', 'boolean')
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
        if len(set(str(x).strip().lower() for x in ch_en)) != len(ch_en):
            errors.append(f"[{row_id}] duplicate option text detected in choices_en")

        # Check answer format
        ans = q['answer']
        if qtype in ('single', 'boolean'):
            if not isinstance(ans, int) or isinstance(ans, bool) or ans < 0 or ans >= len(ch_en):
                errors.append(f"[{row_id}] single/boolean answer index ({ans}) out of bounds [0..{len(ch_en)-1}]")
        elif qtype == 'multiple':
            if not isinstance(ans, list) or len(ans) == 0:
                errors.append(f"[{row_id}] multiple-choice answer must be a non-empty list of indices")
            elif any(not isinstance(x, int) or isinstance(x, bool) or x < 0 or x >= len(ch_en) for x in ans):
                errors.append(f"[{row_id}] multiple-choice answer indices {ans} out of bounds")
            elif len(set(ans)) != len(ans):
                errors.append(f"[{row_id}] duplicate indices in multiple-choice answer: {ans}")

        # Check distractor explanations
        for dist_key in ('why_wrong_en', 'why_wrong_zh'):
            if dist_key in q and q[dist_key] is not None:
                if not isinstance(q[dist_key], list):
                    errors.append(f"[{row_id}] {dist_key} must be a list")
                elif len(q[dist_key]) != len(ch_en):
                    errors.append(f"[{row_id}] {dist_key} length ({len(q[dist_key])}) does not match choices count ({len(ch_en)})")

    if single_lang_count > 0:
        warnings.append(f"{single_lang_count} item(s) provided single-language text; auto-fallback to the other language will be applied.")

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
            if len(raw_bank) < target_mock:
                warnings.append(f"Question bank ({len(raw_bank)} items) is smaller than mock target ({target_mock} items). Mocks will reuse or scale.")

            # Validate domain_weights if specified
            dw = prof.get('domain_weights')
            weight_summary = ""
            if dw is not None:
                if not isinstance(dw, dict) or not dw:
                    errors.append("Exam profile 'domain_weights' must be a non-empty object mapping topic names to numeric weights.")
                else:
                    total_w = 0.0
                    weight_parts = []
                    for dom, w in dw.items():
                        if not isinstance(w, (int, float)) or isinstance(w, bool) or w <= 0:
                            errors.append(f"Invalid weight '{w}' for domain '{dom}' in domain_weights (must be > 0)")
                        else:
                            total_w += w
                            cnt = topics.get(dom, 0)
                            if cnt == 0:
                                warnings.append(f"Syllabus domain '{dom}' (weight {w}%) has 0 questions in the bank.")
                            actual_pct = round(cnt / max(1, len(raw_bank)) * 100)
                            weight_parts.append(f"{dom}: target {w}% / actual {actual_pct}% ({cnt})")
                    weight_summary = "\nSyllabus Weights: " + " | ".join(weight_parts)

            verified = prof.get('verified_rules', False)
            verified_tag = "[Official Rules Verified]" if verified else "[Unofficial Practice Settings]"
            profile_info = (
                f"\nProfile: {prof.get('exam_name')} {verified_tag}"
                f"\nDuration: {prof.get('exam_duration_mins')}m | Benchmark: {prof.get('passing_score_pct')}%"
                f"{weight_summary}"
            )
        except Exception as e:
            errors.append(f"Cannot load profile file {profile_path}: {e}")

    # Summary report
    print(f"=== Question Bank Validation Summary ===")
    print(f"Total Questions : {len(raw_bank)}")
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
