---
name: data-processing-pattern
description: 一种把「配置、临时稿、对话产物」分开管理的 Python 数据处理工作模式。当用户要做数据库取数、清洗、对比、同步、统计等数据处理任务（包括涉及 UPDATE / DELETE 的写操作），或提到「1配置文件 / 对话文件夹 / 临时文件 / 数据处理模式 / 数据处理模板」等关键词时，务必使用本 skill。它会引导你把数据库连接放在 `1配置文件/` 的 ini 里、把提示词草稿放在 `临时文件/`、把每次任务的所有产物（脚本 + 输出 + 写操作备份）归档到 `对话文件夹/时间戳_主题/` 下，保证每次数据处理都可追溯、可复现、写操作有备份可回滚、不污染项目其它部分。
---

# 数据处理模式（data-processing-pattern）

一种**通用的 Python 数据处理工作模式**，把一次数据处理任务拆成三个关注点：

- **配置**（连接哪个数据库） → `1配置文件/`
- **过程稿**（提示词、SQL 草稿） → `临时文件/`
- **产物**（脚本 + 输出） → `对话文件夹/<某次任务>/`

这个模式最早从一个具体的「数据处理模板项目」里提炼出来，但可以套用到任何需要做数据处理的项目。核心收益是：**每次任务都自包含、可回溯，下次做类似任务只要复制目录改 SQL 就行**。

---

## 什么时候用

用户想做以下任何一件事时，都应该按这个模式组织代码：

- 从数据库取数、统计、聚合  ← **只读**
- 两张表 / 两个库之间做对比、对账  ← **只读**
- 把数据从一个库同步到另一个库  ← **会写目标库** ⚠️
- 数据清洗、字段映射、补数  ← **会写库** ⚠️
- 跑一次性的 ETL 脚本  ← **通常会写库** ⚠️

**关键判断**：这个任务**不是**长期运行的服务，而是**一次或几次跑完就结束**的数据处理动作。

> ⚠️ **如果任务涉及 UPDATE / DELETE / INSERT INTO ... SELECT / ALTER / TRUNCATE 等写操作**，
> 必须额外遵守下面「写操作的安全工作流」。这一节不是可选项。

---

## 目录骨架（在用户的项目根下）

```
<项目根>/
├── 1配置文件/                # 数据库连接配置（INI 格式，每个环境一个文件）
│   ├── 配置文件-<环境>-<库说明>.ini
│   ├── 配置文件-<环境>-<库说明>.ini
│   └── ...
│
├── 临时文件/                 # 提示词草稿、临时 SQL、过程稿（可随时清理）
│   └── README.md
│
├── 对话文件夹/                # 每次数据处理任务一个子目录
│   ├── README.md
│   └── <YYYYMMDD_HHMM>_<主题>/
│       ├── 脚本/             # 本次任务的 Python 脚本（可多个）
│       ├── 输出数据/          # 脚本输出（csv / xlsx / json / png…）
│       └── 对话说明.md        # 需求、数据源、逻辑、结论
│
└── 工具/                     # 公共 Python 工具
    ├── config_loader.py      # 加载 ini 配置、建立 DB 连接
    └── new_conversation.py   # 一键新建对话目录
```

### 为什么这样分？

- **`1配置文件/`**：连接信息集中管理，ini 比 .py 配置更适合非程序员查看，比 .env 更适合多环境对比。文件名即说明，一看就知道是「哪个环境的哪个库」。
- **`临时文件/`**：很多数据处理需求是边想边试的，需要一个「草稿区」放提示词、SQL、临时数据。明确告诉团队这里的内容**可以随时删**，避免越积越多。
- **`对话文件夹/<某次>/`**：一次数据处理通常涉及「需求 → 脚本 → 输出 → 结论」一整套产物，把它们放在同一个目录里，下次任何人都能一秒看懂「那次做了什么」。
- **`工具/`**：把「读 ini 配置」「新建对话目录」这种重复动作沉到工具里，新脚本只需要 `from 工具.config_loader import connect` 就能干活。

---

## 标准工作流程

每次开始一个新的数据处理任务，严格按以下顺序：

### 1. 起草提示词（在 `临时文件/` 下）

在 `临时文件/` 下新建一个 `.md` 文件，把需求写清楚。最少包含：

```text
【任务背景】要做什么、为什么要做
【数据源】用 1配置文件/ 下哪个 ini（可写关键字，如 "本地"）
【涉及表】表名 + 关键字段
【处理逻辑】1. 2. 3.
【期望输出】格式（csv/xlsx/…）+ 字段列表
【约束】只读/可写、是否脱敏、性能限制
```

> 模板见 `assets/提示词模板.md`。

### 2. 开新对话目录

```bash
python 工具/new_conversation.py "一句话主题"
```

这会在 `对话文件夹/` 下创建 `<YYYYMMDD_HHMM>_<主题>/` 目录，并自动生成：
- `脚本/process.py` —— 已经预置好读取配置、定位 `OUTPUT_DIR` 的骨架
- `输出数据/` —— 空目录
- `对话说明.md` —— 模板，等任务结束后填写

