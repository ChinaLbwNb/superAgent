from pathlib import Path


class SkillsLoader:
    """
    技能加载器。
    扫描 workspace/skills/ 下所有子目录中的 SKILL.md 文件，
    将内容拼接后注入到系统提示词。
    """

    def __init__(self, workspace: str):
        self.skills_dir = Path(workspace) / "skills"

    def load_all(self) -> dict[str, str]:
        """返回 {skill_name: content} 字典。"""
        skills = {}
        if not self.skills_dir.exists():
            return skills
        for skill_md in sorted(self.skills_dir.rglob("SKILL.md")):
            name = skill_md.parent.name
            skills[name] = skill_md.read_text(encoding="utf-8").strip()
        return skills

    def get_context(self) -> str:
        skills = self.load_all()
        if not skills:
            return ""
        parts = ["# Skills"]
        for name, content in skills.items():
            parts.append(f"## {name}\n{content}")
        return "\n\n".join(parts)
