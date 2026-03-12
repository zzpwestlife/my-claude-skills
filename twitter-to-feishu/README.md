# Twitter to Feishu Skill - 安装和使用指南

## 简介

这个 Claude Code skill 可以自动抓取 Twitter/X 文章并转换为飞书兼容的 Word 文档，所有图片都会嵌入到文档中。

**核心特性：**
- ✅ 自动抓取 Twitter/X 文章内容
- ✅ 使用 Playwright 下载图片（解决网络限制问题）
- ✅ 生成包含本地图片的 Word 文档
- ✅ 可直接导入飞书/Lark

## 安装方法

### 方式 1：从 .skill 文件安装（推荐）

1. 下载 `twitter-to-feishu.skill` 文件
2. 在终端运行：
```bash
claude skill install twitter-to-feishu.skill
```

### 方式 2：从 GitHub 安装（如果发布到 GitHub）

```bash
npx skills add <your-github-username>/twitter-to-feishu
```

## 前置要求

使用此 skill 需要：

1. **web-content-extractor 项目**
   - 克隆或下载项目到本地
   - 推荐位置：`~/Code/OpenSource/my-trivia-tools/web-content-extractor`

2. **Python 环境**
   ```bash
   cd web-content-extractor
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Playwright 浏览器**
   ```bash
   playwright install chromium
   ```

## 使用方法

安装完成后，直接在 Claude Code 中使用：

```
抓取这个 Twitter 文章：https://x.com/username/status/123456789
```

或者：

```
把这个 X 帖子转成飞书文档：https://x.com/...
```

Skill 会自动：
1. 提取文章内容
2. 下载所有图片
3. 生成 Word 文档

最终输出：`output/*_local.docx` 文件可直接导入飞书。

## 工作原理

### 三步工作流

1. **提取内容** - 使用 Playwright 抓取 Twitter 页面
2. **下载图片** - 使用 Playwright 绕过 CDN 限制下载图片
3. **生成文档** - 将 Markdown 转换为包含本地图片的 Word 文档

### 关键技术点

**为什么使用 Playwright 下载图片？**

Twitter 的 CDN (pbs.twimg.com) 会阻止直接 HTTP 请求（curl/requests 会超时）。Playwright 通过模拟真实浏览器来绕过这个限制：

```python
# ✗ 直接请求经常失败
response = requests.get(image_url, timeout=5)

# ✓ Playwright 模拟浏览器成功
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(image_url)
    await page.screenshot(path=filepath)
```

## 故障排除

### 问题：图片下载失败

**解决方案：** 确保 Playwright 浏览器已安装
```bash
playwright install chromium
```

### 问题：找不到 web-content-extractor

**解决方案：** 确认项目路径，或在 skill 使用时指定路径

### 问题：转换为 docx 失败

**解决方案：** 确保虚拟环境中安装了所有依赖
```bash
cd web-content-extractor
source venv/bin/activate
pip install -r requirements.txt
```

## 文件结构

```
twitter-to-feishu/
├── SKILL.md                              # Skill 主文档
├── scripts/
│   ├── download_images_playwright.py     # 图片下载脚本
│   ├── finalize_document.py              # 文档生成脚本
│   └── extract_twitter.sh                # 完整工作流脚本
└── references/
    └── troubleshooting.md                # 故障排除指南
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

Created with Claude Code
