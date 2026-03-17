from pathlib import Path
from config.schema import Config
from agent.memory import MemoryManager
from agent.skills import SkillsLoader


class ContextBuilder:
    """
    上下文构建器：将 system prompt、AGENTS.md、记忆、技能、
    历史消息、当前用户输入组装成发给 LLM 的 messages 列表。
    """

    def __init__(self, config: Config):
        self.config = config
        self.memory = MemoryManager(config.workspace)
        self.skills = SkillsLoader(config.workspace)

    def build_system_prompt(self) -> str:
        parts = [self.config.system_prompt]

        # 工具调用指导（帮助模型正确使用工具）
        tool_instruction = """# Tool Usage Instructions

You have access to tools that can perform real actions. When you need to use a tool:

1. **DO NOT** pretend to have used a tool by writing text like "Tool executed successfully"
2. **DO** call the appropriate tool by returning a tool_calls response
3. Wait for the tool result, then continue your response based on the actual result

Available tools include:
- read_file: Read file contents
- write_file: Write content to a file
- list_dir: List directory contents
- edit_file: Edit a file
- shell: Execute shell commands
- screenshot: Take a screenshot
- save_memory / read_memory: Memory management
- spawn_agent / get_agent_result: Sub-agent management

When user asks you to perform an action (read file, take screenshot, etc.), you MUST call the corresponding tool rather than simulating the result in text."""

        parts.append(tool_instruction)

        # AGENTS.md：agent 行为说明
        agents_md = Path(self.config.workspace) / "AGENTS.md"
        if agents_md.exists():
            parts.append("# Agent Instructions\n" + agents_md.read_text(encoding="utf-8").strip())

        # 记忆（长期 + 今日）
        memory_ctx = self.memory.get_context()
        if memory_ctx:
            parts.append(memory_ctx)

        # 技能
        skills_ctx = self.skills.get_context()
        if skills_ctx:
            parts.append(skills_ctx)

        return "\n\n".join(parts)

    def build(self, history: list[dict], user_input: str) -> list[dict]:
        system_prompt = self.build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        return messages
