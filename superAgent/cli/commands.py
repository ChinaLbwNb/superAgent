import asyncio
import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.panel import Panel

from config.loader import load_config, save_config
from agent.loop import AgentLoop
from bus.queue import MessageBus, Message

app = typer.Typer(help="superAgent - Your personal AI agent", add_completion=False)
console = Console()


def _get_agent(config_path: str | None = None) -> AgentLoop:
    cfg = load_config(Path(config_path) if config_path else None)
    return AgentLoop(cfg)


@app.command()
def chat(
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
    config: str = typer.Option(None, "--config", "-c", help="Path to config.json"),
):
    """Start an interactive chat session with superAgent."""
    agent = _get_agent(config)
    console.print(Panel(
        "[bold cyan]superAgent[/bold cyan] — Type [bold]exit[/bold] or Ctrl+C to quit",
        expand=False
    ))

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if user_input.strip().lower() in ("exit", "quit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break
        if not user_input.strip():
            continue

        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            response = asyncio.run(agent.process(user_input, session_id=session))

        console.print(Panel(Markdown(response), title="[bold blue]superAgent[/bold blue]", expand=False))


@app.command()
def run(
    message: str = typer.Argument(..., help="Message to send to the agent"),
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
    config: str = typer.Option(None, "--config", "-c", help="Path to config.json"),
):
    """Send a single message to superAgent and print the response."""
    agent = _get_agent(config)
    response = asyncio.run(agent.process(message, session_id=session))
    console.print(Markdown(response))


@app.command()
def configure(
    model: str = typer.Option(None, help="Model name"),
    api_key: str = typer.Option(None, help="API key"),
    api_base: str = typer.Option(None, help="API base URL"),
    provider: str = typer.Option(None, help="Provider: openai or anthropic"),
    workspace: str = typer.Option(None, help="Workspace directory"),
    telegram_token: str = typer.Option(None, help="Telegram bot token"),
):
    """Update config.json settings."""
    cfg = load_config()
    if model:
        cfg.model = model
    if api_key:
        cfg.api_key = api_key
    if api_base:
        cfg.api_base = api_base
    if provider:
        cfg.provider = provider
    if workspace:
        cfg.workspace = workspace
    if telegram_token:
        cfg.telegram.token = telegram_token
    save_config(cfg)
    console.print("[green]Config updated.[/green]")
    # 隐藏 api_key 敏感信息
    data = cfg.model_dump()
    data["api_key"] = "***" if data["api_key"] else ""
    console.print(json.dumps(data, indent=2, ensure_ascii=False))


@app.command()
def sessions():
    """List all saved sessions."""
    from session.manager import SessionManager
    cfg = load_config()
    sm = SessionManager(f"{cfg.workspace}/.superagent/sessions")
    items = sm.list_sessions()
    if items:
        for s in items:
            console.print(f"  • {s}")
    else:
        console.print("[dim](no sessions found)[/dim]")


@app.command()
def clear(
    session: str = typer.Argument("default", help="Session ID to clear"),
    config: str = typer.Option(None, "--config", "-c", help="Path to config.json"),
):
    """Clear a session's history."""
    from session.manager import SessionManager
    cfg = load_config(Path(config) if config else None)
    sm = SessionManager(f"{cfg.workspace}/.superagent/sessions")
    sm.clear(session)
    console.print(f"[green]Session '{session}' cleared.[/green]")


@app.command()
def telegram(
    config: str = typer.Option(None, "--config", "-c", help="Path to config.json"),
):
    """Start superAgent as a Telegram bot."""
    cfg = load_config(Path(config) if config else None)
    if not cfg.telegram.token:
        console.print("[red]Error: telegram.token is not set in config.json[/red]")
        raise typer.Exit(1)

    from channels.telegram import TelegramChannel
    agent = AgentLoop(cfg)
    bus = MessageBus()

    async def agent_worker():
        while True:
            msg = await bus.receive()
            response = await agent.process(msg.content, session_id=msg.session_id)
            await bus.reply(Message(session_id=msg.session_id, content=response, role="assistant"))

    async def main():
        channel = TelegramChannel(
            bus=bus,
            token=cfg.telegram.token,
            allowed_users=cfg.telegram.allowed_users or None,
        )
        await asyncio.gather(
            channel.start(),
            agent_worker(),
        )

    console.print(f"[cyan]Starting Telegram bot...[/cyan]")
    asyncio.run(main())


@app.command()
def serve(
    config: str = typer.Option(None, "--config", "-c", help="Path to config.json"),
):
    """Start superAgent with cron + heartbeat services enabled."""
    cfg = load_config(Path(config) if config else None)
    agent = AgentLoop(cfg)

    async def run_task(task_text: str, job_name: str = "heartbeat") -> str:
        return await agent.process(task_text, session_id=f"auto_{job_name}")

    async def main():
        tasks = []
        if cfg.cron.enabled:
            from cron.service import CronService
            cron = CronService(cfg.workspace, handler=run_task)
            tasks.append(cron.start())
            console.print("[cyan]CronService enabled.[/cyan]")

        if cfg.heartbeat.enabled:
            from heartbeat.service import HeartbeatService
            hb = HeartbeatService(
                cfg.workspace,
                handler=lambda t: run_task(t, "heartbeat"),
                interval_seconds=cfg.heartbeat.interval_seconds,
            )
            tasks.append(hb.start())
            console.print(f"[cyan]HeartbeatService enabled (every {cfg.heartbeat.interval_seconds}s).[/cyan]")

        if not tasks:
            console.print("[yellow]No background services enabled. Enable cron or heartbeat in config.json.[/yellow]")
            return

        await asyncio.gather(*tasks)

    asyncio.run(main())
