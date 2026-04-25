#!/usr/bin/env python3
"""Точка входа сборки `/docs-llm` из `/docs`.

Использование:
    python tools/docs-llm/build.py            # сборка + валидация
    python tools/docs-llm/build.py --check    # сравнение с existing /docs-llm

Запускается из корня pw_public.
"""

import argparse
import filecmp
import json
import os
import os.path
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import builder  # type: ignore  # noqa: E402
import validators  # type: ignore  # noqa: E402
from config import TopicsConfig  # type: ignore  # noqa: E402


def _project_paths(start: str) -> dict:
    """Находит корень pw_public по наличию /docs и /tools/docs-llm."""
    cur = os.path.abspath(start)
    while cur != os.path.dirname(cur):
        if os.path.isdir(os.path.join(cur, "docs")) and os.path.isdir(
            os.path.join(cur, "tools", "docs-llm")
        ):
            return {
                "root": cur,
                "docs": os.path.join(cur, "docs"),
                "docs_llm": os.path.join(cur, "docs-llm"),
                "tools": os.path.join(cur, "tools", "docs-llm"),
            }
        cur = os.path.dirname(cur)
    raise SystemExit(
        "Не найден корень pw_public (ожидаются /docs и /tools/docs-llm)."
    )


def _build_into(
    output_dir: str,
    docs_dir: str,
    tools_dir: str,
    repo_root: str,
):
    config = TopicsConfig.load(tools_dir)
    topics, anchor_index, uncovered = builder.build_topics(docs_dir, config)
    builder.resolve_links(topics, anchor_index)
    sha = builder.get_pw_public_sha(repo_root)
    summary = builder.write_outputs(topics, output_dir, sha)
    removed = builder.remove_orphan_topics(
        output_dir, [t["key"] for t in topics]
    )
    return topics, uncovered, summary, removed


def _print_summary(summary: dict, topics_count: int, removed: list, errors: list):
    print(f"  topics_count: {topics_count}")
    print(f"  bundle_size: {summary['bundle_size']} байт")
    print(f"  listing_size: {summary['listing_size']} chars")
    print(f"  build_timestamp: {summary['timestamp']}")
    if removed:
        print(f"  removed orphan topics: {len(removed)} ({', '.join(removed[:5])}{'...' if len(removed) > 5 else ''})")
    if errors:
        print()
        print("ERRORS:")
        for err in errors:
            print(f"  - {err}")


def _diff_dirs(a: str, b: str) -> list:
    """Возвращает список файлов, отличающихся между двумя директориями."""
    diff = filecmp.dircmp(a, b)
    differences = []
    for f in diff.left_only:
        differences.append(f"only in expected: {f}")
    for f in diff.right_only:
        differences.append(f"only in actual:   {f}")
    for f in diff.diff_files:
        differences.append(f"changed: {f}")
    for sub in diff.common_dirs:
        sub_diffs = _diff_dirs(os.path.join(a, sub), os.path.join(b, sub))
        differences.extend(f"{sub}/{d}" for d in sub_diffs)
    return differences


def main():
    parser = argparse.ArgumentParser(
        description="Сборка /docs-llm из /docs",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Сборка во временную директорию и сравнение с existing /docs-llm. "
        "Если расхождение или валидаторы падают — exit 1.",
    )
    parser.add_argument(
        "--output",
        help="Куда писать. По умолчанию <pw_public>/docs-llm. Игнорируется при --check.",
    )
    args = parser.parse_args()

    paths = _project_paths(os.getcwd())

    if args.check:
        with tempfile.TemporaryDirectory() as tmpdir:
            topics, uncovered, summary, removed = _build_into(
                output_dir=tmpdir,
                docs_dir=paths["docs"],
                tools_dir=paths["tools"],
                repo_root=paths["root"],
            )
            errors, _ = validators.run_all(
                topics, uncovered, summary["bundle_size"]
            )
            print(f"[check] сборка во временную директорию OK")
            _print_summary(summary, len(topics), removed, errors)
            if errors:
                return 1

            if not os.path.isdir(paths["docs_llm"]):
                print(
                    "[check] FAIL: /docs-llm не существует — "
                    "запустите `python tools/docs-llm/build.py` без --check"
                )
                return 1

            differences = _diff_dirs(paths["docs_llm"], tmpdir)
            differences = [
                d for d in differences
                if not d.endswith("README.md") and "build_timestamp" not in d
            ]
            differences_real = []
            for d in differences:
                if "changed:" in d:
                    fname = d.split("changed: ", 1)[1]
                    a_path = os.path.join(paths["docs_llm"], fname)
                    b_path = os.path.join(tmpdir, fname)
                    if _is_only_timestamp_diff(a_path, b_path):
                        continue
                differences_real.append(d)

            if differences_real:
                print()
                print("[check] FAIL: /docs-llm не соответствует /docs:")
                for diff in differences_real:
                    print(f"  - {diff}")
                print()
                print("Запустите `python tools/docs-llm/build.py` и закоммитьте изменения.")
                return 1

            print("[check] OK: /docs-llm соответствует /docs")
            return 0

    output_dir = args.output or paths["docs_llm"]
    topics, uncovered, summary, removed = _build_into(
        output_dir=output_dir,
        docs_dir=paths["docs"],
        tools_dir=paths["tools"],
        repo_root=paths["root"],
    )
    errors, _ = validators.run_all(topics, uncovered, summary["bundle_size"])
    print(f"Built into {output_dir}")
    _print_summary(summary, len(topics), removed, errors)
    return 1 if errors else 0


_NON_DETERMINISTIC_PREFIXES = (
    "# build_timestamp:",
    "# pw_public_commit_sha:",
)


def _is_only_timestamp_diff(path_a: str, path_b: str) -> bool:
    """Игнорирует расхождения в недетерминированных полях bundle.txt.

    bundle хранит build_timestamp и pw_public_commit_sha, которые меняются
    при каждой сборке (sha — после очередного коммита pw_public). Эти
    поля информационные, в проверку синхронизации /docs ↔ /docs-llm не
    входят.
    """
    if os.path.basename(path_a) != "bundle.txt":
        return False
    try:
        with open(path_a, "r", encoding="utf-8") as f:
            a_lines = f.read().splitlines()
        with open(path_b, "r", encoding="utf-8") as f:
            b_lines = f.read().splitlines()
    except OSError:
        return False
    if len(a_lines) != len(b_lines):
        return False
    for la, lb in zip(a_lines, b_lines):
        if la == lb:
            continue
        if la.startswith(_NON_DETERMINISTIC_PREFIXES) and lb.startswith(
            _NON_DETERMINISTIC_PREFIXES
        ):
            continue
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
