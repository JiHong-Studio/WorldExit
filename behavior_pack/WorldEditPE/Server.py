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
WorldEditPEServerSystem - Main server-side system for WorldEditPE
"""

import server.extraServerApi as serverApi

from WorldEditPE.commands.parser import parse_and_execute
from WorldEditPE.commands import init_all_commands
from WorldEditPE.core.session import get_player_session, remove_player_session
from WorldEditPE.utils import messages
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.brush.base import apply_brush

ServerSystem = serverApi.GetServerSystemCls()


class WorldEditPEServerSystem(ServerSystem):
    """Main server system"""

    def __init__(self, namespace, system_name):
        super(WorldEditPEServerSystem, self).__init__(namespace, system_name)
        print "===== WorldEditPE Server System Initialising ====="
        print "[WorldEditPE] System: ns=%s name=%s" % (namespace, system_name)

        # 设置全局引用（供 Notifier 使用）- 必须设置 messages 模块中的变量!
        messages.SERVER_SYSTEM = self

        init_all_commands()

        engine_ns = serverApi.GetEngineNamespace()
        engine_sys = serverApi.GetEngineSystemName()
        print "[WorldEditPE] Engine: ns=%s sys=%s" % (engine_ns, engine_sys)

        # 监听聊天事件
        self.ListenForEvent(engine_ns, engine_sys, 'ServerChatEvent', self, self.OnServerChat)
        # 监听左键破坏方块
        self.ListenForEvent(engine_ns, engine_sys, 'ServerPlayerTryDestroyBlockEvent', self, self.OnPlayerTryDestroyBlock)
        # 监听右键点击方块
        self.ListenForEvent(engine_ns, engine_sys, 'ServerItemUseOnEvent', self, self.OnServerItemUseOn)
        # 监听玩家加入
        self.ListenForEvent(engine_ns, engine_sys, 'AddServerPlayerEvent', self, self.OnAddServerPlayer)

        # 启用服务器 tick
        print "===== WorldEditPE Server System Ready ====="

    def _notify(self, player_id, msg):
        """发送通知到玩家"""
        try:
            Notifier(player_id).info(msg)
        except Exception as e:
            print "[WorldEditPE] Notifier error: %s" % str(e)

    def OnAddServerPlayer(self, args):
        player_id = args.get('id', '') or args.get('playerId', '')
        if player_id:
            print "[WorldEditPE] Player joined: %s" % player_id
            self._notify(player_id, 'WorldEditPE loaded! Type =help for commands.')

    def OnServerChat(self, args):
        msg = args.get('message', '') or ''
        player_id = args.get('playerId', '') or args.get('id', '') or ''
        print "[WorldEditPE] OnServerChat: player=%s msg='%s'" % (player_id, msg)
        if not msg or not player_id:
            return
        if not msg.startswith('=') and not msg.startswith('//'):
            return
        handled = parse_and_execute(player_id, msg)
        if handled:
            args['cancel'] = True
            args['message'] = ''
            print "[WorldEditPE] Chat cancelled, command executed"
            self._notify(player_id, 'Executed: ' + msg)

    def OnPlayerTryDestroyBlock(self, args):
        """左键点击方块 - 如果持有木斧，设置 pos1 并取消事件"""
        player_id = args.get('playerId', '')
        if not player_id or not self._is_holding_wand(player_id):
            return
        x = args.get('x', 0)
        y = args.get('y', 0)
        z = args.get('z', 0)
        print "[WorldEditPE] Left click (wand): %s pos=(%d,%d,%d)" % (player_id, x, y, z)
        session = get_player_session(player_id)
        session.selection.set_pos1((x, y, z))
        try:
            dim_id = args.get('dimensionId', 0)
            session.set_dimension(dim_id)
        except:
            pass
        self._notify(player_id, "Position 1 set to (%d, %d, %d)" % (x, y, z))
        args['cancel'] = True

    def OnServerItemUseOn(self, args):
        """右键点击方块 (ServerItemUseOnEvent)"""
        player_id = args.get('entityId', '')
        x = args.get('x', None)
        y = args.get('y', None)
        z = args.get('z', None)
        if not player_id or x is None or y is None or z is None:
            return
        self._handle_right_click(player_id, x, y, z, args)

    def _handle_right_click(self, player_id, x, y, z, args):
        """处理右键点击方块"""
        session = get_player_session(player_id)

        if self._is_holding_wand(player_id):
            last = getattr(session, '_last_rc', None)
            if last == (x, y, z):
                return
            session._last_rc = (x, y, z)

            print "[WorldEditPE] Right click (wand): %s pos=(%d,%d,%d)" % (player_id, x, y, z)
            session.selection.set_pos2((x, y, z))
            try:
                dim_id = args.get('dimensionId', session.get_dimension())
                session.set_dimension(dim_id)
            except:
                pass
            self._notify(player_id, "Position 2 set to (%d, %d, %d)" % (x, y, z))
            try:
                if 'ret' in args:
                    args['ret'] = True
                if 'cancel' in args:
                    args['cancel'] = True
            except:
                pass
            return

        if session.brush is not None:
            last = getattr(session, '_last_rc', None)
            if last == (x, y, z):
                return
            session._last_rc = (x, y, z)
            print "[WorldEditPE] Right click (brush): %s pos=(%d,%d,%d)" % (player_id, x, y, z)
            apply_brush(player_id, (x, y, z))
            try:
                if 'ret' in args:
                    args['ret'] = True
                if 'cancel' in args:
                    args['cancel'] = True
            except:
                pass

    def _is_holding_wand(self, player_id):
        try:
            comp = serverApi.GetEngineCompFactory().CreateItem(player_id)
            try:
                item = comp.GetPlayerItem(serverApi.GetMinecraftEnum().ItemPosType.CARRIED, 0)
            except:
                try:
                    item = comp.GetPlayerItem(serverApi.GetMinecraftEnum().ItemPosType.INVENTORY, 0)
                except:
                    item = None
            if item is None:
                return False
            name = (item.get('itemName', '') or '').lower()
            return 'wooden_axe' in name or 'wood_axe' in name
        except:
            return False

    def Destroy(self):
        print "[WorldEditPE] Server shutdown."
        super(WorldEditPEServerSystem, self).Destroy()
