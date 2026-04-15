#!/usr/bin/env python3
"""
GitHub 项目检索脚本 — 搜索 Claude Code 知识库相关开源项目
输出 JSON 格式的检索结果，供定时任务使用
"""
import json
import subprocess
import sys
import time
from datetime import datetime

SEARCH_QUERIES = [
    "claude code knowledge base",
    "claude code RAG",
    "claude code vector database",
    "claude code documentation assistant",
    "claude code codebase understanding",
    "LLM knowledge base code analysis",
    "claude MCP knowledge",
    "claude code memory",
    "AI coding assistant knowledge base",
    "code search embedding knowledge",
    "claude code context management",
    "code knowledge graph LLM",
    "developer knowledge base AI",
    "codebase RAG embedding",
    "claude code semantic search",
]

MIN_STARS = 10

def search_github(query, sort="stars", limit=10):
    """Search GitHub repositories"""
    cmd = [
        "gh", "search", "repos",
        query,
        "--sort", sort,
        "--limit", str(limit),
        "--json", "fullName,description,stargazersCount,updatedAt,language,url,topics,archived",
        "--stars", f">={MIN_STARS}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error searching '{query}': {result.stderr}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Exception searching '{query}': {e}", file=sys.stderr)
        return []

def main():
    all_results = {}
    
    for query in SEARCH_QUERIES:
        print(f"Searching: {query}", file=sys.stderr)
        results = search_github(query)
        for repo in results:
            full_name = repo.get("fullName", "")
            if full_name and full_name not in all_results:
                all_results[full_name] = {
                    "full_name": full_name,
                    "description": repo.get("description", ""),
                    "stars": repo.get("stargazersCount", 0),
                    "language": repo.get("language", ""),
                    "updated_at": repo.get("updatedAt", ""),
                    "url": repo.get("url", ""),
                    "topics": repo.get("topics", []),
                    "archived": repo.get("archived", False),
                    "discovered_at": datetime.now().isoformat(),
                    "discovered_by_query": query,
                }
        time.sleep(1)  # Rate limiting
    
    # Sort by stars descending
    sorted_results = sorted(all_results.values(), key=lambda x: x["stars"], reverse=True)
    
    # Output as JSON
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_found": len(sorted_results),
        "projects": sorted_results,
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
