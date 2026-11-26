# -*- coding: utf-8 -*-
"""写操作的安全备份工具。

任何会修改数据库数据的操作（UPDATE / DELETE / INSERT INTO ... SELECT / ALTER / TRUNCATE）
都应该**先备份再执行**。

本模块提供三个能力：
1. ``backup_table()``：把要修改的行先导成 CSV，作为 before 快照
2. ``write_rollback_sql()``：根据备份 CSV 生成对应的回滚 INSERT 语句
3. ``confirm_execute()``：检查脚本是否在 --execute 模式下运行（dry-run 防护）

典型用法::

    from __future__ import annotations
    import argparse
    import sys
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(PROJECT_ROOT))

    from 工具.config_loader import connect
    from 工具.db_backup import backup_table, write_rollback_sql, confirm_execute

    OUTPUT_DIR = Path(__file__).resolve().parent.parent / "输出数据"
    BACKUP_DIR = Path(__file__).resolve().parent.parent / "备份"
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    TABLE = "users"
    WHERE = "status = 'X'"

    def main() -> None:
        is_execute = confirm_execute()  # 没加 --execute 就直接退出

        conn = connect("本地")
        try:
            # 1. 先备份
            backup_csv = backup_table(conn, TABLE, WHERE, BACKUP_DIR)
            print(f"[备份完成] {backup_csv}")

            # 2. 生成回滚 SQL
            rollback_sql = BACKUP_DIR / f"{TABLE}_rollback.sql"
            write_rollback_sql(backup_csv, TABLE, rollback_sql)
            print(f"[回滚 SQL] {rollback_sql}")

            # 3. 执行写操作
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {TABLE} SET status = 'Y' WHERE {WHERE}")
                affected = cur.rowcount
            conn.commit()
            print(f"[OK] 已修改 {affected} 行")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    if __name__ == "__main__":
        main()

运行方式：
    # 干跑（默认）：只统计会影响多少行，不真正修改
    python process.py

    # 真正执行
    python process.py --execute
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Dry-run 防护
# ---------------------------------------------------------------------------
def confirm_execute(
    parser: argparse.ArgumentParser | None = None,
    description: str = "数据库写操作脚本",
) -> bool:
    """检查脚本是否在 ``--execute`` 模式下运行。

    - 如果用户**没加** ``--execute``：打印"当前是 dry-run 模式"，返回 False
    - 如果用户**加了** ``--execute``：返回 True

    调用方应该在拿到 False 时**直接 return / exit**，不要执行任何写操作。

    用法::

        if not confirm_execute():
            # 干跑模式：只 SELECT 看看会影响多少行
            count = fetch_one("SELECT COUNT(*) ... ")
            print(f"[dry-run] 将影响 {count} 行；加 --execute 才会真正修改")
            return

        # 真正执行写操作
        ...
    """
    if parser is None:
        parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="真正执行写操作；不加此参数时仅 dry-run（只统计影响行数，不修改数据）",
    )
    args, _ = parser.parse_known_args()

    if not args.execute:
        print("[dry-run] 当前是干跑模式，不会修改任何数据。")
        print("[dry-run] 如需真正执行，请加上 --execute 参数。")
        return False
    return True


# ---------------------------------------------------------------------------
# 备份
# ---------------------------------------------------------------------------
def backup_table(
    conn,
    table: str,
    where: str | None,
    backup_dir: Path,
    *,
    columns: Iterable[str] | None = None,
    file_prefix: str | None = None,
) -> Path:
    """把满足条件的行导出成 CSV 备份文件。

    参数:
        conn: pymysql 连接
        table: 表名
        where: WHERE 子句（不带 WHERE 关键字），如 ``"status = 'X'"``；传 None 表示整表
        backup_dir: 备份目录（通常是 ``对话文件夹/<某次>/备份/``）
        columns: 要备份的列；None 表示所有列
        file_prefix: 备份文件名前缀；缺省用 ``<table>_before_<时间戳>``

    返回:
        备份 CSV 的路径
    """
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = file_prefix or f"{table}_before_{timestamp}"
    backup_path = backup_dir / f"{prefix}.csv"

    cols = ", ".join(f"`{c}`" for c in columns) if columns else "*"
    sql = f"SELECT {cols} FROM `{table}`"
    if where:
        sql += f" WHERE {where}"

    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        if not rows:
            # 没有匹配的行也写一个空 CSV（只有表头），保留证据
            fieldnames = (
                list(columns)
                if columns
                else [d[0] for d in cur.description] if cur.description else []
            )
        else:
            fieldnames = list(rows[0].keys())

    with backup_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"[备份] {len(rows)} 行 -> {backup_path}")
    return backup_path


# ---------------------------------------------------------------------------
# 回滚 SQL 生成
# ---------------------------------------------------------------------------
def _sql_literal(value: Any) -> str:
    """把 Python 值转成 SQL 字面量。"""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        return f"'{value:%Y-%m-%d %H:%M:%S}'"
    # 字符串 / 其他：转义单引号
    s = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"


def write_rollback_sql(
    backup_csv: Path,
    table: str,
    out_path: Path,
    *,
    batch_size: int = 500,
) -> Path:
    """根据备份 CSV 生成对应的回滚 INSERT 语句。

    生成的 SQL 是**幂等**的：使用 ``REPLACE INTO``，可以重复执行不会出错。
    如果原表有主键 / 唯一索引，``REPLACE INTO`` 会正确覆盖。

    参数:
        backup_csv: ``backup_table()`` 生成的 CSV
        table: 目标表名
        out_path: 输出的 .sql 文件路径
        batch_size: 每条 INSERT 包含多少行（避免单条 SQL 过长）
    """
    backup_csv = Path(backup_csv)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with backup_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if not fieldnames:
            raise ValueError(f"备份文件 {backup_csv} 没有表头")

        cols_sql = ", ".join(f"`{c}`" for c in fieldnames)
        lines: list[str] = [
            f"-- 回滚 SQL：把 {table} 恢复到 {backup_csv.name} 中的状态",
            f"-- 生成时间: {datetime.now():%Y-%m-%d %H:%M:%S}",
            f"-- 注意：使用 REPLACE INTO，依赖原表的主键 / 唯一索引",
            "",
            f"USE `{{database}}`;  -- TODO: 改成实际数据库名，或删除本行",
            "",
        ]

        batch: list[str] = []
        row_count = 0
        for row in reader:
            row_count += 1
            values = ", ".join(
                _sql_literal(row[c] if row[c] != "" else None) for c in fieldnames
            )
            batch.append(f"({values})")
            if len(batch) >= batch_size:
                lines.append(
                    f"REPLACE INTO `{table}` ({cols_sql}) VALUES\n  "
                    + ",\n  ".join(batch)
                    + ";"
                )
                batch = []
        if batch:
            lines.append(
                f"REPLACE INTO `{table}` ({cols_sql}) VALUES\n  "
                + ",\n  ".join(batch)
                + ";"
            )

        lines.append("")
        lines.append(f"-- 共 {row_count} 行")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# 影响行数统计（dry-run 用）
# ---------------------------------------------------------------------------
def count_affected(conn, table: str, where: str | None = None) -> int:
    """统计满足条件的行数，用于 dry-run 时打印"将影响 X 行"。"""
    sql = f"SELECT COUNT(*) AS cnt FROM `{table}`"
    if where:
        sql += f" WHERE {where}"
    with conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
        return int(row["cnt"]) if row else 0


if __name__ == "__main__":
    # 简单自测：只测 confirm_execute 和 _sql_literal
    print(_sql_literal(None), _sql_literal(1), _sql_literal("it's"), _sql_literal(datetime(2026, 10, 21)))
