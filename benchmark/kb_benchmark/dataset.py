"""
数据集管理 — 问答数据集的加载、验证和生成。

数据集格式 (JSONL):
{
    "id": "CU-001",
    "category": "code_understanding" | "code_generation" | "problem_solving",
    "subcategory": "function_explanation" | "module_relation" | "bug_localization" | ...
    "difficulty": "easy" | "medium" | "hard",
    "question": "问题描述",
    "reference_answer": "参考答案（ground truth）",
    "files_involved": ["path/to/file.py"],
    "scoring_rubric": {
        "completeness": {"max": 5, "description": "答案完整性"},
        "accuracy": {"max": 5, "description": "答案准确性"},
        "depth": {"max": 5, "description": "分析深度"}
    },
    "tags": ["django", "orm", "queryset"]
}
"""

import json
import os
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Question:
    id: str
    category: str
    subcategory: str
    difficulty: str
    question: str
    reference_answer: str
    files_involved: List[str]
    scoring_rubric: Dict[str, Any]
    tags: List[str] = field(default_factory=list)


class QuestionDataset:
    """问答数据集管理器"""

    def __init__(self, dataset_dir: str):
        self.dataset_dir = Path(dataset_dir)
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self.questions: List[Question] = []
        self.metadata: Dict[str, Any] = {}

    def load(self, filename: str = "questions.jsonl") -> List[Question]:
        """加载 JSONL 格式的问答数据集"""
        filepath = self.dataset_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Dataset not found: {filepath}")

        self.questions = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                self.questions.append(Question(
                    id=data["id"],
                    category=data["category"],
                    subcategory=data["subcategory"],
                    difficulty=data["difficulty"],
                    question=data["question"],
                    reference_answer=data["reference_answer"],
                    files_involved=data.get("files_involved", []),
                    scoring_rubric=data.get("scoring_rubric", {}),
                    tags=data.get("tags", []),
                ))

        # Load metadata
        meta_path = self.dataset_dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)

        return self.questions

    def save(self, filename: str = "questions.jsonl"):
        """保存问答数据集"""
        filepath = self.dataset_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for q in self.questions:
                f.write(json.dumps(asdict(q), ensure_ascii=False) + '\n')

    def save_metadata(self):
        """保存元数据"""
        meta = {
            "version": "1.0.0",
            "total_questions": len(self.questions),
            "categories": self._count_by("category"),
            "difficulties": self._count_by("difficulty"),
            "codebase": self.metadata.get("codebase", {}),
            "hash": self._compute_hash(),
        }
        with open(self.dataset_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        self.metadata = meta

    def validate(self) -> Dict[str, Any]:
        """验证数据集完整性"""
        issues = []
        stats = {
            "total": len(self.questions),
            "by_category": {},
            "by_difficulty": {},
            "missing_fields": 0,
            "empty_answers": 0,
        }

        required_fields = ["id", "category", "difficulty", "question", "reference_answer"]

        for q in self.questions:
            # Count by category
            stats["by_category"][q.category] = stats["by_category"].get(q.category, 0) + 1
            stats["by_difficulty"][q.difficulty] = stats["by_difficulty"].get(q.difficulty, 0) + 1

            # Check required fields
            for field_name in required_fields:
                val = getattr(q, field_name, None)
                if not val:
                    issues.append(f"Question {q.id}: missing {field_name}")
                    stats["missing_fields"] += 1

            if not q.reference_answer or len(q.reference_answer.strip()) < 10:
                stats["empty_answers"] += 1

        return {"issues": issues, "stats": stats, "valid": len(issues) == 0}

    def filter(self, category: str = None, difficulty: str = None, tags: List[str] = None) -> List[Question]:
        """按条件筛选题目"""
        result = self.questions
        if category:
            result = [q for q in result if q.category == category]
        if difficulty:
            result = [q for q in result if q.difficulty == difficulty]
        if tags:
            result = [q for q in result if any(t in q.tags for t in tags)]
        return result

    def _count_by(self, field_name: str) -> Dict[str, int]:
        counts = {}
        for q in self.questions:
            val = getattr(q, field_name, "unknown")
            counts[val] = counts.get(val, 0) + 1
        return counts

    def _compute_hash(self) -> str:
        content = "".join(q.id + q.question for q in sorted(self.questions, key=lambda x: x.id))
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def summary(self) -> str:
        """生成数据集摘要"""
        if not self.questions:
            return "Empty dataset"

        cats = self._count_by("category")
        diffs = self._count_by("difficulty")
        lines = [
            f"📊 Dataset Summary",
            f"   Total Questions: {len(self.questions)}",
            f"   Categories: {json.dumps(cats)}",
            f"   Difficulties: {json.dumps(diffs)}",
        ]
        return "\n".join(lines)
