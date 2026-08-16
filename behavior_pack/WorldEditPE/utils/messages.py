# -*- coding: utf-8 -*-
# WorldEditPE - WorldEdit for NetEase Minecraft (Bedrock)
# Copyright (C) 2026 JiHong-Studio (ChengXing507 & Ecaps)
# This file is part of WorldEditPE.
# WorldEditPE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# WorldEditPE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with WorldEditPE.  If not, see <https://www.gnu.org/licenses/>.
# Notifier - multi-channel notification
# 通道1(主): /tellraw @s with playerId (WE11 已验证手机版可显示)
# 通道2: /title @s actionbar with playerId (WE11 动作栏)
# 通道3: BroadcastToAllClient -> 客户端 HUD (备用)
# 通道4: SendMsgToPlayer 悄悄对自己说 (备用)
# 即时发送, 不依赖 tick

import server.extraServerApi as serverApi

PREFIX = u'\xa7b[WorldEdit]\xa7r '

# 服务端系统实例引用 (Server.py 设置 messages.SERVER_SYSTEM = self)
SERVER_SYSTEM = None


class Notifier(object):
    """Send formatted messages to a specific player."""

    def __init__(self, player_id):
        super(Notifier, self).__init__()
        self._player_id = player_id

    def _send(self, text):
        """Send through multiple channels."""
        pid = self._player_id
        if not pid:
            print '[Notifier] no player id!'
            return

        level_id = None
        try:
            level_id = serverApi.GetLevelId()
        except:
            pass
        if not level_id:
            print '[Notifier] no level id!'
            return

        lines = text.split('\n')
        safe = text.replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '\\n')

        # 通道1(主): /tellraw @s with playerId - 每行单独一条 (WE11 已验证)
        try:
            comp = serverApi.GetEngineCompFactory().CreateCommand(level_id)
            for line in lines:
                l = line.strip()
                if not l:
                    continue
                ls = l.replace('\\', '\\\\').replace('"', '\\"').replace('\r', '')
                comp.SetCommand('/tellraw @s {"rawtext":[{"text":"%s"}]}' % ls, pid, False)
            print '[Notifier] tellraw @s OK (%d lines)' % len(lines)
        except Exception as e:
            print '[Notifier] tellraw @s ERR: %s' % str(e)

        # 通道2: /title @s actionbar with playerId (WE11 动作栏)
        try:
            comp = serverApi.GetEngineCompFactory().CreateCommand(level_id)
            first = lines[0] if lines else text
            comp.SetCommand('/title @s actionbar %s' % first, pid, False)
            print '[Notifier] title actionbar OK'
        except Exception as e:
            print '[Notifier] title actionbar ERR: %s' % str(e)

        # 通道3: BroadcastToAllClient -> 客户端 HUD (备用)
        try:
            if SERVER_SYSTEM is not None:
                SERVER_SYSTEM.BroadcastToAllClient('WEPENotify', {'msg': text})
                print '[Notifier] broadcast OK'
            else:
                print '[Notifier] SERVER_SYSTEM is None!'
        except Exception as e:
            print '[Notifier] broadcast ERR: %s' % str(e)

        # 通道4: SendMsgToPlayer 悄悄对自己说 (备用)
        try:
            comp = serverApi.GetEngineCompFactory().CreateMsg(level_id)
            comp.SendMsgToPlayer(pid, pid, text)
            print '[Notifier] whisper OK'
        except Exception as e:
            print '[Notifier] whisper ERR: %s' % str(e)

    def raw(self, text):
        self._send(text)

    def info(self, text):
        self._send(PREFIX + u'\xa7a' + text + u'\xa7r')

    def error(self, text):
        self._send(PREFIX + u'\xa7c' + text + u'\xa7r')

    def warn(self, text):
        self._send(PREFIX + u'\xa7e' + text + u'\xa7r')
