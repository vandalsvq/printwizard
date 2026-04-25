"""Загрузка конфигурации сборки.

`topics.json` — explicit-mapping `file_relative_to_docs → {prefix, ...}`
`excluded.json` — список путей или директорий, не входящих в индекс.
"""

import fnmatch
import json
import os.path
from typing import Dict, List, Optional


class TopicsConfig:
    """Конфигурация сборки.

    fields:
        topics — dict file → {prefix, exclude_h2, override}
        excluded — список путей-префиксов, исключённых из индекса
    """

    def __init__(self, topics: Dict[str, dict], excluded: List[str]):
        self.topics = topics
        self.excluded = excluded

    @classmethod
    def load(cls, tools_dir: str) -> "TopicsConfig":
        topics_path = os.path.join(tools_dir, "topics.json")
        excluded_path = os.path.join(tools_dir, "excluded.json")
        with open(topics_path, "r", encoding="utf-8") as f:
            topics = json.load(f)
        with open(excluded_path, "r", encoding="utf-8") as f:
            excluded = json.load(f)
        return cls(topics=topics, excluded=excluded)

    def is_excluded(self, file_rel: str) -> bool:
        for pattern in self.excluded:
            if file_rel == pattern:
                return True
            if pattern.endswith("/") and file_rel.startswith(pattern):
                return True
            if any(ch in pattern for ch in "*?[") and fnmatch.fnmatch(
                file_rel, pattern
            ):
                return True
        return False

    def file_settings(self, file_rel: str) -> Optional[dict]:
        return self.topics.get(file_rel)
