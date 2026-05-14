# CODE_REVIEW.md Template

## Summary

**审查范围（必须）**：
- PR / commit range / files：
- Diff 获取命令：

**结论（必须）**：
- Ready to merge?（Yes / No / With fixes）

## Critical Issues
> 必须修复：会导致 Bug / 安全问题 / 数据损坏 / 明显回归

（每条必须包含：文件:行号、问题、影响、修复建议、验证方式）

## Improvement Suggestions
> 建议修复：可维护性/可读性/性能/测试缺口（不阻塞合并但建议尽快处理）

（每条尽量包含：文件:行号、建议、原因、可能的实现方向）

## Code Style

## Positive Highlights

## Review Evidence Block（MANDATORY）

```
Claim: 完成了对 <范围> 的代码审查
Command: <实际用于获取 diff 的命令>
Exit code: <numeric>
Evidence: <1-3 行 diff 统计/文件列表>
Artifacts: CODE_REVIEW.md
```