### 3. 在 `脚本/process.py` 里写处理逻辑

骨架已经预置了：

```python
from 工具.config_loader import connect, fetch_all

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "输出数据"

conn = connect("本地")    # 按关键字匹配 1配置文件/ 下的 ini
```

只需要专注于业务 SQL 和数据加工，**不要**在这一步：
- 重新读 ini 文件（用 `connect()` / `fetch_all()`）
- 硬编码输出路径（用 `OUTPUT_DIR`）
- 把连接信息复制粘贴到脚本里

### 4. 跑脚本，输出落到 `输出数据/`

```bash
python 对话文件夹/<本次任务>/脚本/process.py
```

中间结果文件名建议加 `_tmp` 前缀，最终交付的用业务名。

### 5. 填写 `对话说明.md`

把需求、数据源、关键 SQL、结论、待办写进去。这是下次回溯的入口。

### 6. 清理 `临时文件/` 里的草稿

任务结束后，`临时文件/` 里对应的草稿可以删。`临时文件/` 永远只放「正在进行中」的内容。

---

## 写操作的安全工作流（UPDATE / DELETE / INSERT 必读）

只要任务会**修改数据库里的数据**（不只是 SELECT），就必须遵守以下三条规定。
这些规定的目的是：**就算脚本写错了，也能 1 分钟之内把数据恢复原样**。

### 规定 1：先备份，再执行（强制）

任何写操作执行之前，必须在**本次对话目录**下创建 `备份/` 子目录，
并**先把要修改的行**导出成 CSV：

```
对话文件夹/<某次任务>/
├── 脚本/
│   └── process.py
├── 输出数据/
├── 备份/                    ← 写操作任务必须有这个目录
│   ├── <表名>_before_<时间戳>.csv       ← 改之前的快照
│   └── <表名>_rollback.sql              ← 一键回滚 SQL
└── 对话说明.md
```

用 `工具/db_backup.py` 里的 `backup_table()` 一行代码搞定：

```python
from 工具.db_backup import backup_table, write_rollback_sql

backup_csv = backup_table(conn, "users", "status = 'X'", BACKUP_DIR)
write_rollback_sql(backup_csv, "users", BACKUP_DIR / "users_rollback.sql")
```

**为什么**：CSV 快照是跨数据库、人可读、可 diff 的最通用格式。
回滚 SQL 用 `REPLACE INTO` 生成，依赖主键幂等覆盖，重复执行不会出错。

### 规定 2：默认 dry-run，加 `--execute` 才真正执行（强制）

写操作的脚本**默认必须是 dry-run**：只 `SELECT COUNT(*)` 统计会影响多少行，不真正修改。
用户明确加 `--execute` 参数才执行写操作。

用 `工具/db_backup.py` 里的 `confirm_execute()` 一行代码搞定：

```python
from 工具.db_backup import confirm_execute, count_affected

def main():
    if not confirm_execute():
        # dry-run：只打印影响行数
        n = count_affected(conn, "users", "status = 'X'")
        print(f"[dry-run] 将影响 {n} 行；加 --execute 才会真正修改")
        return

    # 真正的写操作
    ...
```

**为什么**：写操作最常见的错误是 `WHERE` 条件写错。
默认 dry-run 能让用户**先看到会影响多少行**，确认无误再执行。
就算脚本逻辑完全错了，最坏只是查了一次，不会改坏数据。

### 规定 3：`对话说明.md` 必须写清回滚步骤（强制）

写操作任务的 `对话说明.md` 必须包含一节「备份与回滚」，写清楚：

- 备份文件位置：`备份/<表名>_before_<时间戳>.csv`
- 回滚 SQL 位置：`备份/<表名>_rollback.sql`
- 回滚操作步骤：例如 `mysql -u xxx -p dbname < 备份/users_rollback.sql`
- 影响行数（dry-run 阶段统计出来的）

**为什么**：出问题时，**当事人可能不在场**，下次值班的人需要能凭这份说明独立完成回滚。

### 写操作的完整脚本骨架

