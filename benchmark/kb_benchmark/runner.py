"""
Benchmark Runner — 核心执行引擎。

编排完整的评测流程：
1. 构建知识库 → 2. 查询获取上下文 → 3. LLM 回答 → 4. 评分 → 5. 聚合结果
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from kb_benchmark.dataset import QuestionDataset, Question
from kb_benchmark.metrics import BenchmarkResult, BuildMetrics, AnswerMetrics, MetricsCalculator
from kb_benchmark.adapters import KnowledgeBaseAdapter, get_adapter, list_adapters
from kb_benchmark.evaluator import LLMEvaluator


class BenchmarkRunner:
    """Benchmark 执行引擎"""

    def __init__(
        self,
        codebase_path: str,
        dataset_path: str,
        results_dir: str = "./results",
        tools: List[str] = None,
        model: str = "glm-5.1",
        max_context_tokens: int = 64000,  # GLM-5.1: 200K context window, use 64K for KB context
        questions_limit: int = 0,  # 0 = all questions
    ):
        self.codebase_path = Path(codebase_path)
        self.dataset_path = Path(dataset_path)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.tools = tools or ["baseline"]
        self.model = model
        self.max_context_tokens = max_context_tokens
        self.questions_limit = questions_limit

        # Load dataset
        self.dataset = QuestionDataset(str(self.dataset_path))
        self.evaluator = LLMEvaluator(model=model)

    def run(self, tool_names: List[str] = None) -> List[BenchmarkResult]:
        """运行完整 Benchmark"""
        tools = tool_names or self.tools
        results = []

        # Load questions
        print(f"📂 Loading dataset from {self.dataset_path}...")
        questions = self.dataset.load()
        if self.questions_limit > 0:
            questions = questions[:self.questions_limit]
        print(f"   Loaded {len(questions)} questions")

        # Run for each tool
        for tool_name in tools:
            print(f"\n{'='*60}")
            print(f"🔧 Running benchmark for: {tool_name}")
            print(f"{'='*60}")

            result = self._run_single_tool(tool_name, questions)
            results.append(result)

            # Save individual result
            self._save_result(result)

        # Generate comparison report
        if len(results) > 1:
            self._generate_comparison(results)

        return results

    def _run_single_tool(self, tool_name: str, questions: List[Question]) -> BenchmarkResult:
        """运行单个工具的完整评测"""

        result = BenchmarkResult(
            tool_name=tool_name,
            codebase_name=self.codebase_path.name,
            timestamp=datetime.now().isoformat(),
            config={
                "model": self.model,
                "max_context_tokens": self.max_context_tokens,
                "questions_count": len(questions),
            },
        )

        # Step 1: Build knowledge base
        print(f"\n  📦 Step 1: Building knowledge base...")
        try:
            adapter = get_adapter(tool_name, str(self.codebase_path))

            if not adapter.is_available():
                print(f"  ⚠️  {tool_name} not available, installing...")
                if not adapter.install():
                    print(f"  ❌ Failed to install {tool_name}, skipping")
                    result.build_metrics = BuildMetrics(
                        tool_name=tool_name, success=False,
                        errors_encountered=1,
                        extra={"error": "Installation failed"},
                    )
                    return result

            build_metrics = adapter.build()
            result.build_metrics = build_metrics

            status = "✅" if build_metrics.success else "❌"
            print(f"  {status} Build: {build_metrics.build_time_seconds:.1f}s, "
                  f"{build_metrics.files_processed} files, "
                  f"{build_metrics.lines_processed:,} lines, "
                  f"output {build_metrics.output_size_bytes:,} bytes")

        except Exception as e:
            print(f"  ❌ Build failed: {e}")
            result.build_metrics = BuildMetrics(
                tool_name=tool_name, success=False,
                errors_encountered=1, extra={"error": str(e)},
            )
            return result

        # Step 2: Answer questions
        print(f"\n  📝 Step 2: Answering {len(questions)} questions...")
        for i, q in enumerate(questions):
            print(f"  [{i+1}/{len(questions)}] {q.id} ({q.difficulty})...", end=" ", flush=True)

            try:
                # Get context from knowledge base
                context = adapter.get_context_for_question(q.question, self.max_context_tokens)

                # Evaluate answer
                answer_metrics = self.evaluator.evaluate_single(
                    question_id=q.id,
                    question=q.question,
                    reference_answer=q.reference_answer,
                    context=context,
                    codebase_name=self.codebase_path.name,
                    files_involved=q.files_involved,
                )

                result.answer_metrics.append(answer_metrics)

                if answer_metrics.error:
                    print(f"❌ Error: {answer_metrics.error[:50]}")
                else:
                    print(f"✅ Score: {answer_metrics.total_score:.1f}/{answer_metrics.max_score:.0f} "
                          f"({answer_metrics.accuracy_rate:.0%}) "
                          f"tokens: {answer_metrics.tokens_total}")

            except Exception as e:
                print(f"❌ Exception: {e}")
                result.answer_metrics.append(AnswerMetrics(
                    question_id=q.id,
                    reference_answer=q.reference_answer,
                    error=str(e),
                ))

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        # Step 3: Aggregate results
        result.aggregate()

        # Cleanup
        try:
            adapter.cleanup()
        except:
            pass

        return result

    def _save_result(self, result: BenchmarkResult):
        """保存单次结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.tool_name}_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"\n  💾 Result saved: {filepath}")

    def _generate_comparison(self, results: List[BenchmarkResult]):
        """生成对比报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.results_dir / f"comparison_{timestamp}.md"

        lines = [
            f"# 📊 Benchmark 对比报告",
            f"",
            f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> 代码库: {results[0].codebase_name if results else 'N/A'}",
            f"> 评测模型: {self.model}",
            f"> 题目数量: {results[0].questions_answered if results else 0}",
            f"",
            f"## 📈 总览对比",
            f"",
            f"| 指标 | " + " | ".join(r.tool_name for r in results) + " |",
            f"|------|" + "|".join(["------"] * len(results)) + "|",
        ]

        # Build time
        lines.append(
            f"| 构建时间 (s) | " +
            " | ".join(f"{r.total_build_time:.1f}" for r in results) + " |"
        )

        # Accuracy
        lines.append(
            f"| 平均准确率 | " +
            " | ".join(f"{r.avg_accuracy:.1%}" for r in results) + " |"
        )

        # Response time
        lines.append(
            f"| 平均响应时间 (s) | " +
            " | ".join(f"{r.avg_response_time:.1f}" for r in results) + " |"
        )

        # Tokens
        lines.append(
            f"| 平均 Token 消耗 | " +
            " | ".join(f"{r.avg_tokens:.0f}" for r in results) + " |"
        )

        # Score per token
        lines.append(
            f"| Token 效率 (分/Token) | " +
            " | ".join(f"{r.avg_score_per_token:.6f}" for r in results) + " |"
        )

        # Correct answers
        lines.append(
            f"| 正确回答数 (≥80%) | " +
            " | ".join(f"{r.questions_correct}/{r.questions_answered}" for r in results) + " |"
        )

        # Detailed category breakdown
        lines.extend([
            "",
            "## 📋 分类详情",
            "",
        ])

        for r in results:
            lines.append(f"### {r.tool_name}")
            lines.append(f"- 构建时间: {r.total_build_time:.1f}s")
            lines.append(f"- 准确率: {r.avg_accuracy:.1%}")
            lines.append(f"- 平均响应: {r.avg_response_time:.1f}s")
            lines.append(f"- 平均 Token: {r.avg_tokens:.0f}")
            lines.append(f"- Token 效率: {r.avg_score_per_token:.6f}")
            lines.append("")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"\n  📊 Comparison report: {report_path}")

    @staticmethod
    def quick_run(
        codebase_path: str = "/tmp/benchmark-codebase/django",
        dataset_path: str = "/tmp/knowledge-base-research/benchmark/dataset",
        results_dir: str = "/tmp/knowledge-base-research/benchmark/results",
        tools: List[str] = None,
        questions_limit: int = 10,
    ) -> List[BenchmarkResult]:
        """快速运行 Benchmark（便捷方法）"""
        runner = BenchmarkRunner(
            codebase_path=codebase_path,
            dataset_path=dataset_path,
            results_dir=results_dir,
            tools=tools or ["baseline"],
            questions_limit=questions_limit,
        )
        return runner.run(tools)
