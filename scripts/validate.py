#!/usr/bin/env python3
"""验证 GitHub 双平台市场、manifest 和测试 Skill 的基本结构。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "dual-skill-demo"
MARKET_NAME = "dual-skill-market"
PLUGIN_NAME = "dual-skill-demo"
REPO_URL = "https://github.com/ischeng28/dual-skill-market"
EXPECTED_SKILLS = {"hello-test", "format-test"}
VERSION = "0.1.0"


def load_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_path(relative):
    require(relative.startswith("./"), f"插件路径必须以 ./ 开始: {relative}")
    target = (ROOT / relative).resolve()
    require(target.is_relative_to(ROOT), f"插件路径越过仓库根目录: {relative}")
    require(target.is_dir(), f"插件路径不存在: {relative}")
    require(target == PLUGIN.resolve(), f"市场未指向预期插件目录: {relative}")


def main():
    claude_market = load_json(ROOT / ".claude-plugin/marketplace.json")
    codex_market = load_json(ROOT / ".agents/plugins/marketplace.json")
    require(claude_market["name"] == MARKET_NAME, "Claude 市场名称错误")
    require(codex_market["name"] == MARKET_NAME, "Codex 市场名称错误")
    require(claude_market["owner"]["name"] == "ischeng28", "市场 owner 错误")
    require(codex_market["interface"]["displayName"], "Codex 市场显示名称缺失")
    for marketplace in (claude_market, codex_market):
        require(len(marketplace["plugins"]) == 1, "市场应当只有一个插件")
        entry = marketplace["plugins"][0]
        require(entry["name"] == PLUGIN_NAME, "市场插件名称不一致")
        source = entry["source"]
        check_path(source if isinstance(source, str) else source["path"])
    require(codex_market["plugins"][0]["source"]["source"] == "local", "Codex 市场应引用本仓库内相对路径")
    require(claude_market["plugins"][0]["version"] == VERSION, "Claude 市场版本不一致")

    portable = load_json(PLUGIN / "plugin.json")
    claude = load_json(PLUGIN / ".claude-plugin/plugin.json")
    codex = load_json(PLUGIN / ".codex-plugin/plugin.json")
    require(portable["$schema"].endswith("/plugin.schema.json"), "Portable schema 不正确")
    for manifest in (portable, claude, codex):
        require(manifest["name"] == PLUGIN_NAME, "Manifest 插件名称不一致")
        require(manifest["version"] == VERSION, "Manifest 版本不一致")
    require(portable["repository"] == REPO_URL, "Portable 清单远端地址错误")
    require(claude["repository"] == REPO_URL, "Claude 插件清单远端地址错误")
    require(codex["skills"] == "./skills/", "Codex skills 路径错误")

    skills_dir = PLUGIN / "skills"
    found = {child.name for child in skills_dir.iterdir() if child.is_dir()}
    require(found == EXPECTED_SKILLS, f"技能目录应恰好为两个: {found}")
    for name in sorted(EXPECTED_SKILLS):
        content = (skills_dir / name / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
        require(frontmatter is not None, f"Skill 缺少 YAML frontmatter: {name}")
        require(re.search(rf"^name:\s*{re.escape(name)}\s*$", frontmatter.group(1), re.MULTILINE), f"Skill name 错误: {name}")
        require(re.search(r"^description:\s*\S", frontmatter.group(1), re.MULTILINE), f"Skill 缺少 description: {name}")
        require(("HELLO-OK" if name == "hello-test" else "FORMAT-OK") in content, f"测试标记缺失: {name}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require(REPO_URL + ".git" in readme, "README 缺少远端 Git URL")
    require("claude plugin marketplace add ischeng28/dual-skill-market" in readme, "README 缺少 Claude 远端安装命令")
    require("codex plugin marketplace add ischeng28/dual-skill-market" in readme, "README 缺少 Codex 远端安装命令")

    print("PASS: GitHub 远端仓库信息、双平台市场、manifest、两个 Skill 均通过静态校验。")
    print("注：实际远程拉取与两个客户端调用仍需推送到 GitHub 后验证。")


if __name__ == "__main__":
    main()
