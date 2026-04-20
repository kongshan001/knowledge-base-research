"""
知识库工具适配器基类 — 统一接口，方便扩展新的知识库方案。

每个知识库开源项目实现一个 Adapter，提供:
- build() — 构建知识库
- query() — 查询知识库
- get_context() — 获取上下文（用于注入到 LLM prompt）
"""

import os
import json
import time
import subprocess
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Import from our package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kb_benchmark.metrics import BuildMetrics


@dataclass
class QueryResult:
    """知识库查询结果"""
    success: bool
    context: str  # The retrieved context
    sources: List[str] = field(default_factory=list)  # Source files referenced
    query_time_seconds: float = 0.0
    tokens_estimate: int = 0  # Estimated token count of context
    extra: Dict[str, Any] = field(default_factory=dict)


class KnowledgeBaseAdapter(ABC):
    """知识库适配器基类"""

    def __init__(self, name: str, codebase_path: str, work_dir: str = "/tmp/kb-bench-work"):
        self.name = name
        self.codebase_path = Path(codebase_path)
        self.work_dir = Path(work_dir) / name
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self._build_metrics: Optional[BuildMetrics] = None
        self._built = False

    @abstractmethod
    def is_available(self) -> bool:
        """检查工具是否可用（已安装）"""
        pass

    @abstractmethod
    def build(self) -> BuildMetrics:
        """构建知识库，返回构建指标"""
        pass

    @abstractmethod
    def query(self, question: str, max_tokens: int = 8000) -> QueryResult:
        """查询知识库，返回相关上下文"""
        pass

    def get_context_for_question(self, question: str, max_tokens: int = 8000) -> str:
        """获取问题的上下文文本（用于注入 prompt）"""
        result = self.query(question, max_tokens)
        return result.context if result.success else ""

    def get_build_metrics(self) -> Optional[BuildMetrics]:
        return self._build_metrics

    def _count_loc(self) -> int:
        """统计代码行数"""
        total = 0
        for root, dirs, files in os.walk(self.codebase_path):
            # Skip hidden dirs, tests, docs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', '.git')]
            for f in files:
                if f.endswith('.py'):
                    filepath = Path(root) / f
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                            total += sum(1 for _ in fh)
                    except:
                        pass
        return total

    def _count_files(self) -> int:
        """统计 Python 文件数"""
        total = 0
        for root, dirs, files in os.walk(self.codebase_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', '.git')]
            total += sum(1 for f in files if f.endswith('.py'))
        return total

    def install(self) -> bool:
        """安装工具（如果需要），子类可覆盖"""
        return True

    def cleanup(self):
        """清理工作目录"""
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)
        self._built = False


class BaselineAdapter(KnowledgeBaseAdapter):
    """基线适配器 — 不使用任何知识库，直接返回空上下文"""

    def __init__(self, codebase_path: str):
        super().__init__("baseline", codebase_path)

    def is_available(self) -> bool:
        return True

    def build(self) -> BuildMetrics:
        start = time.time()
        loc = self._count_loc()
        files = self._count_files()
        elapsed = time.time() - start
        self._build_metrics = BuildMetrics(
            tool_name=self.name,
            build_time_seconds=elapsed,
            files_processed=files,
            lines_processed=loc,
            success=True,
        )
        self._built = True
        return self._build_metrics

    def query(self, question: str, max_tokens: int = 8000) -> QueryResult:
        return QueryResult(success=True, context="", tokens_estimate=0)


