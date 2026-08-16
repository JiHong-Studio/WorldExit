# WorldEditPE 开发经验总结（skill.md）

> 本文档记录 WorldEditPE（网易版《我的世界》模组）开发过程中积累的关键经验，
> 供后续迭代与问题排查参考。所有结论均基于真实设备调试日志（移动端 100.70.24.83）。

---

## 1. 项目概况

- **项目**：WorldEditPE —— 网易版《我的世界》基岩版的 WorldEdit 类模组（Python 编写）
- **架构**：参考 EngineHub/WorldEdit (Java, GPLv3)，用网易 ModSDK Python API 重实现
- **运行环境**：[中国版] MC Studio / 移动端 MinecraftPE_Netease，Python 2.x 语法
- **当前版本**：v0.1（2026-08-16，通知系统初步调通）

### 目录结构

```
behavior_pack/
  manifest.json
  WorldEditPE/
    modMain.py          # 入口：注册 Server/Client System
    Server.py           # 服务端系统：聊天指令 + 木斧交互
    Client.py           # 客户端系统：接收广播通知 → 本地 HUD 显示
    commands/           # 指令集（parser + 各指令模块）
    core/               # 会话/选区/历史/向量
    algorithms/         # 形状/填充/线条算法
    clipboard/          # 剪贴板
    brush/              # 刷子
    utils/              # messages(通知)/blocks(方块)
resource_pack/
  manifest.json
  textures/ui/icon.png
```

---

## 2. 核心架构经验

### 2.1 注册与生命周期
- 入口 `modMain.py` 必须用 `@Mod.Binding` + `@Mod.InitServer()` / `@Mod.InitClient()` 注册系统
- **RegisterSystem 第三个参数必须传字符串类路径**（网易 SDK 要求）：
  `serverApi.RegisterSystem(ModName, ModServer, "WorldEditPE.Server.WorldEditPEServerSystem")`
  传类对象（`WorldEditPEServerSystem`）会静默失败 — 这是原版代码的一个坑，已修正为字符串路径。
- `import` 路径需兼容两种 SDK 版本：`common.mod` vs `mod.common.mod`、
  `server.extraServerApi` vs `mod.server.extraServerApi`（try/except 双路导入）

### 2.2 指令前缀：用 `=` 不用 `//`
- 网易聊天系统会拦截以单个 `/` 开头的消息作为原生指令，`//` 会被当作聊天消息。
  但实测**手机版**下 `//` 开头同样可能不进入 `ServerChatEvent`（或被 UI 吞掉），
  **最终统一使用 `=` 前缀**（`=help`、`=pos1`...），这是调试后的稳定结论。

### 2.3 事件监听
```python
# 服务端监听引擎事件
engine_ns = serverApi.GetEngineNamespace()
engine_sys = serverApi.GetEngineSystemName()
self.ListenForEvent(engine_ns, engine_sys, 'ServerChatEvent', self, self.OnServerChat)
```
- `ServerChatEvent`：`args['message']`、`args['playerId']`
- 若指令被处理，设置 `args['cancel'] = True` 且 `args['message'] = ''` 取消广播
- **注意**：修改 `args['message']` 为通知文本在服务端日志可见，但**移动端聊天框不会显示替换后的消息**（WE15 实测）— 不要依赖此方案显示通知。

---

## 3. 🔥 通知系统（踩坑最多，重中之重）

### 3.1 玩家 ID 异常
- 移动端 `AddServerPlayerEvent` / `ServerChatEvent` 中的 playerId 实测为 **`-4294967295`**
  （一个异常/占位 ID，等价于 0xFFFFFFFE... 的负数形式？）
- 该 ID **可以**用于 `SetCommand(cmd, playerId, False)` 的 /tellraw @s（WE11 验证有效），
  但**不可靠**，部分手机版本下静默失败。

### 3.2 ❌ 无效方案（均已实测排除）
| 方案 | 结果 |
|---|---|
| `BroadcastToAllClient('WEPENotify', {...})` 广播 + 客户端 `ListenForEvent` | 事件未到达客户端，日志无 `Notify received` |
| `NotifyToClient(playerId, 'WEPENotify', {...})` 定向 | 依赖异常 playerId，不可靠 |
| 客户端 `SetTipMessage` / `SetPopupNotice` / `SetLeftCornerNotify` | 需事件到达客户端才能触发（上两条失败则全失效） |
| 修改 `args['message']` 替换聊天内容 | 服务端日志显示替换成功，移动端 UI 不显示 |
| `EnableServerTick()` + tick 队列延迟发送 | **`WorldEditPEServerSystem` 没有 `EnableServerTick` 属性**（该 API 不存在），报错后队列永不 flush |
| `@p` / `@a` 选择器且不传 playerId | `SetCommand` 缺 playerId 时可能随机执行或失败 |

