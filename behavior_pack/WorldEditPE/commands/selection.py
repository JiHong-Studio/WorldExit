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
"""选区命令 //pos1, //pos2, //wand, //sel, //desel, //selinfo"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.commands.parser import register_command


def cmd_pos1(player_id, args):
    """//pos1 [x y z] - 设置第1个点"""
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    if args and len(args) >= 3:
        try:
            x, y, z = int(args[0]), int(args[1]), int(args[2])
            session.selection.set_pos1((x, y, z))
            notifier.info('Position 1 set to (%d, %d, %d)' % (x, y, z))
            return
        except ValueError:
            notifier.error('Invalid coordinates.')
    _set_pos_from_player(player_id, is_pos1=True)

def cmd_pos2(player_id, args):
    """//pos2 [x y z] - 设置第2个点"""
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    if args and len(args) >= 3:
        try:
            x, y, z = int(args[0]), int(args[1]), int(args[2])
            session.selection.set_pos2((x, y, z))
            notifier.info('Position 2 set to (%d, %d, %d)' % (x, y, z))
            return
        except ValueError:
            notifier.error('Invalid coordinates.')
    _set_pos_from_player(player_id, is_pos1=False)

def cmd_wand(player_id, args):
    """//wand - 获取木斧"""
    try:
        import server.extraServerApi as serverApi
        comp = serverApi.GetEngineCompFactory().CreateItem(player_id)
        comp.SpawnItemToPlayerInv({'itemName': 'minecraft:wooden_axe', 'count': 1, 'aux': 0}, player_id)
        Notifier(player_id).info('Wooden axe given! Left-click = pos1, Right-click = pos2.')
    except Exception as e:
        Notifier(player_id).error('Failed to give wand: %s' % str(e))

def cmd_sel(player_id, args):
    """//sel - 选区信息"""
    Notifier(player_id).info('Current selection mode: cuboid')

def cmd_desel(player_id, args):
    """//desel - 清除选区"""
    get_player_session(player_id).selection.clear()
    Notifier(player_id).info('Selection cleared.')

def cmd_sel_info(player_id, args):
    """//selinfo - 显示选区信息"""
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    lines = sel.get_info()
    if not lines:
        notifier.warn('No selection defined.')
        notifier.info('Use //pos1 and //pos2 to set positions.')
    else:
        for line in lines:
            notifier.raw(line)

def _set_pos_from_player(player_id, is_pos1=True):
    session = get_player_session(player_id)
    try:
        import server.extraServerApi as serverApi
        pos_comp = serverApi.GetEngineCompFactory().CreatePos(player_id)
        pos = pos_comp.GetPos()
        dim_comp = serverApi.GetEngineCompFactory().CreateDimension(player_id)
        dim_id = dim_comp.GetEntityDimensionId()
        block_pos = (int(pos[0]), int(pos[1]), int(pos[2]))
        if is_pos1:
            session.selection.set_pos1(block_pos, dim_id)
        else:
            session.selection.set_pos2(block_pos, dim_id)
        session.set_dimension(dim_id)
    except Exception as e:
        Notifier(player_id).error('Failed to get position: %s' % str(e))

def init_selection_commands():
    register_command('pos1', cmd_pos1)
    register_command('pos2', cmd_pos2)
    register_command('wand', cmd_wand)
    register_command('sel', cmd_sel)
    register_command('deselect', cmd_desel)
    register_command('desel', cmd_desel)
    register_command('selinfo', cmd_sel_info)
