# -*- coding: utf-8 -*-
"""把本仓库 skills/ 下的技能安装到本机 DSH 用户级 skills 目录。

用法::

    python install.py                 # 安装全部技能
    python install.py data-processing-pattern   # 只装指定的一个
    python install.py --link          # 用软链接（改仓库即生效，Windows 需开发者模式）
    python install.py --list          # 只列出仓库里的技能，不安装

目标目录按优先级：
1. 环境变量 DSH_SKILLS_DIR
2. ~/.agents/skills
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_SRC = REPO_ROOT / "skills"


def target_dir() -> Path:
    env = os.environ.get("DSH_SKILLS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".agents" / "skills").resolve()


def discover_skills() -> list[Path]:
    if not SKILLS_SRC.is_dir():
        return []
    out = []
    for child in sorted(SKILLS_SRC.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            out.append(child)
    return out


def read_skill_name(skill_dir: Path) -> str:
    """从 SKILL.md 的 frontmatter 里取 name，取不到就用目录名。"""
    try:
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return skill_dir.name
    if text.startswith("---"):
        for line in text.splitlines()[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                return line.split(":", 1)[1].strip().strip("'\"")
    return skill_dir.name


def install_one(skill_dir: Path, dest_root: Path, use_link: bool) -> str:
    name = read_skill_name(skill_dir)
    dest = dest_root / name

    if dest.exists() or dest.is_symlink():
        if dest.is_symlink() or dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest)

    dest_root.mkdir(parents=True, exist_ok=True)

    if use_link:
        try:
            os.symlink(skill_dir, dest, target_is_directory=True)
            return f"[LINK] {name} -> {skill_dir}"
        except (OSError, NotImplementedError) as exc:
            print(f"[WARN] 软链接失败（{exc}），改为复制")

    shutil.copytree(
        skill_dir,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
    )
    return f"[COPY] {name} -> {dest}"


def main() -> int:
    ap = argparse.ArgumentParser(description="安装本仓库的技能到本机 DSH skills 目录")
    ap.add_argument("names", nargs="*", help="只安装指定技能（目录名或 frontmatter name）")
    ap.add_argument("--link", action="store_true", help="用软链接代替复制")
    ap.add_argument("--list", action="store_true", help="只列出技能，不安装")
    ap.add_argument("--dest", help="覆盖目标目录")
    args = ap.parse_args()

    skills = discover_skills()
    if not skills:
        print(f"[ERROR] 在 {SKILLS_SRC} 下没找到任何含 SKILL.md 的技能目录")
        return 1

    if args.list:
        print(f"仓库技能目录：{SKILLS_SRC}")
        for s in skills:
            print(f"  - {read_skill_name(s)}  ({s.name})")
        return 0

    dest_root = Path(args.dest).expanduser().resolve() if args.dest else target_dir()

    selected = skills
    if args.names:
        wanted = {n.strip() for n in args.names if n.strip()}
        selected = [s for s in skills if read_skill_name(s) in wanted or s.name in wanted]
        missing = wanted - {read_skill_name(s) for s in selected} - {s.name for s in selected}
        if missing:
            print(f"[ERROR] 仓库里没有这些技能：{', '.join(sorted(missing))}")
            print(f"        可用：{', '.join(read_skill_name(s) for s in skills)}")
            return 1

    print(f"目标目录：{dest_root}")
    print(f"待安装：{len(selected)} 个技能")
    print("")

    for s in selected:
        print(install_one(s, dest_root, args.link))

    print("")
    print("[OK] 安装完成。重启 DSH 或新开会话后生效。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