### 3.3 ✅ 有效方案（v0.1 采用，WE16）
**原生 `/tellraw @s` + 显式 playerId 传递 + `/title @s actionbar` 双通道即时发送**：

```python
# utils/messages.py 核心
comp = serverApi.GetEngineCompFactory().CreateCommand(level_id)
comp.SetCommand('/tellraw @s {"rawtext":[{"text":"%s"}]}' % safe, pid, False)  # 聊天栏
comp.SetCommand('/title @s actionbar %s' % text, pid, False)                    # 动作栏
```

要点：
1. **即时发送**，不要用服务器 tick 队列（`EnableServerTick` 不存在）
2. 长文本（=help）按 `\n` 拆成多行，**逐行单独 SetCommand**（一次大 JSON 易失败/截断）
3. 颜色代码直接嵌入文本：`\xa7a`(绿) `\xa7c`(红) `\xa7e`(黄) `\xa7b`(蓝) `\xa7r`(重置)
4. JSON 转义：`\\`、`\"`、`\r`、`\n`
5. 保留备用通道：`BroadcastToAllClient`、`SendMsgToPlayer`（未来客户端 UI 方案可复用）
6. 每通道成功/失败都 `print` 诊断日志，方便远程日志定位

### 3.4 调试方法论（重要）
- 网易移动端日志通过 `[Developer] Starting mobile logger` 远程输出，控制台 print 可见
- **每个关键分支都加 print**（前缀 `[WorldEditPE]`+`[Notifier]`），这是定位「没执行 vs 执行了没效果」的唯一手段
- 判断标准：日志出现 `[Notifier] tellraw @s OK` = 发送成功；仍未显示 = 引擎/客户端问题
- 版本迭代建议一次性打包 WE##.zip 供测试，保留历史包便于 diff（WE11~WE16 均在 /workspace/uploads/）

---

## 4. 指令实现要点

- **选区**：pos1/pos2 存 `core/selector.py` 的 SelectionState；木斧左键=pos1、右键=pos2
- **木斧判定**：`CreateItem(player_id).GetPlayerItem(CARRIED, 0)` 检查 itemName 含 `wooden_axe`
- **方块操作**：`CreateBlockInfo`/`SetBlock`（网易 API 与 Java 不同，需查 API 文档 "世界-方块"）
- **历史/撤销**：`core/history.py` 记录每次操作前后快照，undo/redo 恢复
- **剪贴板**：`clipboard/dict_clipboard.py`，结构为 `{(x,y,z): (blockName, auxValue)}`
- **翻转**：`nz = -z` 修复了规范 Y 轴翻转的坐标映射（2016 版 WorldEdit 行为对齐）
- **自动朝向**：`transform.py` 用 `CreateRot` 的 `GetRot()` 拿玩家 yaw 换算 `north/south/east/west`

---

## 5. 发布与合规（v0.1 确立）

- **许可证**：GPLv3（与上游 EngineHub/WorldEdit 一致）
- **版权**：JiHong-Studio（ChengXing507 与 Ecaps）
- README 必须包含：原项目信息 + 相对原项目的改动说明（GPLv3 要求）+ 自写介绍（简介/指令集）
- 发布包：behavior_pack + resource_pack 打包成 zip，注意 manifest.json 的 uuid 唯一性
- **合规红线**：不得包含未经授权的第三方代码；引用 EngineHub/WorldEdit 需保留 GPL 声明

---

## 6. 已知问题与后续方向

- [x] v0.1 通知可达性：=help 等指令输出可显示（WE16 初步通过）
- [ ] 通知在多行/长文本下的排版优化（当前逐行 tellraw，颜色前缀会重复）
- [ ] 确认移动端不同版本（iOS/Android、不同 MC 版本）下一套通道是否全部有效
- [ ] 评估客户端 UI（自定义 UI 界面）作为通知通道的长期方案（需要 ui_defs + py UI）
- [ ] 指令集完善：当前缺 generatemobs/forest/generate 等高级指令
- [ ] 中文指令别名与多语言支持
- [ ] undo 内存优化（大选区快照占用）

---

*最后更新：2026-08-16*
