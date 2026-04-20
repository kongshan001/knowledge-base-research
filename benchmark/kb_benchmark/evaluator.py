"""
LLM 评估器 — 使用 LLM 对知识库辅助回答进行评分和对比。

支持两种模式:
1. 自动评分模式 — 使用关键词匹配和 LLM 辅助评分
2. LLM 回答模式 — 让 LLM 基于知识库上下文回答问题
"""

import json
import time
import subprocess
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass

from kb_benchmark.metrics import AnswerMetrics, MetricsCalculator


@dataclass
class LLMResponse:
    """LLM 响应"""
    text: str
    tokens_input: int = 0
    tokens_output: int = 0
    response_time: float = 0.0
    model: str = ""
    error: Optional[str] = None


class LLMEvaluator:
    """LLM 评估器 — 通过 Claude API 或 CLI 进行回答和评分"""

    def __init__(self, model: str = "glm-5.1", api_mode: str = "auto"):
        self.model = model
        self.api_mode = api_mode  # "cli", "api", "auto"
        self._claude_cli = self._find_claude_cli()

    def _find_claude_cli(self) -> Optional[str]:
        """查找 Claude Code CLI"""
        import shutil
        return shutil.which("claude")

    def _call_llm(self, prompt: str, max_tokens: int = 16384) -> LLMResponse:
        """调用 LLM（通过 Claude CLI）"""
        start = time.time()

        if self._claude_cli:
            try:
                # Use claude CLI in non-interactive mode
                result = subprocess.run(
                    ["claude", "--print", "--model", self.model,
                     "--max-tokens", str(max_tokens),
                     "-p", prompt],
                    capture_output=True, text=True, timeout=120
                )
                elapsed = time.time() - start

                if result.returncode == 0:
                    output = result.stdout.strip()
                    # Estimate tokens (~4 chars per token)
                    tokens_out = len(output) // 4
                    tokens_in = len(prompt) // 4

                    return LLMResponse(
                        text=output,
                        tokens_input=tokens_in,
                        tokens_output=tokens_out,
                        response_time=elapsed,
                        model=self.model,
                    )
                else:
                    return LLMResponse(
                        text="", response_time=elapsed,
                        error=f"CLI error: {result.stderr[:200]}",
                        model=self.model,
                    )
            except subprocess.TimeoutExpired:
                return LLMResponse(text="", error="Timeout", response_time=time.time() - start)
            except Exception as e:
                return LLMResponse(text="", error=str(e), response_time=time.time() - start)

        # Fallback: try hermes tools if available
        return LLMResponse(text="", error="No LLM backend available")

    def answer_question(
        self,
        question: str,
        context: str = "",
        codebase_name: str = "unknown",
        max_context_tokens: int = 8000,
    ) -> LLMResponse:
        """让 LLM 基于知识库上下文回答问题"""

        if context:
            prompt = f"""You are an expert software engineer analyzing the {codebase_name} codebase.

Below is relevant context from the codebase's knowledge base:

<knowledge_base_context>
{context[:max_context_tokens * 4]}
</knowledge_base_context>

Based on the above context, answer the following question precisely and accurately.
If the context doesn't contain enough information, say so and provide the best answer you can.

Question: {question}

Answer:"""
        else:
            prompt = f"""You are an expert software engineer. Answer the following question about the {codebase_name} codebase.

Note: You do NOT have access to the codebase. Answer based on your general knowledge only.

Question: {question}

Answer:"""

        return self._call_llm(prompt)

    def score_answer(
        self,
        question: str,
        answer: str,
        reference_answer: str,
    ) -> Dict[str, float]:
        """使用 LLM 对回答进行评分"""

        # First, use keyword matching as baseline
        keyword_scores = MetricsCalculator.keyword_match_score(answer, reference_answer)

        # Then try LLM-based scoring for more accuracy
        scoring_prompt = f"""Score the following AI answer on a scale of 0-5 for each criterion.

Question: {question}

Reference Answer (ground truth):
{reference_answer}

AI Answer to Score:
{answer}

Score each criterion from 0 to 5:
- completeness: Does the answer cover all key points from the reference?
- accuracy: Is the information correct?
- depth: Does it provide meaningful technical depth?

Respond ONLY with a JSON object like:
{{"completeness": 4.0, "accuracy": 3.5, "depth": 3.0, "total": 10.5}}"""

        llm_response = self._call_llm(scoring_prompt, max_tokens=256)

        if llm_response.error is None and llm_response.text:
            try:
                # Extract JSON from response
                text = llm_response.text
                json_match = re.search(r'\{[^}]+\}', text)
                if json_match:
                    scores = json.loads(json_match.group())
                    total = scores.get("completeness", 0) + scores.get("accuracy", 0) + scores.get("depth", 0)
                    return {
                        "completeness": float(scores.get("completeness", 0)),
                        "accuracy": float(scores.get("accuracy", 0)),
                        "depth": float(scores.get("depth", 0)),
                        "total": float(total),
                        "scoring_method": "llm",
                    }
            except (json.JSONDecodeError, ValueError):
                pass

        # Fallback to keyword scores
        keyword_scores["scoring_method"] = "keyword_match"
        return keyword_scores

    def evaluate_single(
        self,
        question_id: str,
        question: str,
        reference_answer: str,
        context: str,
        codebase_name: str,
        files_involved: List[str] = None,
    ) -> AnswerMetrics:
        """评估单个问题"""

        # Step 1: Get LLM answer
        llm_response = self.answer_question(question, context, codebase_name)

        if llm_response.error:
            return AnswerMetrics(
                question_id=question_id,
                reference_answer=reference_answer,
                error=llm_response.error,
                response_time_seconds=llm_response.response_time,
            )

        # Step 2: Score the answer
        scores = self.score_answer(question, llm_response.text, reference_answer)

        # Step 3: Calculate file reference score
        file_score = 0
        if files_involved:
            file_score = MetricsCalculator.file_reference_score(
                llm_response.text, files_involved
            )

        total_score = scores.get("total", 0) + file_score
        max_score = 15.0 + 5.0  # 3 criteria * 5 + file reference * 5

        return AnswerMetrics(
            question_id=question_id,
            answer=llm_response.text,
            reference_answer=reference_answer,
            scores=scores,
            total_score=round(total_score, 2),
            max_score=max_score,
            response_time_seconds=llm_response.response_time,
            tokens_input=llm_response.tokens_input,
            tokens_output=llm_response.tokens_output,
            tokens_total=llm_response.tokens_input + llm_response.tokens_output,
            correct_files_referenced=int(file_score),
            total_files_involved=len(files_involved) if files_involved else 0,
        )
