"""
指标体系 — 定义和计算所有评测指标。

四大核心指标:
1. 构建效率 (Build Efficiency) — 构建知识库的时间和资源消耗
2. 回答准确性 (Answer Accuracy) — AI 回答与参考答案的匹配度 [核心指标]
3. 回答效率 (Answer Efficiency) — 回答问题所需的时间和交互轮次
4. Token 效率 (Token Efficiency) — Token 消耗量与效果比值
"""

import time
import json
import hashlib
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class BuildMetrics:
    """知识库构建效率指标"""
    tool_name: str
    build_time_seconds: float = 0.0
    build_memory_mb: float = 0.0
    output_size_bytes: int = 0
    files_processed: int = 0
    lines_processed: int = 0
    errors_encountered: int = 0
    success: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def throughput_lines_per_sec(self) -> float:
        if self.build_time_seconds <= 0:
            return 0
        return self.lines_processed / self.build_time_seconds

    @property
    def compression_ratio(self) -> float:
        if self.lines_processed <= 0:
            return 0
        return self.output_size_bytes / (self.lines_processed * 50)  # ~50 bytes per line avg


@dataclass
class AnswerMetrics:
    """单题回答评估指标"""
    question_id: str
    answer: str = ""
    reference_answer: str = ""
    scores: Dict[str, float] = field(default_factory=dict)  # completeness, accuracy, depth
    total_score: float = 0.0
    max_score: float = 15.0
    response_time_seconds: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_total: int = 0
    interaction_rounds: int = 1
    correct_files_referenced: int = 0
    total_files_involved: int = 0
    error: Optional[str] = None

    @property
    def accuracy_rate(self) -> float:
        if self.max_score <= 0:
            return 0
        return self.total_score / self.max_score

    @property
    def tokens_per_score(self) -> float:
        if self.total_score <= 0:
            return float('inf')
        return self.tokens_total / self.total_score


@dataclass
class BenchmarkResult:
    """单次 Benchmark 完整结果"""
    tool_name: str
    codebase_name: str
    timestamp: str = ""
    build_metrics: BuildMetrics = None
    answer_metrics: List[AnswerMetrics] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

    # Aggregated metrics
    avg_accuracy: float = 0.0
    avg_response_time: float = 0.0
    avg_tokens: float = 0.0
    avg_score_per_token: float = 0.0
    total_build_time: float = 0.0
    questions_answered: int = 0
    questions_correct: int = 0  # score >= 80% max

    def aggregate(self):
        """计算聚合指标"""
        if not self.answer_metrics:
            return

        valid = [m for m in self.answer_metrics if m.error is None]
        if not valid:
            return

        self.questions_answered = len(valid)
        self.avg_accuracy = sum(m.accuracy_rate for m in valid) / len(valid)
        self.avg_response_time = sum(m.response_time_seconds for m in valid) / len(valid)
        self.avg_tokens = sum(m.tokens_total for m in valid) / len(valid)
        self.total_build_time = self.build_metrics.build_time_seconds if self.build_metrics else 0

        total_score = sum(m.total_score for m in valid)
        total_tokens = sum(m.tokens_total for m in valid)
        self.avg_score_per_token = total_score / total_tokens if total_tokens > 0 else 0

        # Count correct answers (>= 80% of max score)
        self.questions_correct = sum(
            1 for m in valid
            if m.total_score >= m.max_score * 0.8
        )

    def to_dict(self) -> Dict:
        return {
            "tool_name": self.tool_name,
            "codebase_name": self.codebase_name,
            "timestamp": self.timestamp,
            "build_metrics": asdict(self.build_metrics) if self.build_metrics else None,
            "answer_metrics": [asdict(m) for m in self.answer_metrics],
            "aggregated": {
                "avg_accuracy": round(self.avg_accuracy, 4),
                "avg_response_time": round(self.avg_response_time, 2),
                "avg_tokens": round(self.avg_tokens, 1),
                "avg_score_per_token": round(self.avg_score_per_token, 6),
                "total_build_time": round(self.total_build_time, 2),
                "questions_answered": self.questions_answered,
                "questions_correct": self.questions_correct,
            },
            "config": self.config,
        }


