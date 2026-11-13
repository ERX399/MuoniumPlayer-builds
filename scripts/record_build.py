#!/usr/bin/env python3
import json
import os
import sys
import time
from pathlib import Path


def main() -> int:
    dist = Path(sys.argv[1])
    target = Path(sys.argv[2])
    jars = sorted(dist.glob("*.jar"))
    if not jars:
        print(f"{dist} 里没有 jar", file=sys.stderr)
        return 1
    data = {
        "upstream": "zihe114514/MuoniumPlayer-multiversion",
        "sha": os.environ["UPSTREAM_SHA"],
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "jars": [
            {"name": jar.name, "size": jar.stat().st_size}
            for jar in jars
        ],
    }
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已写入 {target}，共 {len(jars)} 个 jar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
