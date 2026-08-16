# WorldEditPE

> WorldEdit for NetEase Minecraft (Bedrock) — 网易版《我的世界》WorldEdit 模组

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**WorldEditPE** 是一个运行在网易版《我的世界》（基岩版 / MinecraftPE_Netease）上的
地图编辑模组。它将经典 Java 版 WorldEdit 的核心能力（选区、填充、几何生成、剪贴板、
撤销/重做、刷子等）以 Python + 网易 ModSDK 的形式带到移动端。

- **版本**：v0.1（首个可发布版本）
- **作者**：JiHong-Studio（ChengXing507 与 Ecaps）
- **协议**：GNU GPL v3

---

## 目录

- [原项目信息](#原项目信息)
- [相较原项目的改动](#相较原项目的改动)
- [介绍](#介绍)
  - [简介](#简介)
  - [指令集](#指令集)
- [安装](#安装)
- [构建与打包](#构建与打包)
- [项目结构](#项目结构)
- [许可](#许可)

---

## 原项目信息

> **版权声明**：本项目（WorldEditPE）是 GPLv3 开源项目的衍生作品。
> - 架构与指令设计参考自 **EngineHub/WorldEdit**（Copyright © sk89q and WorldEdit team and contributors，GPLv3）
> - 早期代码基于社区 **WorldEditPE 原型**（匿名贡献者）
> - 依据 GPLv3 第 5 条要求，本 README 与 `LICENSE` 中保留上述上游版权声明。
>
> **免责声明**：WorldEditPE 与 EngineHub/WorldEdit 项目**无任何从属或背书关系**。

遵循其开源许可要求：

### 1. EngineHub/WorldEdit（架构来源）

- **项目**：[EngineHub/WorldEdit](https://github.com/EngineHub/WorldEdit)（Java，Minecraft 地图编辑器）
- **协议**：[GNU General Public License v3](https://github.com/EngineHub/WorldEdit/blob/version/7.4.x/LICENSE.txt)（GPL-3.0-only）
- **用途**：WorldEditPE 的**架构、指令语义、算法思路**参考自 WorldEdit：
  - `EditSession` / `ChangeSet` → `core/operator.py` / `core/history.py`
  - `CuboidRegion` / `LocalSession` → `core/selector.py` / `core/session.py`
  - `Clipboard` / `BlockVector3` → `clipboard/dict_clipboard.py` / `core/vectors.py`
  - `ShapeGenerator` / `Brush` → `algorithms/shapes.py` / `brush/base.py`
  - 指令名与参数语义（`=set`、`=copy`、`=paste`、`=stack`、`=cyl`、`=sphere` 等）与 WorldEdit 对齐

> 本项目**不是** WorldEdit 的代码翻译或复制，而是参考其架构与指令设计的 Python 重实现。
> 作为基于 GPLv3 上游作品衍生的项目，WorldEditPE 同样以 GPLv3 发布，且在本 README 中明示上游出处。

### 2. 早期 WorldEditPE 原型（代码起点）

- 本项目早期版本代码（`extracted_original` 中所见）是社区 WorldEditPE 原型，包含
  `modMain.py`、`Server.py`、`commands/`、`algorithms/` 等模块的基本框架。
- 其中 `modMain.py` 的 `RegisterSystem` 传类对象的方式存在静默失败问题，已在
  v0.1 中改为**字符串类路径**并重新实现。

---

## 相较原项目的改动

> 依据 GPLv3 第 5 条（Conveying Modified Source Versions）要求，列出相对上游的修改。

### 相对 WorldEdit（Java）的改动

1. **语言与运行平台**：Java/Fabric/Bukkit → Python 2 + 网易 ModSDK（移动端/Studio）
2. **指令前缀**：Java 版 `//` → 网易版使用 `=`（因网易聊天系统拦截单 `/`，`//` 在移动端不可靠）
3. **通知通道**：新增多维通知系统 `utils/messages.py`：
   - 原生 `/tellraw @s` + 显式 playerId（主通道）
   - `/title @s actionbar` 动作栏（备用可见通道）
   - `BroadcastToAllClient` → 客户端 HUD（预留）
   - `SendMsgToPlayer` 悄悄话（备用）
4. **注册方式**：修复 `RegisterSystem` 传类对象失败问题，改为字符串类路径
5. **剪贴板实现**：JSON 字典 `{(x,y,z): block}`，非 Java 的 NBT schematic
6. **新增指令**：`=transform`（自动朝向翻转/旋转）、`=selinfo`、`=fillr`（递归填充）等
7. **方块 API**：全部改用网易 `CreateBlockInfo`/`SetBlock` 系列接口

### 相对早期 WorldEditPE 原型的改动

> 早期原型为匿名社区作品（无版权声明），基于其代码开发时已整体重构；
> 新增与修改代码的版权归 JiHong-Studio（ChengXing507 & Ecaps）所有，见各源文件头部声明。

1. **入口修复**：`RegisterSystem` 第三参数改为**字符串类路径**（官方 API 要求），
   原代码传类对象导致系统注册静默失败
2. **通知修复**：原 `utils/messages.py` 仅 1714 字节，通道单一且不可靠；
   重写为多通道 + 诊断日志 + 逐行 tellraw
3. **翻转变换修复**：修正 `flip` 的 Y 轴坐标映射（`nz = -z`），对齐 2016 版 WorldEdit 行为
4. **新增自动朝向**：`commands/transform.py` 使用 `CreateRot().GetRot()` 获取玩家 yaw，
   `=flip`/`=rotate` 无需手动指定方向
5. **代码规范**：统一版权头、GPLv3 声明、模块 docstring

---

## 介绍

### 简介

WorldEditPE 让你在手机上的网易版《我的世界》里也能获得桌面级的地图编辑体验：

- **选区**：木斧左键/右键快速框选，或 `=pos1`/`=pos2` 精确指定
- **区域操作**：一键填充、替换、建墙、描边
- **几何生成**：圆柱、球体、金字塔、圆锥等一键生成
- **剪贴板**：复制/剪切/粘贴大区域，支持旋转与翻转
- **历史记录**：撤销/重做，手滑无忧
- **实用工具**：一键排水、填充空洞、递归填充
- **刷子系统**：球形/圆柱形刷子，自由雕刻地形

所有指令以 **`=`** 前缀在聊天框输入（如 `=help`），即时生效，无需重启世界。

### 指令集

#### 帮助
| 指令 | 说明 |
|---|---|
| `=help` / `=?` | 显示全部指令的帮助 |

#### 选区
| 指令 | 说明 |
|---|---|
| `=pos1 [x y z]` | 设置选区第 1 点（默认当前位置） |
| `=pos2 [x y z]` | 设置选区第 2 点（默认当前位置） |
| `=wand` | 获取木斧（左键=pos1，右键=pos2） |
| `=sel` | 显示选区信息 |
| `=selinfo` | 显示选区详细信息 |
| `=deselect` / `=desel` | 清除选区 |

#### 区域操作
| 指令 | 说明 |
|---|---|
| `=set <block>` | 用方块填充整个选区 |
| `=replace [from] <to>` | 替换方块（可选指定来源方块） |
| `=walls <block>` | 沿选区边缘建造墙壁 |
| `=outline <block>` | 建造选区边框（空心） |
| `=line <block>` | 在两点间画线 |

#### 几何生成
| 指令 | 说明 |
|---|---|
| `=cyl <block> <半径> [高度]` | 实心圆柱 |
| `=hcyl <block> <半径> [高度]` | 空心圆柱 |
| `=sphere <block> <半径>` | 实心球体 |
| `=hsphere <block> <半径>` | 空心球体 |
| `=pyramid <block> <大小>` | 金字塔 |
| `=cone <block> <半径> <高度>` | 圆锥 |

#### 剪贴板
| 指令 | 说明 |
|---|---|
| `=copy` | 复制选区到剪贴板 |
| `=cut` | 剪切选区到剪贴板（清空原区域） |
| `=paste [-a]` | 粘贴剪贴板（`-a` 包含空气方块） |
| `=stack <数量> [方向]` | 沿方向重复堆叠选区 |
| `=rotate <角度>` | 旋转剪贴板（90 的倍数） |
| `=flip [方向]` | 翻转剪贴板（默认按玩家朝向） |

#### 实用工具
| 指令 | 说明 |
|---|---|
| `=fill <block> <半径> [深度]` | 填充空洞（仅填充空气） |
| `=fillr <block> <半径> [深度]` | 递归填充（填充连通区域） |
| `=drain <半径>` | 排空液体（水/岩浆） |
| `=brush <sphere\|cylinder> <block> <半径>` | 设置刷子 |
| `=size <半径>` | 设置刷子大小 |
| `=mask <block>` | 设置刷子蒙版（仅替换指定方块） |

#### 历史
| 指令 | 说明 |
|---|---|
| `=undo` | 撤销上一次操作 |
| `=redo` | 重做上一次撤销 |
| `=clearhistory` | 清空操作历史 |

#### 调试
| 指令 | 说明 |
|---|---|
| `=test` | 测试模组与通知通道是否正常 |

---

## 安装

1. 在 **MC Studio**（网易开发者平台）中打开世界工程
2. 将 `behavior_pack/` 与 `resource_pack/` 放入 `行为包` / `资源包` 目录
   （或直接导入发布包 `WorldEditPE_v0.1.zip`）
3. 在 Studio 中确认两个包的 uuid 无冲突（`manifest.json`）
4. 运行世界，聊天框输入 `=help` 验证

---

## 构建与打包

```bash
# 打包发布 zip（包含 behavior_pack + resource_pack）
python3 scripts/package.py
```

---

## 项目结构

```
WorldExit/
├── LICENSE                     # GNU GPL v3
├── README.md                   # 本文件
├── skill.md                    # 开发经验总结
├── behavior_pack/
│   ├── manifest.json           # 行为包清单
│   └── WorldEditPE/
│       ├── modMain.py          # 入口：注册 Server/Client System
│       ├── Server.py           # 服务端系统：聊天指令 + 木斧交互
│       ├── Client.py           # 客户端系统：广播通知 → 本地 HUD
│       ├── commands/           # 指令集（parser + 各指令模块）
│       ├── core/               # 会话/选区/历史/向量
│       ├── algorithms/         # 形状/填充/线条算法
│       ├── clipboard/          # 剪贴板
│       ├── brush/              # 刷子
│       └── utils/              # messages(通知)/blocks(方块)
├── resource_pack/
│   └── manifest.json           # 资源包清单
└── scripts/
    └── package.py              # 打包脚本
```

---

## 许可

```
WorldEditPE - WorldEdit for NetEase Minecraft (Bedrock)
Copyright (C) 2026 JiHong-Studio (ChengXing507 & Ecaps)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

**上游致谢**：架构与指令设计参考 [EngineHub/WorldEdit](https://github.com/EngineHub/WorldEdit)
（Copyright © EngineHub；GPLv3）。