class MetricsCalculator:
    """指标计算器 — 提供 LLM 辅助评分和关键词匹配评分"""

    @staticmethod
    def keyword_match_score(answer: str, reference: str) -> Dict[str, float]:
        """基于关键词匹配的自动评分（baseline）"""
        if not answer or not reference:
            return {"completeness": 0, "accuracy": 0, "depth": 0, "total": 0}

        # Extract key terms from reference
        ref_words = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b', reference.lower()))
        # Filter common words
        stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can",
                       "had", "her", "was", "one", "our", "out", "has", "have", "this",
                       "that", "with", "from", "they", "been", "said", "each", "which",
                       "their", "will", "other", "about", "many", "then", "them", "these",
                       "some", "would", "make", "like", "into", "time", "very", "when",
                       "come", "could", "more", "over", "such", "after", "also", "than"}
        ref_keywords = ref_words - stop_words

        ans_words = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b', answer.lower()))
        ans_keywords = ans_words - stop_words

        if not ref_keywords:
            return {"completeness": 3, "accuracy": 3, "depth": 3, "total": 9}

        # How many reference keywords are covered
        overlap = ref_keywords & ans_keywords
        completeness = min(5.0, len(overlap) / len(ref_keywords) * 5.0 * 1.2)  # slight boost

        # How much of the answer is relevant (precision)
        if ans_keywords:
            precision = len(overlap) / len(ans_keywords)
        else:
            precision = 0
        accuracy = min(5.0, precision * 5.0 * 1.5)

        # Depth: longer, more detailed answers get higher scores
        ref_len = len(reference.split())
        ans_len = len(answer.split())
        depth_ratio = min(1.5, ans_len / ref_len) if ref_len > 0 else 0
        depth = min(5.0, depth_ratio * 3.5)

        total = completeness + accuracy + depth

        return {
            "completeness": round(completeness, 2),
            "accuracy": round(accuracy, 2),
            "depth": round(depth, 2),
            "total": round(total, 2),
        }

    @staticmethod
    def file_reference_score(answer: str, files_involved: List[str]) -> float:
        """评估回答中是否正确引用了相关文件"""
        if not files_involved:
            return 5.0  # No files to check

        mentioned = 0
        answer_lower = answer.lower()
        for f in files_involved:
            # Check filename or module path
            parts = f.replace('/', '.').replace('.py', '').split('.')
            for part in parts:
                if part and part in answer_lower:
                    mentioned += 1
                    break
            # Also check full path
            if f in answer or os.path.basename(f) in answer:
                mentioned += 0  # Already counted above

        return min(5.0, (mentioned / len(files_involved)) * 5.0)

    @staticmethod
    def compute_token_efficiency(results: List[AnswerMetrics]) -> Dict[str, float]:
        """计算 Token 效率指标"""
        if not results:
            return {}

        valid = [r for r in results if r.error is None and r.tokens_total > 0]
        if not valid:
            return {}

        total_tokens = sum(r.tokens_total for r in valid)
        total_score = sum(r.total_score for r in valid)
        correct = [r for r in valid if r.total_score >= r.max_score * 0.8]

        return {
            "total_tokens": total_tokens,
            "avg_tokens_per_question": total_tokens / len(valid),
            "tokens_per_score_point": total_tokens / total_score if total_score > 0 else float('inf'),
            "correct_answer_avg_tokens": sum(r.tokens_total for r in correct) / len(correct) if correct else 0,
            "token_efficiency_ratio": len(correct) / (total_tokens / 1000) if total_tokens > 0 else 0,
        }


import os  # needed for os.path.basename in file_reference_score
