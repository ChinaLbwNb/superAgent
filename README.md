diff --git a/C:\Users\1\Desktop\superAgent\README.md b/C:\Users\1\Desktop\superAgent\README.md
new file mode 100644
--- /dev/null
+++ b/C:\Users\1\Desktop\superAgent\README.md
@@ -0,0 +1,156 @@
+# superAgent
+
+本地优先的个人 AI 助手，支持工具调用、记忆、会话持久化，以及 CLI / Telegram / 定时任务接入。  
+Local-first personal AI assistant with tool calling, memory, session persistence, and CLI / Telegram / scheduled-task integrations.
+
+## Why superAgent
+
+`superAgent` is a lightweight Python project for people who want an assistant that can do more than chat. It can read and edit files in your workspace, run shell commands, keep long-term notes, and stay available through multiple interaction channels.
+
+它适合想在本地工作流里接入 AI 助手的个人开发者、效率工具爱好者，或者想基于一个清晰骨架继续扩展自己 agent 系统的人。
+
+## Highlights
+
+- CLI-first interactive assistant for daily local tasks
+- Tool calling for file operations, shell commands, screenshots, and web access
+- Session persistence for continuing conversations across runs
+- Built-in memory and daily notes
+- Optional Telegram channel for remote access
+- Background automation via `cron` and `heartbeat`
+- Skill folder structure for prompt and workflow extension
+
+## Quick Start
+
+### 1. Install dependencies / 安装依赖
+
+```bash
+pip install -r requirements.txt
+```
+
+### 2. Configure the model / 配置模型
+
+Edit `config.json` and fill in your model settings:
+
+```json
+{
+  "model": "Pro/zai-org/GLM-5",
+  "api_key": "your-api-key",
+  "api_base": "https://api.siliconflow.cn/v1",
+  "provider": "openai",
+  "workspace": ".",
+  "restrict_to_workspace": true
+}
+```
+
+You can also update common fields from the CLI:
+
+```bash
+python main.py configure --model "gpt-4o" --provider "openai" --api-key "sk-xxx"
+```    ```
+
+### 3. Start chatting / 开始使用
+
+```bash
+python main.py chat
+```
+
+Run a single prompt:
+
+```bash
+python main.py run "Read config.json and tell me which model is configured."
+```
+
+## What It Can Do
+
+### Core capabilities / 核心能力
+
+- Read, write, edit, and list files inside the workspace
+- Execute shell commands from the project workspace
+- Save long-term memory to `MEMORY.md`
+- Save daily notes for lightweight work logging
+- Search the web, fetch web pages, and send HTTP requests
+- Capture screenshots to `.superagent/screenshots/`
+- Persist chat history under `.superagent/sessions/`
+
+### Interaction modes / 使用方式
+
+- `chat`: interactive conversation in the terminal
+- `run`: one-shot task execution
+- `telegram`: run the assistant as a Telegram bot
+- `serve`: start background services such as cron and heartbeat
+
+## Command Overview
+
+```bash
+python main.py chat
+python main.py chat -s my_session
+python main.py run "List files in the current directory"
+python main.py configure --model "deepseek-ai/DeepSeek-V3"
+python main.py sessions
+python main.py clear my_session
+python main.py telegram
+python main.py serve
+```    ```
+
+## Example Use Cases
+
+- Manage local project files through natural language
+- Keep personal notes and preferences in agent memory
+- Run recurring prompts from `CRON.md`
+- Track simple recurring tasks from `HEARTBEAT.md`
+- Connect the same assistant to a Telegram bot for lightweight remote access
+
+## Configuration
+
+Main settings live in `config.json`.
+
+| Field | Description |
+|------|------|
+| `model` | Model name |
+| `api_key` | API key |
+| `api_base` | API base URL || ' api_base ' | API基础URL |
+| `provider` | Provider type, currently `openai` or `anthropic` || `provider` |提供程序类型，当前为`openai`或`anthropic` |
+| `max_tokens` | Maximum output tokens || `max_tokens` |最大输出token |
+| `temperature` | Sampling temperature || ' temperature ' |采样温度|
+| `max_tool_iterations` | Maximum tool-calling loop iterations |
+| `workspace` | Workspace directory |
+| `restrict_to_workspace` | Limit file access to the workspace |
+| `telegram.token` | Telegram bot token |
+| `telegram.allowed_users` | Optional allowlist for Telegram users |# GitHub README的重写计划
+| `cron.enabled` | Enable scheduled task service |
+| `heartbeat.enabled` | Enable heartbeat service |
+| `heartbeat.interval_seconds` | Heartbeat polling interval |
+
+## Project Structure   ##项目结构
+
+```text   ' ' '文本
+superAgent/
+├── agent/        # Core agent loop, memory, context, tools, subagent runner├──agent/ #核心agent循环，内存，上下文，工具，子agent运行器
+├── cli/          # Typer CLI commands├──cli/ #输入cli命令
+├── providers/    # LLM provider adapter layer├──providers/ # LLM provider适配器层
+├── config/       # Config loading and schemas├──config/ #配置加载和模式
+├── session/      # Session persistence├──session/ #会话持久化
+├── channels/     # External channels such as Telegram├──channels/ # Telegram等外部通道
+├── cron/         # Scheduled task service├──cron/ #定时任务服务
+├── heartbeat/    # Heartbeat task service├──heartbeat/ #心跳任务服务
+├── skills/       # Extendable skill definitions├──skills/ #可扩展技能定义
+├── config.json   # Runtime configuration├──配置。json #运行时配置
+├── MEMORY.md     # Long-term memory store├──记忆。md#长期记忆存储
+└── main.py       # Application entrypoint──main.py #应用入口点
+```    ```
+
+## Notes   # #笔记
+
+- This project is designed as a personal, local-first assistant rather than a hardened multi-user platform.-该项目被设计为一个个人的、本地优先的助手，而不是一个强化的多用户平台。
+- Tool availability depends on the model/provider you configure.-工具的可用性取决于你配置的模型/提供者。
+- Some internal capabilities, such as subagent helpers, are implementation details and are not positioned as stable public-facing features yet.-一些内部功能，例如子代理助手，是实现细节，还没有定位为稳定的面向公众的功能。
+- Session data and generated files are stored in the workspace under `.superagent/`.-会话数据和生成的文件存储在`.superagent/`下的工作空间中。
+
+## Development   # #发展
+
+This repository currently exposes a runnable codebase and usage documentation, but it does not yet include a formal test suite, packaging setup, or CI workflow. If you plan to publish or extend it, the current structure is a good starting point for:这个存储库目前公开了一个可运行的代码库和使用文档，但是它还没有包含正式的测试套件、打包设置或CI工作流。如果你计划发布或扩展它，当前的结构是一个很好的起点：
+
+- adding provider integrations-添加provider集成
+- expanding the tool registry-展开工具注册表
+- improving safety constraints around shell and file access-改进shell和文件访问的安全性约束
+- evolving the skill and automation system-改进技能和自动化系统
