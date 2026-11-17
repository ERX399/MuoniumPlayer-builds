# MuoniumPlayer 自动构建

跟随 [zihe114514/MuoniumPlayer-multiversion](https://github.com/zihe114514/MuoniumPlayer-multiversion) 自动构建，只发布能直接放进 `mods/` 的主 jar。

## 产物

- 每个 Minecraft 版本 × 加载器一个 jar，命名沿用上游：`MuoniumPlayer-<mc>-<loader>-<version>.jar`
- 不含 `-sources.jar`、`-dev.jar`，也不含 Skija / FFmpeg / 汽水后端等伴生包
- 每次发布附 `SHA256SUMS`
- 发布说明里直接列出每个 jar 的下载链接和大小，按 Minecraft 版本分组，不用展开 Assets 找文件

## 触发方式

| 方式 | 行为 |
| --- | --- |
| 每天 04:00（北京时间） | 构建上游默认分支最新提交，更新 `nightly` Release |
| 手动 `workflow_dispatch` | 可指定上游 ref，可选择是否发布 |
| push 到 main | 只构建，不发布 |

## 构建矩阵

| Minecraft | 加载器 | JDK |
| --- | --- | --- |
| 1.20.1 recode | Fabric / Forge | 21 |
| 1.21.1 | Fabric / NeoForge | 21 |
| 1.21.10 | Fabric / NeoForge | 21 |
| 1.21.11 recode | Fabric / NeoForge | 21 |
| 26.1.2 | Fabric / NeoForge | 25 |
| 26.2 | Fabric / NeoForge | 25 |
| 26.3 | Fabric / NeoForge | 25 |

## 实现

- `.github/workflows/build.yml`：拉取上游指定提交，清掉本机专用 Gradle 配置后按矩阵构建
- `scripts/collect_jar.py`：只挑主 jar，校验里面确实有 mod 元数据，再计算 SHA256
- `scripts/record_build.py`：把上游 SHA、构建时间和每个 jar 的大小写进 `last-build.json`，同时让仓库保持活跃，避免定时任务被 GitHub 自动停用
- `scripts/render_body.py`：按 Minecraft 版本生成发布说明，正文直接给出每个 jar 的下载直链、大小和校验和

本仓库不含上游代码，也不对上游源码做任何修改。

## 许可

构建产物来自上游项目，遵循其 Apache-2.0 许可。
