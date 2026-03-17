import json
from pathlib import Path
from .schema import Config

_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config(config_path: Path | None = None) -> Config:
    path = config_path or _DEFAULT_CONFIG_PATH
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return Config.model_validate(data)
    return Config()


def save_config(config: Config, config_path: Path | None = None) -> None:
    path = config_path or _DEFAULT_CONFIG_PATH
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
