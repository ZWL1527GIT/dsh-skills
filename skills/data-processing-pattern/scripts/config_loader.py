# -*- coding: utf-8 -*-
"""加载「1配置文件」中的 INI 数据库连接配置。

项目里的 ini 文件命名约定：

    配置文件-<环境>-<库说明>.ini

每个 ini 文件都有 ``[database]`` 段，包含
host / port / user / password / database / charset。

用法::

    from 工具.config_loader import load_db_config, connect

    # 方式 1：按完整文件名
    cfg = load_db_config("配置文件-1-本地.ini")

    # 方式 2：按关键字（在 1配置文件/ 下找第一个文件名包含关键字的 ini）
    cfg = load_db_config("本地")
    cfg = load_db_config("为知V2-供应链")

    # 直接拿 pymysql 连接
    conn = connect("本地")
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        print(cur.fetchall())
    conn.close()
"""
from __future__ import annotations

import configparser
import os
import sys
from pathlib import Path
from typing import Any

# Windows GBK 控制台兼容
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import pymysql
from pymysql.cursors import DictCursor

# 项目根（本文件在 工具/ 下，所以 parents[1] 是项目根）
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "1配置文件"


def list_config_files() -> list[Path]:
    """返回 1配置文件/ 下所有 ini 配置文件（按文件名排序）。"""
    if not CONFIG_DIR.exists():
        return []
    return sorted(CONFIG_DIR.glob("*.ini"))


def _resolve_config_path(name_or_path: str) -> Path:
    """把用户的输入解析成一个真实存在的 ini 路径。

    支持三种写法：
      1. 完整文件名：``配置文件-1-本地.ini``
      2. 不带后缀：  ``配置文件-1-本地``
      3. 关键字：    ``本地`` / ``为知V2-供应链`` —— 在 CONFIG_DIR 下找
                     第一个文件名包含该关键字的 ini
    """
    # 写法 1：本身就是一个存在的路径
    p = Path(name_or_path)
    if p.is_file():
        return p

    # 写法 2：CONFIG_DIR 下的相对文件名
    candidate = CONFIG_DIR / name_or_path
    if candidate.is_file():
        return candidate
    if not name_or_path.lower().endswith(".ini"):
        candidate = CONFIG_DIR / f"{name_or_path}.ini"
        if candidate.is_file():
            return candidate

    # 写法 3：关键字匹配
    hits = [f for f in list_config_files() if name_or_path in f.name]
    if not hits:
        available = [f.name for f in list_config_files()]
        raise FileNotFoundError(
            f"在 {CONFIG_DIR} 找不到匹配 {name_or_path!r} 的配置文件。\n"
            f"可用配置：{available}"
        )
    if len(hits) > 1:
        names = [f.name for f in hits]
        raise ValueError(
            f"{name_or_path!r} 匹配到多个配置文件，请写得更具体：{names}"
        )
    return hits[0]


def load_db_config(name_or_path: str) -> dict[str, Any]:
    """读取 ini 配置，返回 pymysql 连接参数字典。

    返回字段：host / port / user / password / database / charset / _source
    （``_source`` 是 ini 文件路径，便于排查）
    """
    ini_path = _resolve_config_path(name_or_path)

    parser = configparser.ConfigParser()
    parser.read(ini_path, encoding="utf-8")

    if "database" not in parser:
        raise KeyError(f"{ini_path} 缺少 [database] 段")

    sec = parser["database"]
    cfg: dict[str, Any] = {
        "host": sec.get("host", "127.0.0.1"),
        "port": sec.getint("port", 3306),
        "user": sec.get("user", ""),
        "password": sec.get("password", ""),
        "database": sec.get("database", ""),
        "charset": sec.get("charset", "utf8mb4"),
    }
    cfg["_source"] = str(ini_path)
    return cfg


def connect(name_or_path: str, **overrides: Any) -> pymysql.connections.Connection:
    """根据 ini 配置建立一个 pymysql 连接（DictCursor）。"""
    cfg = load_db_config(name_or_path)
    cfg.pop("_source", None)
    cfg.update(overrides)
    cfg.setdefault("cursorclass", DictCursor)
    cfg.setdefault("autocommit", False)
    return pymysql.connect(**cfg)


def fetch_all(name_or_path: str, sql: str, params: Any = None) -> list[dict]:
    """便捷函数：一次性查完返回字典列表（自动关连接）。"""
    conn = connect(name_or_path)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())
    finally:
        conn.close()


if __name__ == "__main__":
    # 简单自测：列出所有配置并打印脱敏信息
    print(f"配置目录：{CONFIG_DIR}\n")
    files = list_config_files()
    if not files:
        print("(没有找到 ini 配置文件)")
    for f in files:
        try:
            cfg = load_db_config(f.name)
            masked = {k: ("***" if k == "password" else v) for k, v in cfg.items()}
            print(f"  {f.name}")
            for k, v in masked.items():
                print(f"    {k}: {v}")
        except Exception as e:  # noqa: BLE001
            print(f"  {f.name}  ->  加载失败: {e}")
