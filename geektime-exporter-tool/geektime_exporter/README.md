# 极客时间 Markdown 导出工具

## 功能
- 自动登录并复用会话（默认浏览器引导登录，兼容账号密码模式）
- 导出单篇文章或批量导出专栏文章
- 保留标题、段落、代码块、引用、列表语义，输出 GFM Markdown
- 下载图片到本地并替换为相对路径，支持断点续传与去重
- 失败重试、错误分类、运行日志记录

## 安装（macOS）
```bash
python3 -m pip install -e .
```

安装后可执行命令：
```bash
geektime-exporter export --help
```

## 配置文件（JSON）
浏览器登录模式（推荐）：
```json
{
  "auth_mode": "browser",
  "browser_cdp_url": "http://127.0.0.1:9222",
  "browser_cdp_required": true,
  "browser_login_url": "https://time.geekbang.org/",
  "browser_channel": "chrome",
  "session_file": "./output/.session.json",
  "log_file": "./output/export.log"
}
```

账号密码模式（兼容）：
```json
{
  "auth_mode": "password",
  "username": "your-username",
  "password": "your-password",
  "login_url": "https://time.geekbang.org/serv/v1/login",
  "session_file": "./output/.session.json",
  "log_file": "./output/export.log"
}
```

说明：
- `auth_mode` 默认是 `browser`，首次会自动打开系统默认浏览器引导登录
- 浏览器模式优先使用 CDP 连接你已打开的真实 Chrome 会话
- `browser_cdp_required` 默认为 `true`，CDP 不可用会直接报错退出
- 浏览器模式下，工具会自动读取浏览器登录会话并写入 `session_file`，后续优先复用
- `browser_channel` 可选，推荐 `"chrome"`（使用本机 Chrome 通道）
- 会话失效后会自动触发重新登录流程
- 账号密码模式下，凭据优先读取环境变量 `GEEKTIME_USERNAME` / `GEEKTIME_PASSWORD`，缺失时回退配置文件
- 首次使用浏览器模式前，建议执行 `make install-browser`
- 使用 CDP 前，请先启动可调试 Chrome：
```bash
open -na "Google Chrome" --args --remote-debugging-port=9222
```

## 命令示例
单篇导出：
```bash
geektime-exporter export \
  --article "https://time.geekbang.org/column/article/100000" \
  --output "./output" \
  --images-dir "./output/images" \
  --naming slug \
  --retries 3
```

批量导出：
```bash
geektime-exporter export \
  --batch "https://time.geekbang.org/column/intro/123" \
  --output "./output" \
  --images-dir "./output/images" \
  --naming id \
  --retries 3
```

## Makefile 使用
工具目录提供了 [Makefile](file:///Users/admin/openSource/my-claude-skills/geektime-exporter-tool/Makefile)，可用简短命令完成安装、测试和导出。

查看所有命令：
```bash
make help
```

安装、检查与测试：
```bash
make install
make install-browser
make lint
make fmt
make test
make export-log-reset
```

单篇导出：
```bash
make export-one ARTICLE="https://time.geekbang.org/column/article/100000"
```

批量导出：
```bash
make export-batch BATCH="https://time.geekbang.org/column/intro/123"
```

低噪音模式（先清空日志再执行导出）：
```bash
make export-one-clean ARTICLE="https://time.geekbang.org/column/article/100000"
make export-batch-clean BATCH="https://time.geekbang.org/column/intro/123"
```

覆盖默认参数（输出目录、图片目录、命名规则、重试次数、配置文件）：
```bash
make export-batch \
  BATCH="https://time.geekbang.org/column/intro/123" \
  OUTPUT="./data/md" \
  IMAGES="./data/md/images" \
  NAMING="id" \
  RETRIES=5 \
  CONFIG="./prod-config.json"
```

清理输出目录：
```bash
make clean
```

## 低噪音建议
- 每次导出前先执行 `make export-log-reset`，避免历史日志干扰判断
- 优先看本次导出的 `*-failed.json`，它只记录当前批次失败项
- 日志文件位置可用 `LOG_FILE=...` 自定义，例如：
```bash
make export-log-reset LOG_FILE="./output/run-2026-05-08.log"
```

## 常见问题
- 浏览器登录失败：确认系统默认浏览器可打开极客时间并能正常登录
- 登录失败：检查 `auth_mode`、`login_url`、账户凭据与已付费访问权限
- 网络失败：提高 `--retries`，并检查网络连通性
- 会话失效：删除 `session_file` 后重试，系统也会自动重登
- 图片重复下载：工具按内容哈希去重，首次完成后会复用本地文件
