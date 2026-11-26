# dsh-skills

我个人的 DeepSeek Harness / Agent Skills 仓库。每个 skill 一个目录，放在 `skills/` 下，可直接被 DSH 的用户级 skills 目录加载。

## 目录结构

```
dsh-skills/
├── skills/
│   ├── data-processing-pattern/     # 数据处理模式
│   │   ├── SKILL.md                 # 技能主文件（frontmatter + 说明）
│   │   ├── scripts/                 # 可直接复制到目标项目 工具/ 下的 Python 工具
│   │   ├── assets/                  # 模板文件（ini / 提示词 / 对话说明）
│   │   └── references/              # 参考文档（FAQ）
│   └── java-multi-agent-orchestrator/   # Java 多智能体编排
│       ├── SKILL.md                 # 技能主文件（frontmatter + 说明）
│       ├── agents/                  # 平台适配配置（openai.yaml）
│       └── references/              # 参考文档（任务分类 / 契约 / 路由 / 恢复 / 规则 / 用例）
├── install.py                       # 一键安装脚本
└── README.md
```

## 技能清单

| Skill | 说明 |
| --- | --- |
| `data-processing-pattern` | Python 数据处理工作模式：把「配置 / 临时稿 / 对话产物」分开管理。数据库取数、清洗、对比、同步、统计等任务按固定目录结构 + 6 步工作流组织，每次任务自包含、可回溯，写操作有备份可回滚。 |
| `java-multi-agent-orchestrator` | Java 仓库多智能体编排：根 agent 掌握决策、集成与最终答复，仅在用户明确要求多 agent / 并行分析 / 委派时才拆分任务，普通小改动保持单 agent。含任务分类、任务契约、模型路由、失败恢复、Java 项目规则与评估用例。 |

## 安装 / 拉取到本机

DSH 的用户级 skills 目录是 `~/.agents/skills/`（Windows 上是 `C:\Users\<你>\.agents\skills\`）。仓库里的 `skills/<name>/` 直接复制进去就能用。

### 方式一：一键脚本（推荐）

```bash
git clone <本仓库地址> dsh-skills
python dsh-skills/install.py
```

脚本会把 `skills/` 下每个技能目录复制（或软链接）到 `~/.agents/skills/`，已存在的会提示覆盖。

### 方式二：手动复制

```bash
git clone <本仓库地址> dsh-skills
cp -r dsh-skills/skills/* ~/.agents/skills/
```

Windows PowerShell：

```powershell
git clone <本仓库地址> dsh-skills
Copy-Item -Recurse dsh-skills\skills\* "$env:USERPROFILE\.agents\skills\"
```

### 方式三：只装某一个技能

```bash
cp -r dsh-skills/skills/data-processing-pattern ~/.agents/skills/
```

安装后重启 DSH（或新开会话），技能会自动出现在可用 skills 列表里。

## 更新

```bash
cd dsh-skills
git pull
python install.py        # 覆盖本机旧版本
```

## 新增技能

在 `skills/` 下新建一个目录，放 `SKILL.md`（含 `name` / `description` frontmatter），需要的话再加 `scripts/`、`assets/`、`references/` 子目录，然后更新本 README 的技能清单。

## 说明

- 本仓库只放**技能定义**，不放具体业务项目的产物。
- `data-processing-pattern` 的 `scripts/` 里的 Python 工具是给目标项目复制用的，不是在本仓库里运行。
- `java-multi-agent-orchestrator` 的 `agents/openai.yaml` 是平台适配配置，不影响 DSH 加载；DSH 只读 `SKILL.md` 与 `references/`。
- 所有 skill 的 `SKILL.md` 用中文编写，面向中文项目环境。
