#!/usr/bin/env python3
"""Inventory stray Human Design Engine operational files safely.

The scanner is intentionally conservative: it classifies candidates outside this
repository, checks exact-content duplicates against canonical repository files,
and searches cron/systemd-style runtime reference surfaces before anything can be
called safe to delete. Default mode is read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOTS = [
    Path('/home/ubuntu/work'),
    Path('/home/ubuntu/.hermes/profiles/ned/scripts'),
    Path('/home/ubuntu/.hermes/profiles/ned/cron'),
    Path('/tmp'),
]
CANONICAL_PREFIXES = [
    str(REPO_ROOT) + '/',
    '/home/ubuntu/work/hd-platform-staging/',
]
REFERENCE_ROOTS = [
    Path('/etc/cron.d'),
    Path('/etc/crontab'),
    Path('/var/spool/cron'),
    Path('/etc/systemd/system'),
    Path('/lib/systemd/system'),
    Path('/home/ubuntu/.config/systemd/user'),
    Path('/home/ubuntu/.hermes/profiles/ned/cron'),
    Path('/home/ubuntu/.hermes/profiles/ned/scripts'),
]
SKIP_PARTS = {'.git', 'node_modules', '.venv', 'dist', '__pycache__'}
TEXT_EXTS = {'.md', '.py', '.js', '.mjs', '.json', '.yaml', '.yml', '.txt', '.sh', '.html', '.log', '.out', '.service'}
TERMS = [
    'hde',
    'hd engine',
    'human design engine',
    'humandesignengine',
    'daily transit',
    'transit message',
    'hde-payment',
    'hde-reports',
]
SAFE_DELETE_PREFIXES = [
    '/tmp/',
    '/home/ubuntu/work/artifacts/',
]


@dataclass
class Candidate:
    path: str
    size: int | None
    sha256: str | None
    classification: str
    repo_duplicate_of: list[str]
    external_duplicate_group_size: int
    runtime_reference_hits: list[str]
    safe_delete_candidate: bool
    action: str


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def is_canonical(path: Path) -> bool:
    sp = str(path)
    return any(sp.startswith(prefix) for prefix in CANONICAL_PREFIXES)


def is_probably_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTS


def read_text_prefix(path: Path, limit: int = 50_000) -> str:
    try:
        return path.read_text(errors='ignore')[:limit]
    except Exception:
        return ''


def text_hit(path: Path) -> bool:
    name = path.name.lower().replace(' ', '')
    compact_terms = [term.replace(' ', '') for term in TERMS]
    if any(term in name for term in compact_terms):
        return True
    if not is_probably_text(path):
        return False
    txt = read_text_prefix(path).lower()
    return any(term in txt for term in TERMS)


def classify(path: Path) -> str:
    sp = str(path)
    if sp.startswith('/tmp/'):
        return 'tmp-evidence-or-log'
    if '/.hermes/profiles/ned/scripts/' in sp:
        return 'active-profile-script-candidate-copy-to-repo'
    if '/.hermes/profiles/ned/cron/' in sp:
        return 'runtime-cron-output-summarize-not-commit'
    if sp.endswith('.bundle'):
        return 'git-bundle-or-checkpoint-archive'
    if '/hd-reports/' in sp:
        return 'legacy-hde-research-candidate-import'
    return 'review'


def iter_files(roots: Iterable[Path], limit: int | None) -> Iterable[Path]:
    seen = 0
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            files = [root]
        else:
            files = root.rglob('*')
        for path in files:
            if limit is not None and seen >= limit:
                return
            if path.is_dir() and should_skip(path):
                continue
            if not path.is_file() or should_skip(path) or is_canonical(path):
                continue
            seen += 1
            yield path


def sha256(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open('rb') as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def canonical_hash_index() -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for path in REPO_ROOT.rglob('*'):
        if not path.is_file() or should_skip(path):
            continue
        digest = sha256(path)
        if digest:
            index[digest].append(str(path.relative_to(REPO_ROOT)))
    return dict(index)


def load_reference_corpus(extra_roots: Iterable[Path]) -> dict[str, str]:
    corpus: dict[str, str] = {}
    for root in list(REFERENCE_ROOTS) + list(extra_roots):
        if not root.exists():
            continue
        paths = [root] if root.is_file() else root.rglob('*')
        for path in paths:
            if not path.is_file() or should_skip(path) or not is_probably_text(path):
                continue
            text = read_text_prefix(path, limit=250_000)
            if text:
                corpus[str(path)] = text
    return corpus


def reference_hits(path: Path, corpus: dict[str, str]) -> list[str]:
    sp = str(path)
    name = path.name
    hits = []
    for ref_path, text in corpus.items():
        if sp in text or name in text:
            hits.append(ref_path)
    return sorted(set(hits))


def action_for(path: Path, classification: str, repo_dupes: list[str], refs: list[str]) -> tuple[bool, str]:
    sp = str(path)
    safe_prefix = any(sp.startswith(prefix) for prefix in SAFE_DELETE_PREFIXES)
    if repo_dupes and not refs and safe_prefix:
        return True, 'safe-delete-after-human-review: exact repo duplicate, no runtime references, safe prefix'
    if repo_dupes and refs:
        return False, 'keep: exact repo duplicate but referenced by runtime surface'
    if repo_dupes:
        return False, 'keep: exact repo duplicate outside approved safe-delete prefixes'
    if classification == 'runtime-cron-output-summarize-not-commit':
        return False, 'summarize only: runtime cron output'
    if classification == 'active-profile-script-candidate-copy-to-repo':
        return False, 'copy/port source first, then repoint cron/systemd in a separate verified change'
    if classification == 'legacy-hde-research-candidate-import':
        return False, 'import durable findings only; do not delete source research in this pass'
    if classification == 'git-bundle-or-checkpoint-archive':
        return False, 'keep archive until branch/content is verified'
    return False, 'review: no exact canonical duplicate proven'


def build_report(paths: list[Path], extra_reference_roots: list[Path]) -> dict:
    repo_index = canonical_hash_index()
    ref_corpus = load_reference_corpus(extra_reference_roots)
    path_hashes = {path: sha256(path) for path in paths}
    external_groups: dict[str, list[str]] = defaultdict(list)
    for path, digest in path_hashes.items():
        if digest:
            external_groups[digest].append(str(path))

    candidates: list[Candidate] = []
    for path in sorted(paths, key=lambda p: str(p)):
        digest = path_hashes[path]
        repo_dupes = sorted(repo_index.get(digest or '', [])) if digest else []
        refs = reference_hits(path, ref_corpus)
        classification = classify(path)
        safe_delete, action = action_for(path, classification, repo_dupes, refs)
        try:
            size = path.stat().st_size
        except OSError:
            size = None
        candidates.append(Candidate(
            path=str(path),
            size=size,
            sha256=digest,
            classification=classification,
            repo_duplicate_of=repo_dupes,
            external_duplicate_group_size=len(external_groups.get(digest or '', [])) if digest else 0,
            runtime_reference_hits=refs,
            safe_delete_candidate=safe_delete,
            action=action,
        ))

    counts = Counter(c.classification for c in candidates)
    return {
        'repo_root': str(REPO_ROOT),
        'candidate_count': len(candidates),
        'counts_by_classification': dict(sorted(counts.items())),
        'safe_delete_candidate_count': sum(1 for c in candidates if c.safe_delete_candidate),
        'reference_surface_count': len(ref_corpus),
        'candidates': [asdict(c) for c in candidates],
    }


def emit_markdown(report: dict) -> str:
    lines = [
        '# HDE Operational Duplicate Safety Report',
        '',
        f"- Repo root: `{report['repo_root']}`",
        f"- Candidates: **{report['candidate_count']}**",
        f"- Runtime reference files inspected: **{report['reference_surface_count']}**",
        f"- Safe-delete candidates: **{report['safe_delete_candidate_count']}**",
        '',
        '## Counts by classification',
        '',
        '| Classification | Count |',
        '|---|---:|',
    ]
    for key, value in report['counts_by_classification'].items():
        lines.append(f'| `{key}` | {value} |')
    lines.extend(['', '## Candidate decisions', '', '| Action | Class | Path | Evidence |', '|---|---|---|---|'])
    for row in report['candidates']:
        evidence = []
        if row['repo_duplicate_of']:
            evidence.append('repo duplicate: ' + ', '.join(f"`{p}`" for p in row['repo_duplicate_of'][:3]))
        if row['runtime_reference_hits']:
            evidence.append('runtime refs: ' + ', '.join(f"`{p}`" for p in row['runtime_reference_hits'][:3]))
        if row['external_duplicate_group_size'] > 1:
            evidence.append(f"external duplicate group size: {row['external_duplicate_group_size']}")
        evidence.append(row['action'])
        lines.append(
            f"| {'SAFE DELETE' if row['safe_delete_candidate'] else 'KEEP/REVIEW'} "
            f"| `{row['classification']}` | `{row['path']}` | {'; '.join(evidence)} |"
        )
    lines.append('')
    return '\n'.join(lines)


def delete_safe_candidates(report: dict) -> list[str]:
    deleted = []
    for row in report['candidates']:
        if not row['safe_delete_candidate']:
            continue
        path = Path(row['path'])
        if path.exists() and path.is_file():
            path.unlink()
            deleted.append(str(path))
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', action='append', help='Root to scan; may be repeated')
    parser.add_argument('--reference-root', action='append', default=[], help='Extra cron/systemd/reference root to inspect')
    parser.add_argument('--limit', type=int, default=None, help='Max files to inspect before content filtering')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    parser.add_argument('--delete-safe', action='store_true', help='Delete only exact repo duplicates under approved safe prefixes with zero runtime references')
    args = parser.parse_args()

    roots = [Path(p) for p in args.root] if args.root else DEFAULT_ROOTS
    paths = [path for path in iter_files(roots, args.limit) if text_hit(path)]
    report = build_report(paths, [Path(p) for p in args.reference_root])
    if args.delete_safe:
        report['deleted'] = delete_safe_candidates(report)

    if args.format == 'markdown':
        print(emit_markdown(report))
    else:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
