# Tasks
- [x] Task 1: 搭建项目骨架与 CLI 入口
  - [x] SubTask 1.1: 初始化可执行程序入口（支持 `export` 子命令）
  - [x] SubTask 1.2: 定义命令参数（单篇/批量、输出路径、图片路径、命名规则、重试参数）
  - [x] SubTask 1.3: 接入配置文件加载与参数覆盖优先级逻辑

- [x] Task 2: 实现登录与会话管理
  - [x] SubTask 2.1: 实现账户登录流程与凭据读取
  - [x] SubTask 2.2: 实现会话持久化与过期检测
  - [x] SubTask 2.3: 实现会话失效后的自动恢复策略

- [x] Task 3: 实现文章抓取与正文解析
  - [x] SubTask 3.1: 实现文章页面获取与专栏文章列表发现
  - [x] SubTask 3.2: 实现正文 DOM 解析与结构化中间表示
  - [x] SubTask 3.3: 保障标题、段落、代码块、引用、列表等块级语义保真

- [x] Task 4: 实现图片下载、本地化与资源管理
  - [x] SubTask 4.1: 提取正文图片资源并建立下载队列
  - [x] SubTask 4.2: 实现断点续传（含进度元数据存储）
  - [x] SubTask 4.3: 实现图片去重（基于内容哈希或稳定标识）
  - [x] SubTask 4.4: 替换 Markdown 图片链接为本地相对路径

- [x] Task 5: 实现 Markdown 渲染与文件输出
  - [x] SubTask 5.1: 将结构化内容转换为 GFM 兼容 Markdown
  - [x] SubTask 5.2: 实现文件命名规则与冲突处理
  - [x] SubTask 5.3: 支持单篇导出与批量导出流程编排

- [x] Task 6: 实现错误处理、日志与重试机制
  - [x] SubTask 6.1: 设计错误分类与统一错误码
  - [x] SubTask 6.2: 实现结构化日志与运行摘要输出
  - [x] SubTask 6.3: 实现网络与解析失败的可配置重试策略

- [x] Task 7: 完成交付物与质量保障
  - [x] SubTask 7.1: 编写单元测试（解析、渲染、路径替换、去重）
  - [x] SubTask 7.2: 编写集成测试（登录、单篇导出、批量导出、失败重试）
  - [x] SubTask 7.3: 编写使用文档（安装、配置、命令示例、故障排查）
  - [x] SubTask 7.4: 产出 macOS 可执行程序并完成本地验证

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 3 and Task 4
- Task 6 depends on Task 2 and Task 5
- Task 7 depends on Task 1, Task 5, and Task 6

# Parallelization Notes
- 在 Task 1 完成后，Task 2 与日志基础设施中的部分设计可并行准备。
- 在 Task 3 完成后，Task 4 与 Task 5 可由不同子代理并行开发后再集成。
- Task 7 可在 Task 5 稳定后先并行编写文档与部分单元测试。