class RepomixAdapter(KnowledgeBaseAdapter):
    """Repomix 适配器 — 打包代码为 AI 友好格式"""

    def __init__(self, codebase_path: str, work_dir: str = "/tmp/kb-bench-work"):
        super().__init__("repomix", codebase_path, work_dir)
        self.output_file = self.work_dir / "repomix-output.txt"

    def is_available(self) -> bool:
        return shutil.which("repomix") is not None

    def install(self) -> bool:
        result = subprocess.run(
            ["npm", "install", "-g", "repomix@1.11.0"],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0

    def build(self) -> BuildMetrics:
        start = time.time()
        loc = self._count_loc()
        files = self._count_files()

        try:
            # Use globally installed repomix CLI (pinned v1.11.0)
            cmd = [
                "repomix",
                "--style", "plain",
                "--output", str(self.output_file),
                "--compress",
                str(self.codebase_path),
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300,
                cwd=str(self.work_dir)
            )

            elapsed = time.time() - start
            output_size = self.output_file.stat().st_size if self.output_file.exists() else 0

            self._build_metrics = BuildMetrics(
                tool_name=self.name,
                build_time_seconds=round(elapsed, 2),
                output_size_bytes=output_size,
                files_processed=files,
                lines_processed=loc,
                success=result.returncode == 0,
                extra={"command": " ".join(cmd)},
            )
        except Exception as e:
            elapsed = time.time() - start
            self._build_metrics = BuildMetrics(
                tool_name=self.name,
                build_time_seconds=round(elapsed, 2),
                files_processed=files,
                lines_processed=loc,
                success=False,
                errors_encountered=1,
                extra={"error": str(e)},
            )

        self._built = True
        return self._build_metrics

    def query(self, question: str, max_tokens: int = 8000) -> QueryResult:
        if not self.output_file.exists():
            return QueryResult(success=False, context="", tokens_estimate=0)

        start = time.time()
        try:
            with open(self.output_file, 'r', encoding='utf-8', errors='ignore') as f:
                full_content = f.read()

            # Simple truncation to max_tokens (~4 chars per token)
            max_chars = max_tokens * 4
            context = full_content[:max_chars]
            tokens_est = len(context) // 4

            return QueryResult(
                success=True,
                context=context,
                tokens_estimate=tokens_est,
                query_time_seconds=time.time() - start,
                extra={"strategy": "full_pack_truncated"},
            )
        except Exception as e:
            return QueryResult(
                success=False, context="",
                query_time_seconds=time.time() - start,
                extra={"error": str(e)},
            )


class Code2PromptAdapter(KnowledgeBaseAdapter):
    """Code2Prompt 适配器 — Rust 高性能代码打包"""

    def __init__(self, codebase_path: str, work_dir: str = "/tmp/kb-bench-work"):
        super().__init__("code2prompt", codebase_path, work_dir)
        self.output_file = self.work_dir / "code2prompt-output.md"

    def is_available(self) -> bool:
        return shutil.which("code2prompt") is not None

    def install(self) -> bool:
        # Requires cargo
        result = subprocess.run(
            ["cargo", "install", "code2prompt"],
            capture_output=True, text=True, timeout=600
        )
        return result.returncode == 0

    def build(self) -> BuildMetrics:
        start = time.time()
        loc = self._count_loc()
        files = self._count_files()

        try:
            cmd = [
                "code2prompt",
                str(self.codebase_path),
                "--output", str(self.output_file),
                "--tokens",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300,
                cwd=str(self.work_dir)
            )

            elapsed = time.time() - start
            output_size = self.output_file.stat().st_size if self.output_file.exists() else 0

            # Parse token count from output
            token_count = 0
            for line in (result.stdout + result.stderr).split('\n'):
                if 'token' in line.lower():
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        token_count = int(match.group(1))

            self._build_metrics = BuildMetrics(
                tool_name=self.name,
                build_time_seconds=round(elapsed, 2),
                output_size_bytes=output_size,
                files_processed=files,
                lines_processed=loc,
                success=result.returncode == 0,
                extra={"estimated_tokens": token_count},
            )
        except Exception as e:
            elapsed = time.time() - start
            self._build_metrics = BuildMetrics(
                tool_name=self.name,
                build_time_seconds=round(elapsed, 2),
                files_processed=files,
                lines_processed=loc,
                success=False,
                errors_encountered=1,
                extra={"error": str(e)},
            )

        self._built = True
        return self._build_metrics

    def query(self, question: str, max_tokens: int = 8000) -> QueryResult:
        if not self.output_file.exists():
            return QueryResult(success=False, context="", tokens_estimate=0)

        start = time.time()
        try:
            with open(self.output_file, 'r', encoding='utf-8', errors='ignore') as f:
                full_content = f.read()

            max_chars = max_tokens * 4
            context = full_content[:max_chars]

            return QueryResult(
                success=True,
                context=context,
                tokens_estimate=len(context) // 4,
                query_time_seconds=time.time() - start,
                extra={"strategy": "full_pack_truncated"},
            )
        except Exception as e:
            return QueryResult(
                success=False, context="",
                query_time_seconds=time.time() - start,
                extra={"error": str(e)},
            )


# Registry of available adapters
ADAPTER_REGISTRY: Dict[str, type] = {
    "baseline": BaselineAdapter,
    "repomix": RepomixAdapter,
    "code2prompt": Code2PromptAdapter,
}


def get_adapter(name: str, codebase_path: str, **kwargs) -> KnowledgeBaseAdapter:
    """获取适配器实例"""
    if name not in ADAPTER_REGISTRY:
        raise ValueError(f"Unknown adapter: {name}. Available: {list(ADAPTER_REGISTRY.keys())}")
    return ADAPTER_REGISTRY[name](codebase_path, **kwargs)


def list_adapters() -> List[str]:
    """列出所有已注册的适配器"""
    return list(ADAPTER_REGISTRY.keys())
