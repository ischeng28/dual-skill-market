# dual-skill-market

一个可以从 **GitHub 远端安装**的跨平台插件市场，提供 **1 个插件 / 2 个 Skill**，同时支持 **Claude Code** 与支持插件市场的 **Codex** 客户端。

- GitHub 仓库：<https://github.com/ischeng28/dual-skill-market>
- 远端 Git 地址：`https://github.com/ischeng28/dual-skill-market.git`
- 市场名称：`dual-skill-market`
- 插件名称：`dual-skill-demo`
- 两个测试 Skill：`hello-test`、`format-test`

> **第一次使用前必须先把本项目全部文件推送到 GitHub。** 目前创建了空仓库并不等于插件已在远端可安装；仓库根目录必须包含下面的隐藏目录 `.claude-plugin/` 和 `.agents/`。

## 目录

```text
dual-skill-market/
├── .claude-plugin/
│   └── marketplace.json                 # Claude Code 市场入口
├── .agents/
│   └── plugins/marketplace.json          # Codex 市场入口
├── .codex/
│   └── config.toml                       # 打开本仓库时的 Codex 项目配置（可选）
├── .github/
│   └── workflows/validate.yml           # 推送后自动执行结构校验
├── plugins/
│   └── dual-skill-demo/
│       ├── plugin.json                   # Portable Agent Plugins 清单
│       ├── .claude-plugin/plugin.json    # Claude Code 插件清单
│       ├── .codex-plugin/plugin.json     # Codex 兼容插件清单
│       └── skills/
│           ├── hello-test/SKILL.md       # 固定输出测试
│           └── format-test/SKILL.md      # 输入处理测试
├── scripts/validate.py
├── .gitignore
└── README.md
```

两个市场均引用仓库内的 `./plugins/dual-skill-demo`，**并不是引用使用者电脑上的某个本地路径**。运行 `claude plugin marketplace add ischeng28/dual-skill-market` 或 `codex plugin marketplace add ischeng28/dual-skill-market` 时，客户端从 GitHub 获取市场仓库并解析目录内插件。这样无需分别发布两个 Skill 或另建插件仓库。

## 第一步：将文件提交到已经创建好的空 GitHub 仓库

解压 ZIP，确保进入的是**含 `.claude-plugin`、`.agents`、`plugins` 的项目根目录**，然后在 PowerShell / Bash 中运行：

```bash
git init
git branch -M main
git remote add origin https://github.com/ischeng28/dual-skill-market.git
git add .
git commit -m "feat: add Claude Code and Codex test plugin"
git push -u origin main
```

如 `git remote add origin` 显示 `remote origin already exists`，则改用：

```bash
git remote set-url origin https://github.com/ischeng28/dual-skill-market.git
```

如仓库已初始化，则直接略过 `git init`。GitHub 推送需要你在本机使用已登录的 Git Credential Manager / SSH / GitHub CLI 等方式完成授权。

**推送完成后确认：** 打开 <https://github.com/ischeng28/dual-skill-market>，首页能看到 `README.md`，且 `.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json` 和 `plugins/dual-skill-demo/skills/` 都存在。

## 第二步：Claude Code 从 GitHub 安装

无需先手动 `git clone`。在本机终端执行：

```bash
claude plugin marketplace add ischeng28/dual-skill-market
claude plugin install dual-skill-demo@dual-skill-market
claude plugin list
```

也可以在 Claude Code 交互会话中执行：

```text
/plugin marketplace add ischeng28/dual-skill-market
/plugin install dual-skill-demo@dual-skill-market
```

新开 Claude Code 会话，测试两个 Skill：

```text
/dual-skill-demo:hello-test
/dual-skill-demo:format-test hello Codex 123
```

### Claude Code 更新

把修改后的文件推送到 GitHub 后，在已安装插件的机器上执行：

```bash
claude plugin marketplace update dual-skill-market
claude plugin update dual-skill-demo@dual-skill-market
```

更新后重新开始会话，或在支持的版本里使用 `/reload-plugins`。如果需要自动更新，可到 `/plugin` 的 Marketplaces 页面为该市场开启 auto-update。

## 第三步：Codex 从 GitHub 添加市场并安装

无需先手动 `git clone`。在安装了支持插件市场命令的 Codex CLI 的终端运行：

```bash
codex plugin marketplace add ischeng28/dual-skill-market
codex plugin marketplace list
```

这一步只注册并获取市场，**不代表插件已启用**。按当前官方流程，请在支持本地 / Git 仓库市场的 **Codex / ChatGPT 桌面客户端 Plugins Directory** 中找到 `ischeng28 Dual Skill Market`，安装 `dual-skill-demo`，然后启动新会话并执行：

```text
$hello-test
$format-test hello Codex 123
```

> 如果你的 Codex CLI / 桌面端版本没有插件市场或安装 UI，请升级到支持版本。不要把“通过复制 SKILL.md 手动使用”误认为“远端插件市场安装成功”。

### Codex 更新

推送新版到 GitHub 后执行：

```bash
codex plugin marketplace upgrade dual-skill-market
```

按你使用的 Codex 客户端重新同步 / 安装插件，并新建会话验证。Codex 的市场刷新机制与 Claude Code 的自动插件更新开关并不完全等价。

## 两个 Skill 的预期输出

**Skill 1：`hello-test`**（无需参数，始终输出这四行）

```text
[hello-test]
插件：dual-skill-demo
消息：你好，Claude Code 和 Codex！
校验码：HELLO-OK
```

**Skill 2：`format-test`**（传入 `hello Codex 123`）

```text
[format-test]
原文：hello Codex 123
大写：HELLO CODEX 123
校验码：FORMAT-OK
```

两个技能都是纯 `SKILL.md` 自然语言指令，不需要联网、MCP、API Key 或其他运行时依赖。预期输出用于人工检查模型是否执行指令，不保证每个模型会逐字遵循。

## 本地静态校验

安装了 Python 3.9+ 的机器，在项目根目录执行：

```bash
python scripts/validate.py
```

此外可以使用 Claude Code 的官方检查：

```bash
claude plugin validate .
claude plugin validate ./plugins/dual-skill-demo
```

项目自带 GitHub Actions，推送到 `main` 后自动运行静态结构校验。静态检查并不能证明 CLI 已安装成功，还需要上面的真实客户端测试。

## 维护与发布更新

两个 Skill 的实际源文件统一放在 `plugins/dual-skill-demo/skills/`。修改 Skill 后提交并推送：

```bash
git add .
git commit -m "feat: update test skills"
git push
```

如要发布新的插件版本，统一更新下面三个 manifest 的 `version`（例如 `0.1.0` → `0.2.0`），以及 `.claude-plugin/marketplace.json` 里的对应版本：

- `plugins/dual-skill-demo/plugin.json`
- `plugins/dual-skill-demo/.claude-plugin/plugin.json`
- `plugins/dual-skill-demo/.codex-plugin/plugin.json`

## 参考文档

- [Claude Code：Create a marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code：Plugin manifest](https://code.claude.com/docs/en/plugins-reference)
- [OpenAI：Package your plugin](https://developers.openai.com/plugins/build/plugins)