```python
# -*- coding: utf-8 -*-
"""<任务主题>（含写操作，已带备份与 dry-run 防护）"""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from 工具.config_loader import connect
from 工具.db_backup import backup_table, write_rollback_sql, confirm_execute, count_affected

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "输出数据"
BACKUP_DIR = Path(__file__).resolve().parent.parent / "备份"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

TABLE = "users"
WHERE = "status = 'X'"          # 修改条件
SET_CLAUSE = "status = 'Y'"     # 要改成什么


def main() -> None:
    conn = connect("本地")
    try:
        # Step 1: dry-run 防护
        if not confirm_execute():
            n = count_affected(conn, TABLE, WHERE)
            print(f"[dry-run] 将影响 {n} 行；加 --execute 才会真正修改")
            return

        # Step 2: 先备份
        backup_csv = backup_table(conn, TABLE, WHERE, BACKUP_DIR)
        rollback_sql = BACKUP_DIR / f"{TABLE}_rollback.sql"
        write_rollback_sql(backup_csv, TABLE, rollback_sql)

        # Step 3: 执行写操作
        with conn.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE}` SET {SET_CLAUSE} WHERE {WHERE}")
            affected = cur.rowcount
        conn.commit()
        print(f"[OK] 已修改 {affected} 行；备份在 {backup_csv}，回滚 SQL 在 {rollback_sql}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
```

---

## 关键代码

### `工具/config_loader.py` —— 读 ini、建连接

完整实现见 `scripts/config_loader.py`。核心 API：

```python
from 工具.config_loader import load_db_config, connect, fetch_all

# 按关键字挑配置（自动在 1配置文件/ 下找文件名包含关键字的 ini）
cfg  = load_db_config("本地")               # 拿配置字典
conn = connect("为知V2-供应链")              # 直接拿 pymysql 连接
rows = fetch_all("本地", "SELECT * FROM t LIMIT 10")
```

**关键字匹配的语义**：在 `1配置文件/` 下找所有 ini，返回第一个**文件名包含该关键字**的文件。如果匹配到多个会报错，提示用户写得更具体。

### `工具/new_conversation.py` —— 新建对话目录

完整实现见 `scripts/new_conversation.py`。命令行用法：

```bash
python 工具/new_conversation.py "统计各分类图书数量"
python 工具/new_conversation.py "对比两侧客户数据" --date 20261020_1430
```

---

## INI 配置约定

每个 ini 文件必须有 `[database]` 段：

```ini
[database]
host = 127.0.0.1
port = 3306
user = root
password = ******
database = my_db
charset = utf8mb4
```

**命名建议**：`配置文件-<环境>-<库说明>.ini`，例如：
- `配置文件-1-本地.ini`
- `配置文件-孝南-食堂-正式.ini`
- `配置文件-为知V2-供应链.ini`

这样的好处：
- 文件名即文档，一眼看出连的是哪个库
- 多环境并排时容易对比
- 关键字匹配友好（`connect("本地")` / `connect("孝南")` 都能唯一定位）

---

## 跨项目复用

把这个模式搬到一个新项目：

1. 在项目根建 `1配置文件/`、`临时文件/`、`对话文件夹/`、`工具/` 四个目录。
2. 把 `scripts/config_loader.py` 和 `scripts/new_conversation.py` 复制到 `工具/`。
3. 在 `1配置文件/` 下加几个 ini。
4. 完成 —— 已经可以按上面的「标准工作流程」开干了。

**如果用户的项目已经有了自己的工具**（比如已有的 `load_db_config`），优先用他们自己的，不要强行替换；本模式关注的是**目录结构 + 工作流程**，不是某个具体函数。

---

## 常见反模式（不要这样做）

### 结构反模式

- ❌ 把数据库连接信息硬编码在脚本里 → 应该用 ini + `connect()`
- ❌ 把脚本放在项目根 → 应该放进 `对话文件夹/<某次>/脚本/`
- ❌ 把输出文件随意放在脚本旁边 → 应该放进同对话目录的 `输出数据/`
- ❌ 在 `临时文件/` 里放正式产物 → 临时文件只放草稿
- ❌ 一个对话目录里塞多次不相关任务 → 每次任务开新目录
- ❌ 跳过 `对话说明.md` → 没有它，下次看不懂那次做了什么

### 写操作反模式（更严重）

- ❌ **没有备份就直接 UPDATE / DELETE** → 必须先把要修改的行导出到 `备份/<表名>_before_<时间戳>.csv`，并生成对应的 `<表名>_rollback.sql`
- ❌ **写操作脚本不支持 dry-run** → 必须默认只 `SELECT COUNT(*)` 统计影响行数，加 `--execute` 才执行
- ❌ **`对话说明.md` 里不写回滚步骤** → 出问题时没人知道怎么把数据改回去
- ❌ **用事务但忘了 `conn.commit()` 或 `conn.rollback()` 处理异常** → 必须 `try / except / finally`，异常时显式 `rollback()`
- ❌ **在生产库上直接试写操作** → 必须先在 dev / 本地库上跑通整个流程（包括备份和回滚）

---

## 资源清单

| 文件 | 何时使用 |
| --- | --- |
| `scripts/config_loader.py` | 复制到用户项目的 `工具/` 下：读 ini 配置 |
| `scripts/new_conversation.py` | 复制到用户项目的 `工具/` 下：新建对话目录 |
| `scripts/db_backup.py` | 复制到用户项目的 `工具/` 下：**写操作前必用**，提供备份 / 回滚 SQL 生成 / dry-run 防护 |
| `assets/配置文件-模板.ini` | 新建 ini 配置时参考 |
| `assets/提示词模板.md` | 起草新任务提示词时参考 |
| `assets/对话说明模板.md` | 填写 `对话说明.md` 时参考（含「备份与回滚」一节） |
| `references/FAQ.md` | 遇到边角情况（多库、跨项目、非 pymysql、写操作安全）时查阅 |

开始任务前先确认用户的项目里有没有已存在的 `1配置文件 / 临时文件 / 对话文件夹 / 工具`；有就直接用，没有就按本 skill 帮他建起来。
