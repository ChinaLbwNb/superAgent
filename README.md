# superAgent

本地优先的个人 AI 助手，支持工具调用、记忆、会话持久化，以及 CLI / Telegram / 定时任务接入。  
Local-first personal AI assistant with tool calling, memory, session persistence, and CLI / Telegram / scheduled-task integrations.

## Why superAgent

`superAgent` is a lightweight Python project for people who want an assistant that can do more than chat. It can read and edit files in your workspace, run shell commands, keep long-term notes, and stay available through multiple interaction channels.

它适合想在本地工作流里接入 AI 助手的个人开发者、效率工具爱好者，或者想基于一个清晰骨架继续扩展自己 agent 系统的人。

## Highlights

- CLI-first interactive assistant for daily local tasks
- Tool calling for file operations, shell commands, screenshots, and web access
- Session persistence for continuing conversations across runs
- Built-in memory and daily notes
- Optional Telegram channel for remote access
- Background automation via `cron` and `heartbeat`
- Skill folder structure for prompt and workflow extension

## Quick Start

### 1. Install dependencies / 安装依赖

```bash
pip install -r requirements.txt
```

### 2. Configure the model / 配置模型

Edit `config.json` and fill in your model settings:

```json
{
  "model": "Pro/zai-org/GLM-5",
  "api_key": "your-api-key",
  "api_base": "https://api.siliconflow.cn/v1",
  "provider": "openai",
  "workspace": ".",
  "restrict_to_workspace": true
}
```

You can also update common fields from the CLI:

```bash
python main.py configure --model "gpt-4o" --provider "openai" --api-key "sk-xxx"
```

### 3. Start chatting / 开始使用

```bash
python main.py chat
```

Run a single prompt:

```bash
python main.py run "Read config.json and tell me which model is configured."
```

## What It Can Do

### Core capabilities / 核心能力

- Read, write, edit, and list files inside the workspace
- Execute shell commands from the project workspace
- Save long-term memory to `MEMORY.md`
- Save daily notes for lightweight work logging
- Search the web, fetch web pages, and send HTTP requests
- Capture screenshots to `.superagent/screenshots/`
- Persist chat history under `.superagent/sessions/`

### Interaction modes / 使用方式

- `chat`: interactive conversation in the terminal
- `run`: one-shot task execution
- `telegram`: run the assistant as a Telegram bot
- `serve`: start background services such as cron and heartbeat

## Command Overview

```bash
python main.py chat
python main.py chat -s my_session
python main.py run "List files in the current directory"
python main.py configure --model "deepseek-ai/DeepSeek-V3"
python main.py sessions
python main.py clear my_session
python main.py telegram
python main.py serve
```

## Example Use Cases

- Manage local project files through natural language
- Keep personal notes and preferences in agent memory
- Run recurring prompts from `CRON.md`
- Track simple recurring tasks from `HEARTBEAT.md`
- Connect the same assistant to a Telegram bot for lightweight remote access

## Configuration

Main settings live in `config.json`.

| Field | Description |
|------|------|
| `model` | Model name |
| `api_key` | API key |
| `api_base` | API base URL |
| `provider` | Provider type, currently `openai` or `anthropic` |
| `max_tokens` | Maximum output tokens |
| `temperature` | Sampling temperature |
| `max_tool_iterations` | Maximum tool-calling loop iterations |
| `workspace` | Workspace directory |
| `restrict_to_workspace` | Limit file access to the workspace |
| `telegram.token` | Telegram bot token |
| `telegram.allowed_users` | Optional allowlist for Telegram users |
| `cron.enabled` | Enable scheduled task service |
| `heartbeat.enabled` | Enable heartbeat service |
| `heartbeat.interval_seconds` | Heartbeat polling interval |

## Project Structure

```text
superAgent/
├── agent/        # Core agent loop, memory, context, tools, subagent runner
├── cli/          # Typer CLI commands
├── providers/    # LLM provider adapter layer
├── config/       # Config loading and schemas
├── session/      # Session persistence
├── channels/     # External channels such as Telegram
├── cron/         # Scheduled task service
├── heartbeat/    # Heartbeat task service
├── skills/       # Extendable skill definitions
├── config.json   # Runtime configuration
├── MEMORY.md     # Long-term memory store
└── main.py       # Application entrypoint
```

## Notes

- This project is designed as a personal, local-first assistant rather than a hardened multi-user platform.
- Tool availability depends on the model/provider you configure.
- Some internal capabilities, such as subagent helpers, are implementation details and are not positioned as stable public-facing features yet.
- Session data and generated files are stored in the workspace under `.superagent/`.

## Development

This repository currently exposes a runnable codebase and usage documentation, but it does not yet include a formal test suite, packaging setup, or CI workflow. If you plan to publish or extend it, the current structure is a good starting point for:

- adding provider integrations
- expanding the tool registry
- improving safety constraints around shell and file access
- evolving the skill and automation system
