import os
from typing import Any
import litellm
from litellm import completion

from config.schema import Config
from .schema import LLMResponse

# 关闭 litellm 的冗余日志
litellm.suppress_debug_info = True


class LLMProvider:
    """
    统一的 LLM 调用层，兼容 OpenAI 协议和 Anthropic 协议。
    通过 litellm 路由，用户只需配置 provider / api_key / api_base / model。
    """

    def __init__(self, config: Config):
        self.config = config
        self._setup_env()

    def _setup_env(self):
        cfg = self.config
        if cfg.provider == "anthropic":
            if cfg.api_key:
                # 支持自定义 Anthropic 兼容端点（如 SiliconFlow）
                os.environ["ANTHROPIC_API_KEY"] = cfg.api_key
                os.environ["ANTHROPIC_AUTH_TOKEN"] = cfg.api_key
            if cfg.api_base:
                os.environ["ANTHROPIC_BASE_URL"] = cfg.api_base
        else:
            # openai 兼容（包括自定义 url）
            if cfg.api_key:
                os.environ["OPENAI_API_KEY"] = cfg.api_key
            if cfg.api_base:
                os.environ["OPENAI_API_BASE"] = cfg.api_base

    def _build_model_string(self) -> str:
        cfg = self.config
        if cfg.provider == "anthropic":
            # litellm 识别 "anthropic/claude-xxx" 或直接 "claude-xxx"
            if not cfg.model.startswith("anthropic/"):
                return f"anthropic/{cfg.model}"
            return cfg.model
        elif cfg.api_base:
            # 自定义 OpenAI 兼容接口
            return f"openai/{cfg.model}"
        else:
            return cfg.model

    def _build_kwargs(self) -> dict[str, Any]:
        cfg = self.config
        kwargs: dict[str, Any] = {}
        if cfg.provider != "anthropic" and cfg.api_base:
            kwargs["api_base"] = cfg.api_base
        if cfg.provider != "anthropic" and cfg.api_key:
            kwargs["api_key"] = cfg.api_key
        return kwargs

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> LLMResponse:
        cfg = self.config
        model = self._build_model_string()
        extra = self._build_kwargs()

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens or cfg.max_tokens,
            "temperature": temperature if temperature is not None else cfg.temperature,
            **extra,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = completion(**kwargs)

        choice = response.choices[0]
        message = choice.message
        stop_reason = choice.finish_reason or "end_turn"

        content = message.content or ""

        tool_calls = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                import json
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })

        usage = response.usage or {}
        input_tokens = getattr(usage, "prompt_tokens", 0) or 0
        output_tokens = getattr(usage, "completion_tokens", 0) or 0

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
