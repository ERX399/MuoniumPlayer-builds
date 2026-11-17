#!/usr/bin/env python3
import argparse
import os
import sys
import time
from pathlib import Path

REPO = "ERX399/MuoniumPlayer-builds"
UPSTREAM = "zihe114514/MuoniumPlayer-multiversion"
LOADER_LABELS = {"fabric": "Fabric", "forge": "Forge", "neoforge": "NeoForge"}
LOADER_ORDER = ("fabric", "forge", "neoforge")


def human(size: int) -> str:
    for unit in ("B", "KB", "MB"):
        if size < 1024 or unit == "MB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return f"{size:.1f} MB"


def parse(name: str):
    if not name.startswith("MuoniumPlayer-") or not name.endswith(".jar"):
        return None
    parts = name[: -len(".jar")].split("-")
    if len(parts) < 4:
        return None
    loader = parts[-2]
    if loader not in LOADER_LABELS:
        return None
    return "-".join(parts[1:-2]), loader, parts[-1]


def version_key(mc: str):
    try:
        return (tuple(int(p) for p in mc.split(".")), mc)
    except ValueError:
        return ((10**9,), mc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist")
    parser.add_argument("--tag", default="nightly")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    dist = Path(args.dist)
    jars = sorted(dist.glob("*.jar"))
    if not jars:
        print(f"{dist} 里没有 jar", file=sys.stderr)
        return 1

    sha = os.environ.get("UPSTREAM_SHA", "")
    groups: dict[str, dict[str, Path]] = {}
    unknown: list[Path] = []
    for jar in jars:
        parsed = parse(jar.name)
        if parsed is None:
            unknown.append(jar)
            continue
        mc, loader, _ = parsed
        groups.setdefault(mc, {})[loader] = jar

    lines = []
    if sha:
        lines.append(f"上游 [{UPSTREAM}](https://github.com/{UPSTREAM}) @ [`{sha[:7]}`](https://github.com/{UPSTREAM}/commit/{sha})")
    lines.append(f"构建时间：{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}")
    lines.append("")
    lines.append("选好你的 Minecraft 版本，点对应的加载器直接下载，jar 丢进 `mods/` 就行。")
    lines.append("")
    lines.append("| Minecraft | 加载器 | 下载 | 大小 |")
    lines.append("| --- | --- | --- | --- |")
    for mc in sorted(groups, key=version_key):
        loaders = groups[mc]
        for loader in LOADER_ORDER:
            jar = loaders.get(loader)
            if jar is None:
                continue
            url = f"https://github.com/{REPO}/releases/download/{args.tag}/{jar.name}"
            lines.append(
                f"| {mc} | {LOADER_LABELS[loader]} | [{jar.name}]({url}) | {human(jar.stat().st_size)} |"
            )
    for jar in unknown:
        url = f"https://github.com/{REPO}/releases/download/{args.tag}/{jar.name}"
        lines.append(f"| - | - | [{jar.name}]({url}) | {human(jar.stat().st_size)} |")

    sums = dist / "SHA256SUMS"
    if sums.exists():
        lines.append("")
        lines.append("<details><summary>SHA256 校验和</summary>")
        lines.append("")
        lines.append("```")
        for line in sums.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2:
                lines.append(f"{parts[0]}  {parts[1]}")
        lines.append("```")
        lines.append("")
        lines.append("</details>")

    lines.append("")
    lines.append("只包含能直接放进 `mods/` 的主 jar，不含源码包、dev 包和伴生包。")

    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已写入 {args.out}，共 {len(jars)} 个 jar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
