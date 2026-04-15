# 📐 知识库效果验证 Benchmark 设计方案

## 1. 设计目标

量化评估**建设知识库 vs 不建设知识库**对 AI 编码能力（以 Claude 为代表）在**真实生产环境**中的实际差异。

## 2. 评测对象

- **目标代码库**: Godot Engine 源码（~200 万行 C++，复杂度高、模块多、文档相对完善）
- **AI 模型**: Claude（通过 Claude Code CLI / API）
- **知识库方案**: 各开源项目按调研顺序接入

## 3. 评测维度

### 3.1 代码理解能力（Code Understanding）

| 指标 | 说明 | 评分方式 |
|------|------|---------|
| **函数功能解释** | 给定一个函数，准确描述其功能 | 0-5 人工评分 |
| **模块关系理解** | 正确描述模块间依赖和调用关系 | 0-5 人工评分 |
| **Bug 定位** | 在给定 Bug 描述下，正确定位问题代码 | 命中率 % |
| **架构理解** | 对整体架构的描述准确性 | 0-5 人工评分 |

### 3.2 代码生成能力（Code Generation）

| 指标 | 说明 | 评分方式 |
|------|------|---------|
| **功能实现** | 根据需求生成可编译通过的代码 | 编译通过率 % |
| **代码风格一致性** | 生成的代码与 Godot 代码风格一致 | 0-5 评分 |
| **API 使用正确性** | 正确使用 Godot 内部 API | 正确率 % |
| **上下文连贯性** | 生成代码与现有代码的融合度 | 0-5 评分 |

### 3.3 问题解决能力（Problem Solving）

| 指标 | 说明 | 评分方式 |
|------|------|---------|
| **Issue 回答** | 基于 GitHub Issue 的解决方案质量 | 0-5 评分 |
| **跨模块推理** | 涉及多个模块的问题解决能力 | 0-5 评分 |
| **性能优化建议** | 给出可行的性能优化方案 | 0-5 评分 |

### 3.4 效率指标

| 指标 | 说明 | 度量方式 |
|------|------|---------|
| **首次响应准确率** | 第一次回答即正确的比例 | % |
| **上下文消耗** | 完成 task 消耗的 token 数 | Token 数 |
| **迭代次数** | 达到正确答案需要的对话轮数 | 轮次 |
| **响应延迟** | 平均响应时间 | 秒 |

## 4. 测试数据集

### 4.1 数据集构建方法

从 Godot 源码中构建以下类型的测试题：

```
benchmark/dataset/
├── code-understanding/
│   ├── function-explanation.jsonl    # 函数功能解释题
│   ├── module-relation.jsonl         # 模块关系题
│   ├── bug-localization.jsonl        # Bug 定位题
│   └── architecture.jsonl            # 架构理解题
├── code-generation/
│   ├── feature-implementation.jsonl  # 功能实现题
│   ├── style-consistency.jsonl       # 代码风格题
│   └── api-usage.jsonl               # API 使用题
├── problem-solving/
│   ├── github-issues.jsonl           # 真实 Issue 解决题
│   ├── cross-module.jsonl            # 跨模块推理题
│   └── optimization.jsonl            # 性能优化题
└── metadata.json                     # 数据集元信息
```

### 4.2 题目格式

```json
{
  "id": "CU-001",
  "category": "code-understanding",
  "subcategory": "function-explanation",
  "difficulty": "medium",
  "question": "解释 scene/3d/physics_body_3d.cpp 中 RigidBody3D::_direct_state_changed 的功能和调用链",
  "reference_answer": "...",
  "files_involved": ["scene/3d/physics_body_3d.cpp", "servers/physics_server_3d.h"],
  "scoring": {
    "completeness": 5,
    "accuracy": 5,
    "depth": 5
  }
}
```

## 5. 评测流程

```
┌──────────────────────────────────────────────────┐
│                  Benchmark 流程                    │
├──────────────────────────────────────────────────┤
│                                                    │
│  1. 准备阶段                                       │
│     ├── 克隆 Godot 源码                             │
│     ├── 构建测试数据集（30+ 题）                     │
│     └── 准备知识库（按方案索引 Godot 源码）           │
│                                                    │
│  2. 基线测试（无知识库）                             │
│     ├── Claude 直接回答测试题                        │
│     ├── 记录回答、Token、耗时                        │
│     └── 人工评分 + 自动评分                          │
│                                                    │
│  3. 知识库测试（有知识库）                           │
│     ├── Claude + 知识库 回答测试题                   │
│     ├── 记录回答、Token、耗时                        │
│     └── 人工评分 + 自动评分                          │
│                                                    │
│  4. 对比分析                                       │
│     ├── 各维度得分对比                               │
│     ├── 效率指标对比                                 │
│     └── 生成 Benchmark 报告                         │
│                                                    │
└──────────────────────────────────────────────────┘
```

## 6. 评分标准

| 分数 | 含义 |
|------|------|
| 5 | 完全正确，细节准确，超出预期 |
| 4 | 基本正确，细节略有偏差 |
| 3 | 方向正确，但有明显遗漏或错误 |
| 2 | 部分相关，但有重大错误 |
| 1 | 几乎不相关 |
| 0 | 完全错误或无法回答 |

## 7. 结果输出

评测结果将自动生成在 `benchmark/results/` 目录下，包含：
- 各维度详细得分表
- 雷达图对比（有/无知识库）
- Token 消耗对比
- 优化建议

---

*此 Benchmark 方案将持续迭代，欢迎补充和改进*
