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
"""
WorldEditPE 客户端系统
监听服务器广播/定向通知事件，通过客户端 HUD 显示
"""

import client.extraClientApi as clientApi

ClientSystem = clientApi.GetClientSystemCls()


class WorldEditPEClientSystem(ClientSystem):
    """WorldEditPE 客户端系统"""

    def __init__(self, namespace, system_name):
        super(WorldEditPEClientSystem, self).__init__(namespace, system_name)
        print '[WorldEditPE] Client system initialized. ns=%s name=%s' % (namespace, system_name)

        # 监听服务器系统的通知事件
        # 关键: 必须使用服务器系统的 namespace 和 systemName!
        # 服务器系统: ns=WorldEditPE, name=WorldEditPEServerSystem
        # 客户端系统: ns=WorldEditPE, name=WorldEditPEClientSystem
        self.ListenForEvent('WorldEditPE', 'WorldEditPEServerSystem', 'WEPENotify', self, self._on_notify)

        # 也监听自己的命名空间 (广播可能走这里)
        self.ListenForEvent(namespace, system_name, 'WEPENotify', self, self._on_notify)

        # 引擎命名空间
        try:
            engine_ns = clientApi.GetEngineNamespace()
            engine_sys = clientApi.GetEngineSystemName()
            self.ListenForEvent(engine_ns, engine_sys, 'WEPENotify', self, self._on_notify)
        except:
            pass

        print '[WorldEditPE] Client: listening for WEPENotify events'

    def _on_notify(self, args):
        """收到服务器通知事件，在客户端显示."""
        msg = args.get('msg', '')
        if not msg:
            return
        print '[WorldEditPE][Client] Notify received: %s' % msg[:50]

        try:
            player_id = clientApi.GetLocalPlayerId()
            if not player_id:
                print '[WorldEditPE][Client] No local player!'
                return

            # 通道1: Tip 消息 (物品栏上方)
            game_comp = clientApi.GetEngineCompFactory().CreateGame(player_id)
            game_comp.SetTipMessage(msg)
            print '[WorldEditPE][Client] SetTipMessage OK'

            # 通道2: Popup 消息 (Tip 下方)
            game_comp.SetPopupNotice(msg, '')
            print '[WorldEditPE][Client] SetPopupNotice OK'

            # 通道3: 左上角通知
            try:
                level_id = clientApi.GetLevelId()
                notify_comp = clientApi.GetEngineCompFactory().CreateTextNotifyClient(level_id)
                notify_comp.SetLeftCornerNotify(msg)
                print '[WorldEditPE][Client] SetLeftCornerNotify OK'
            except Exception as e:
                print '[WorldEditPE][Client] LeftCorner ERR: %s' % str(e)

        except Exception as e:
            print '[WorldEditPE][Client] Display error: %s' % str(e)

    def Destroy(self):
        print '[WorldEditPE] Client system destroyed.'
        super(WorldEditPEClientSystem, self).Destroy()
