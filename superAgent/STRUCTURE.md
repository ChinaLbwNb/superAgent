superAgent/
├── agent/
│   ├── loop.py              # Agent 主循环（含 tool 执行、历史持久化）
│   ├── context.py           # 上下文构建（system prompt + memory + skills）
│   ├── memory.py            # 长期记忆 + 每日笔记管理
│   ├── skills.py            # 技能文件加载器（SKILL.md）
│   ├── subagent.py          # 子代理后台执行器
│   └── tools/
│       ├── base.py          # 工具基类
│       ├── registry.py      # 工具注册表
│       ├── filesystem.py    # read/write/edit/list/shell 工具
│       ├── memory_tools.py  # save_memory / read_memory / save_today_note
│       └── subagent_tools.py# spawn_agent / get_agent_result
├── providers/
│   ├── llm.py               # litellm 统一调用（OpenAI + Anthropic）
│   └── schema.py            # LLMResponse
├── session/
│   └── manager.py           # JSONL 会话持久化
├── config/
│   ├── loader.py            # 配置加载/保存
│   └── schema.py            # Config（含 telegram/cron/heartbeat）
├── bus/
│   └── queue.py             # 异步消息总线
├── channels/
│   ├── base.py              # BaseChannel 抽象类
│   └── telegram.py          # Telegram channel
├── cron/
│   └── service.py           # 定时任务（解析 CRON.md）
├── heartbeat/
│   └── service.py           # 心跳服务（读取 HEARTBEAT.md）
├── skills/                  # 技能目录（每个子目录放一个 SKILL.md）
├── AGENTS.md                # Agent 行为说明
├── MEMORY.md                # 长期记忆（agent 可写）
├── HEARTBEAT.md             # 心跳任务清单
├── CRON.md                  # 定时任务配置
├── config.json              # 用户配置
├── requirements.txt
└── main.py                  # 入口
