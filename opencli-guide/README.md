# OpenCLI 安装与使用指南

OpenCLI 是一个“万物皆可 CLI”的强大工具，特别为 AI Agent 设计。它的核心能力是：**把任何网站、Electron 桌面应用（如 Cursor、Notion 等）变成标准的命令行接口**。

它最大的亮点是**直接复用你本地 Chrome 浏览器的登录状态**，无需去折腾复杂的 API Key 或 Token。

## 1. 环境准备与安装

**前置要求：**
- Node.js (>= 20.0.0)
- Google Chrome 浏览器

**安装命令：**
在终端执行以下命令进行全局安装：

```bash
npm install -g @jackwener/opencli
```

## 2. 基础使用（公开数据，无需配置）

安装完成后，你可以立即使用一些无需登录权限的公共命令。

**查看所有支持的平台和命令：**
```bash
opencli list
```

**示例 1：获取 HackerNews 热门前 3 条：**
```bash
opencli hackernews top --limit 3
```

**示例 2：获取 V2EX 热门帖子前 3 条：**
```bash
opencli v2ex hot --limit 3
```

## 3. 高级使用（需读取浏览器登录状态）

大部分网站（如推特、知乎、小红书等）需要登录权限。为了让 OpenCLI 能够复用你的登录状态，你需要进行一次**极简的浏览器插件配置**。

### 3.1 安装浏览器桥接插件
1. 前往 [OpenCLI GitHub Releases 页面](https://github.com/jackwener/opencli/releases) 下载最新版本的 `opencli-extension.zip`。
2. 将下载的 `.zip` 文件解压到一个固定的文件夹中。
3. 打开 Chrome 浏览器，地址栏输入并访问 `chrome://extensions`。
4. 开启页面右上角的**“开发者模式”**开关。
5. 点击页面左上角的**“加载已解压的扩展程序”**，选择你刚刚解压的文件夹。

> **提示：** 配置完成后，本地守护进程会在你运行相关命令时自动启动，无需额外手动配置。

### 3.2 使用示例
确保你在 Chrome 中**已经正常登录**了对应的网站，然后直接在终端执行：

```bash
# 查看推特热搜（需在 Chrome 中登录 Twitter/X）
opencli twitter trending

# 查看知乎热榜（需在 Chrome 中登录知乎）
opencli zhihu hot

# 搜索小红书笔记（需在 Chrome 中登录小红书）
opencli xiaohongshu search "猫咪"

# 下载微信公众号文章为 Markdown 格式（需提供链接）
opencli weixin download
```

## 4. 安全性与防封控说明

- **隐私安全（零风险）**：你的账号密码、Cookie、Token **永远不会离开你的本地机器**。它纯粹是在本地通过 CDP（Chrome DevTools Protocol）或注入脚本控制你自己的浏览器。
- **防封控（高隐匿）**：最新版本的 OpenCLI 内置了高级的“浏览器隐身（Stealth Anti-Detection）”功能（如屏蔽 WebDriver 检测、清理自动化痕迹等），能有效防止网站发现你在使用自动化脚本。
- **注意事项**：由于该工具具有控制你已登录浏览器的最高权限，**请仅使用官方自带的指令，或者你绝对信任的开发者编写的第三方 Adapter**。

## 5. 常见问题排查

### 5.1 执行命令返回 `(no data)` 怎么办？
如果你在运行类似 `opencli zhihu hot` 时，终端直接返回 `(no data)` 并且没有报错，这是因为该命令处于 `[cookie]` 或 `[browser]` 模式。
**原因**：OpenCLI 需要通过浏览器插件读取你当前 Chrome 中真实的登录态（Cookie/数据），如果你没有配置插件或 Chrome 中未登录该网站，就会静默返回空数据。
**解决办法**：
1. 确保已按本文 `3.1` 章节正确安装了 Chrome 浏览器桥接插件。
2. 打开 Chrome，确保你**已经登录**了目标网站（例如 `https://www.zhihu.com`）。
3. 运行 `opencli doctor` 检查守护进程状态。

### 5.2 诊断工具
如果你在运行需要登录的命令时遇到其他报错或数据为空，可以使用自带的诊断命令来检查连接状态：

```bash
opencli doctor
```
它会帮你自动诊断扩展程序和本地守护进程（Daemon）是否工作正常。