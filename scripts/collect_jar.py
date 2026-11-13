#!/usr/bin/env python3
import argparse
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

MOD_METADATA = ("fabric.mod.json", "META-INF/neoforge.mods.toml", "META-INF/mods.toml")
CLASSIFIERS = ("-sources.jar", "-dev.jar", "-javadoc.jar")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--loader", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    libs = Path(args.root) / args.tree / args.loader / "build" / "libs"
    jars = sorted(
        p
        for p in libs.glob("MuoniumPlayer-*.jar")
        if not p.name.endswith(CLASSIFIERS)
    )
    if len(jars) != 1:
        print(f"期望 {libs} 里只有一个主 jar，实际：{[p.name for p in jars]}", file=sys.stderr)
        return 1

    jar = jars[0]
    with zipfile.ZipFile(jar) as archive:
        names = set(archive.namelist())
    if not any(entry in names for entry in MOD_METADATA):
        print(f"{jar.name} 里没有 mod 元数据，可能是源码包或构建失败", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    target = out / jar.name
    shutil.copy2(jar, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"{target.name}\t{target.stat().st_size}\t{digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
