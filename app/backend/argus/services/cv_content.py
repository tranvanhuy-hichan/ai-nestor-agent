"""Keep submitted CV records when an LLM omits entries or over-summarizes them."""
import copy
import json
import re

ARRAYS = {'experience', 'education', 'skills', 'languages', 'projects', 'highlights'}
SECTIONS = ARRAYS | {'summary', 'awards', 'interests'}
IDENTITY = {'experience': ('role', 'company'), 'education': ('school', 'degree'), 'skills': ('name',), 'languages': ('name',), 'projects': ('name',), 'highlights': ('value', 'label')}


def profile_from_messages(messages):
    """Read user-authored form data, not model/tool-generated CVs, even after context compaction."""
    decoder = json.JSONDecoder()
    for message in reversed(messages):
        if message.get('role') != 'user':
            continue
        for line in reversed(message.get('content', '').splitlines()):
            if not line.startswith('- ') or '{' not in line:
                continue
            try:
                p, _ = decoder.raw_decode(line[line.index('{'):])
            except (ValueError, TypeError):
                continue
            if isinstance(p, dict) and isinstance(p.get('template'), str) and isinstance(p.get('data'), dict) and isinstance(p.get('skipped_sections'), list):
                return p
    return None


class IncompleteCvError(ValueError):
    """Ask the agent to finish its edit instead of silently printing raw source text."""


def _text(original, edited, path, issues):
    if not isinstance(original, str) or not original.strip():
        return edited if isinstance(edited, str) else original
    facts = re.findall(r'https?://\S+|\d+(?:[.,:/%-]\d+)*%?', original)
    if not isinstance(edited, str) or not edited.strip():
        issues.append(path + ': thiếu nội dung biên tập')
        return original
    if any(f not in edited for f in facts):
        issues.append(path + ': thiếu số liệu hoặc liên kết gốc')
    # Wording may legitimately be shorter; character count cannot measure meaning.
    return edited


def preserve_profile(profile, edited):
    original = profile['data']
    result = copy.deepcopy(original)
    restored = []
    skipped = set(profile['skipped_sections'])
    for key in ('summary', 'awards', 'interests'):
        if key not in skipped and (key in original or key == 'summary'):
            result[key] = _text(original.get(key, ''), edited.get(key), key, restored)
    for section in ARRAYS:
        if section in skipped:
            result[section] = []
            continue
        rows = original.get(section)
        if not isinstance(rows, list):
            # Form is the source of truth; do not invent new records in an empty section.
            result[section] = []
            continue
        candidates = [x for x in edited.get(section, []) if isinstance(x, dict)] if isinstance(edited.get(section), list) else []
        merged, used = [], set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            match = next((i for i, c in enumerate(candidates) if i not in used and row.get('id') and c.get('id') == row['id']), None)
            if match is None:
                fields = IDENTITY[section]
                match = next((i for i, c in enumerate(candidates) if i not in used and all(str(c.get(k, '')).strip().casefold() == str(row.get(k, '')).strip().casefold() for k in fields)), None)
            entry = copy.deepcopy(row)
            if match is None:
                if len(candidates) == len(rows) and index not in used and not candidates[index].get('id'):
                    match = index
                else:
                    restored.append(f'{section}[{index + 1}]: thiếu bản biên tập, giữ đúng ID gốc')
            if match is not None:
                used.add(match)
                candidate = candidates[match]
                # Names, dates, links and numeric claims remain exactly as submitted.
                if section == 'skills':
                    entry['name'] = _text(row.get('name', ''), candidate.get('name'), f'{section}[{index + 1}].name', restored)
                if 'desc' in row:
                    entry['desc'] = _text(row['desc'], candidate.get('desc'), f'{section}[{index + 1}].desc', restored)
            merged.append(entry)
        result[section] = merged
    for key in skipped:
        if key in SECTIONS:
            result[key] = [] if key in ARRAYS else ''
    if restored:
        raise IncompleteCvError("CV chưa đủ nội dung biên tập: " + "; ".join(restored) + ". CHƯA xuất file. Đọc lại đầy đủ form, viết lại từng mục với đúng ID và giữ đủ ý, số liệu, liên kết. Không chép nguyên văn để né lỗi; không bỏ mục hoặc tự rút gọn.")
    return result, []
