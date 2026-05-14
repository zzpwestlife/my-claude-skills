#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude Code Agent - Changelog Generator
用于分析当前分支与主分支的差异，并自动生成 CHANGELOG.md
"""

import os
import sys
import subprocess
import argparse
import json

class ChangelogAgent:
    def __init__(self, options):
        self.options = options
        self.repo_dir = os.getcwd()
        self.changelog_file = os.path.join(self.repo_dir, "CHANGELOG.md")
        self.config = self._load_config()
        self.main_branch = self._detect_main_branch()

    def _load_config(self):
        """加载配置文件"""
        config_paths = [
            os.path.join(self.repo_dir, "changelog_config.json"),
            os.path.join(self.repo_dir, ".claude", "changelog_config.json")
        ]
        
        default_config = {
            "ignore_patterns": [],
            "commit_url_template": "" # e.g. https://github.com/user/repo/commit/{hash}
        }
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                        default_config.update(user_config)
                        if self.options.verbose:
                            print(f"已加载配置文件: {path}")
                        return default_config
                except Exception as e:
                    print(f"配置文件加载失败 {path}: {e}")
        
        return default_config

    def _run_git(self, args):
        """运行 git 命令并返回输出"""
        try:
            result = subprocess.check_output(
                ["git"] + args, 
                stderr=subprocess.STDOUT,
                cwd=self.repo_dir
            )
            return result.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            if self.options.verbose:
                print(f"Git Error: {e.output.decode('utf-8')}")
            return None

    def _detect_main_branch(self):
        """自动检测主分支名称 (main 或 master)"""
        branches = self._run_git(["branch", "-r"])
        if not branches:
            return "main" # 默认回退
        
        if "origin/main" in branches:
            return "main"
        elif "origin/master" in branches:
            return "master"
        
        # 尝试本地分支
        local_branches = self._run_git(["branch"])
        if "main" in local_branches:
            return "main"
        elif "master" in local_branches:
            return "master"
            
        return "main" # 最终默认

    def get_current_branch(self):
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def get_full_diff(self):
        """获取当前工作区与主分支的完整代码差异 (git diff)"""
        # 排除常见的锁定文件和二进制文件，减少干扰
        # 使用 :(exclude) 语法以兼容更多 Git 版本，或仅依赖 .gitignore
        # 注意：git diff main 默认会包含所有差异，除非文件被 ignore。
        # 如果这些文件已在版本控制中，我们需要显式排除。
        
        exclude_patterns = [
            "package-lock.json", 
            "yarn.lock", 
            "pnpm-lock.yaml",
            "go.sum",
            "*.lock",
            "*.pyc",
        ]
        
        # 构建 exclude 参数
        # 使用 :(exclude)pattern 语法
        exclude_args = [f":(exclude){p}" for p in exclude_patterns]
        
        # git diff <main_branch> 会对比工作区（含未提交变更）与主分支
        cmd = ["diff", self.main_branch, "--", "."] + exclude_args
        return self._run_git(cmd)

    def run(self):
        """执行主流程"""
        # 模式: 获取差异 (Diff Mode)
        # 这是默认行为
        # 脚本不再负责生成 Markdown，而是负责提供原始数据给 AI Agent
        print(f"正在获取代码差异: 当前工作区 <-> 主分支 [{self.main_branch}] ...", file=sys.stderr)
        
        diff_content = self.get_full_diff()
        
        if not diff_content:
            print("未发现代码差异。", file=sys.stderr)
            return

        # 直接输出 Diff 内容到 stdout，供 Agent 读取
        print(diff_content)

def main():
    parser = argparse.ArgumentParser(description="Claude Code Agent - Changelog Generator")
    parser.add_argument("--dry-run", action="store_true", help="[已废弃] 预览模式")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")
    parser.add_argument("--version", type=str, help="[已废弃] 指定版本号")
    
    args = parser.parse_args()
    
    agent = ChangelogAgent(args)
    agent.run()

if __name__ == "__main__":
    main()
