# superAgent 使用指南

个人 AI 助手，支持工具调用、记忆管理、多渠道接入。

## 快速开始

```bash
# 进入项目目录
cd ~/Desktop/superagent

# 安装依赖
pip install -r requirements.txt

# 启动交互式聊天
python main.py chat
```

## 命令列表

### chat - 交互式聊天

```bash
python main.py chat
python main.py chat -s my_session    # 指定会话 ID
python main.py chat -c /path/to/config.json  # 指定配置文件
```

交互中输入 `exit` 或 `quit` 退出。

### run - 单次对话

```bash
python main.py run "你的问题"
python main.py run "读取 config.json" -s my_session
```

### configure - 修改配置

```bash
# 设置模型
python main.py configure --model "deepseek-ai/DeepSeek-V3"

# 设置 API Key
python main.py configure --api-key "sk-xxx"

# 设置 API Base URL
python main.py configure --api-base "https://api.siliconflow.cn/v1"

# 设置提供商
python main.py configure --provider "openai"

# 设置工作空间
python main.py configure --workspace "/path/to/workspace"

# 设置 Telegram Token
python main.py configure --telegram-token "your-bot-token"

# 组合使用
python main.py configure --model "gpt-4o" --provider "openai" --api-key "sk-xxx"
```

### sessions - 查看会话列表

```bash
python main.py sessions
```

### clear - 清除会话历史

```bash
python main.py clear              # 清除默认会话
python main.py clear my_session   # 清除指定会话
```

### telegram - 启动 Telegram 机器人

```bash
python main.py telegram
```

需要先在 `config.json` 中配置 `telegram.token`。

### serve - 启动后台服务

```bash
python main.py serve
```

启动定时任务（cron）和心跳服务（heartbeat），需在 `config.json` 中启用。

## 配置说明

编辑 `config.json`：

```json
{
  "model": "Pro/zai-org/GLM-5",
  "api_key": "your-api-key",
  "api_base": "https://api.siliconflow.cn/v1",
  "provider": "openai",
  "max_tokens": 4096,
  "temperature": 0.7,
  "max_tool_iterations": 20,
  "workspace": ".",
  "restrict_to_workspace": true,
  "system_prompt": "You are superAgent...",
  "telegram": {
    "token": "",
    "allowed_users": []
  },
  "cron": {
    "enabled": false
  },
  "heartbeat": {
    "enabled": false,
    "interval_seconds": 300
  }
}
```

| 字段 | 说明 |
|------|------|
| `model` | 模型名称 |
| `api_key` | API 密钥 |
| `api_base` | API 地址 |
| `provider` | 协议类型：`openai` 或 `anthropic` |
| `max_tokens` | 最大输出 token |
| `temperature` | 温度参数 (0-1) |
| `max_tool_iterations` | 工具调用最大轮数 |
| `workspace` | 工作空间目录 |
| `restrict_to_workspace` | 是否限制只能访问工作空间内的文件 |

## 可用工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `read_file` | 读取文件 | "读取 config.json" |
| `write_file` | 写入文件 | "创建 test.txt，内容是 hello" |
| `list_dir` | 列出目录 | "列出当前目录" |
| `edit_file` | 编辑文件 | "把 config.json 里的 temperature 改成 0.5" |
| `shell` | 执行命令 | "运行 pip list" |
| `screenshot` | 截图 | "帮我截图" |
| `web_search` | 网络搜索 | "搜索 Python 最新版本" |
| `web_fetch` | 获取网页 | "获取 https://python.org 的内容" |
| `web_request` | HTTP 请求 | "调用 API 获取数据" |
| `save_memory` | 保存记忆 | "记住：我喜欢用中文" |
| `read_memory` | 读取记忆 | "你还记得什么" |
| `save_today_note` | 保存今日笔记 | "记录今天完成了任务 A" |
| `spawn_agent` | 启动子代理 | （内部使用） |
| `get_agent_result` | 获取子代理结果 | （内部使用） |

## 示例对话

```bash
$ python main.py chat

You: 列出当前目录的文件

┌─ 🧠 Thinking ─┐
│ Iteration 1   │
└───────────────┘
┌── Decision ───┐
│ 调用 1 个工具 │
└───────────────┘
┌───────────┬─────────────────┐
│ list_dir  │ {"path": "."}   │
└───────────┴─────────────────┘
...

You: 读取 config.json，告诉我模型是什么

┌─ 🧠 Thinking ─┐
│ Iteration 1   │
└───────────────┘
┌───────────┬───────────────────────┐
│ read_file │ {"path": "config.json"}│
└───────────┴───────────────────────┘
...

You: exit
Goodbye!
```

## 注意事项

1. **模型支持**：部分模型不支持工具调用（如 GLM-5），会直接文本回复
2. **工作空间限制**：默认只能访问工作空间内的文件，可在配置中关闭
3. **会话持久化**：对话历史保存在 `.superagent/sessions/` 目录
4. **截图保存**：截图保存在 `.superagent/screenshots/` 目录

## 推荐模型

以下模型支持工具调用（Function Calling）：

| 平台 | 模型 |
|------|------|
| SiliconFlow | `deepseek-ai/DeepSeek-V3` |
| SiliconFlow | `Qwen/Qwen2.5-72B-Instruct` |
| OpenAI | `gpt-4o` |
| Anthropic | `claude-3-opus` |

## 项目结构

```
superAgent/
├── agent/           # Agent 核心逻辑
│   ├── loop.py      # 主循环
│   ├── context.py   # 上下文构建
│   ├── memory.py    # 记忆管理
│   ├── skills.py    # 技能加载
│   └── tools/       # 工具集
├── providers/       # LLM 调用
├── session/         # 会话管理
├── config/          # 配置管理
├── channels/        # 通信渠道
├── cli/             # 命令行接口
├── skills/          # 技能目录
├── main.py          # 入口
└── config.json      # 配置文件
```
