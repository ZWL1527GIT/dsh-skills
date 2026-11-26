# -*- coding: utf-8 -*-
"""在「对话文件夹」下新建一次数据处理对话的目录。

用法::

    cd <项目根>
    python 工具/new_conversation.py "统计各分类图书数量"
    python 工具/new_conversation.py "对比两侧客户数据" --date 20261020_1430

会创建::

    对话文件夹/<日期>_<主题>/
    ├── 脚本/
    │   └── process.py        （脚本模板）
    ├── 输出数据/
    └── 对话说明.md            （说明模板）
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Windows GBK 控制台兼容：让中文/特殊符号能正常输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONVERSATION_ROOT = PROJECT_ROOT / "对话文件夹"

README_TEMPLATE = """# {title}

- 时间：{timestamp}
- 需求：<一句话描述>
- 数据源：`1配置文件/配置文件-<环境>-<库说明>.ini`
- 脚本：[`脚本/process.py`](脚本/process.py)
- 输出：`输出数据/`

## 处理逻辑

1. <步骤 1>
2. <步骤 2>
3. <步骤 3>

## 运行

```bash
python {script_rel}
```

## 结论

<处理完成后填写>
"""

SCRIPT_TEMPLATE = '''# -*- coding: utf-8 -*-
"""{title}

如果本任务涉及写操作（UPDATE / DELETE / INSERT INTO ... SELECT / ALTER / TRUNCATE）：
  1. 取消下面 HAS_WRITE_OPERATION 的注释，启用 dry-run + 备份防护
  2. 填写 TABLE / WHERE / SET_CLAUSE
  3. 先跑 `python process.py`（默认 dry-run）确认影响行数
  4. 再加 `--execute` 真正执行
"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 让脚本无论从哪儿运行都能 import 项目根下的 工具 包
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from 工具.config_loader import connect, fetch_all  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "输出数据"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 写操作防护：如果本任务只读（SELECT），把下面这行注释掉即可
# 如果是写操作（UPDATE/DELETE/...），取消注释，并填好 TABLE / WHERE / SET_CLAUSE
# ---------------------------------------------------------------------------
# HAS_WRITE_OPERATION = True
# TABLE = "your_table"
# WHERE = "your_condition"          # 不带 WHERE 关键字
# SET_CLAUSE = "col = 'new_value'"  # UPDATE 的 SET 子句（仅 UPDATE 用）


def main() -> None:
    # 连接数据库（关键字即可，会自动去 1配置文件/ 匹配 ini 文件）
    # 例：conn = connect("本地")  或  connect("为知V2-供应链")
    conn = connect("本地")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            print("数据库连接 OK：", cur.fetchall())

        # ------------------------------------------------------------------
        # 只读任务：在这里写 SELECT / 统计 / 对比逻辑
        # rows = fetch_all("本地", "SELECT * FROM books LIMIT 10")
        # out = OUTPUT_DIR / "结果.csv"
        # ...
        # ------------------------------------------------------------------

        # ------------------------------------------------------------------
        # 写操作任务：取消下面这段注释，并按需修改
        # ------------------------------------------------------------------
        # if "HAS_WRITE_OPERATION" in dir():
        #     from 工具.db_backup import (
        #         backup_table,
        #         write_rollback_sql,
        #         confirm_execute,
        #         count_affected,
        #     )
        #
        #     BACKUP_DIR = Path(__file__).resolve().parent.parent / "备份"
        #     BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        #
        #     # Step 1: dry-run 防护（默认只统计，加 --execute 才执行）
        #     if not confirm_execute():
        #         n = count_affected(conn, TABLE, WHERE)
        #         print(f"[dry-run] 将影响 {{n}} 行；加 --execute 才会真正修改")
        #         return
        #
        #     # Step 2: 先备份
        #     backup_csv = backup_table(conn, TABLE, WHERE, BACKUP_DIR)
        #     rollback_sql = BACKUP_DIR / f"{{TABLE}}_rollback.sql"
        #     write_rollback_sql(backup_csv, TABLE, rollback_sql)
        #     print(f"[备份完成] {{backup_csv}}")
        #     print(f"[回滚 SQL] {{rollback_sql}}")
        #
        #     # Step 3: 执行写操作
        #     with conn.cursor() as cur:
        #         cur.execute(f"UPDATE `{{TABLE}}` SET {{SET_CLAUSE}} WHERE {{WHERE}}")
        #         affected = cur.rowcount
        #     conn.commit()
        #     print(f"[OK] 已修改 {{affected}} 行")
        # ------------------------------------------------------------------
    finally:
        conn.close()


if __name__ == "__main__":
    main()
'''


def sanitize(name: str, max_len: int = 30) -> str:
    """把任意标题处理成适合做目录名的字符串。"""
    name = re.sub(r'[\\/:*?"<>|\s]+', "_", name.strip())
    name = name.strip("_")
    return name[:max_len] or "未命名"


def main() -> None:
    parser = argparse.ArgumentParser(description="新建一次数据处理对话目录")
    parser.add_argument("title", help="一句话主题，例如：统计各分类图书数量")
    parser.add_argument(
        "--date",
        default=None,
        help="目录名前缀，格式 YYYYMMDD_HHMM；缺省取当前时间",
    )
    args = parser.parse_args()

    date_part = args.date or datetime.now().strftime("%Y%m%d_%H%M")
    title_part = sanitize(args.title)
    conv_dir = CONVERSATION_ROOT / f"{date_part}_{title_part}"

    if conv_dir.exists():
        raise SystemExit(f"[ERROR] 目录已存在: {conv_dir}")

    (conv_dir / "脚本").mkdir(parents=True)
    (conv_dir / "输出数据").mkdir(parents=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script_path = conv_dir / "脚本" / "process.py"
    script_rel = script_path.relative_to(PROJECT_ROOT).as_posix()

    script_path.write_text(
        SCRIPT_TEMPLATE.format(title=args.title), encoding="utf-8"
    )
    (conv_dir / "对话说明.md").write_text(
        README_TEMPLATE.format(
            title=args.title, timestamp=timestamp, script_rel=script_rel
        ),
        encoding="utf-8",
    )

    print(f"[OK] 已创建对话目录: {conv_dir}")
    print(f"   - 脚本: {script_path}")
    print(f"   - 输出: {conv_dir / '输出数据'}")


if __name__ == "__main__":
    main()
