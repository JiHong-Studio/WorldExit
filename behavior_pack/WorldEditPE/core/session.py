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
PlayerSession: 玩家会话管理
对应 WorldEdit 的 LocalSession，管理选区、剪贴板、历史、刷子等
"""

from WorldEditPE.core.selector import SelectionState
from WorldEditPE.core.history import OperationStack
from WorldEditPE.core.operator import WorldOperator
from WorldEditPE.clipboard.dict_clipboard import DictClipboard


class PlayerSession(object):
    """玩家会话，每个玩家一个实例"""

    def __init__(self, player_id):
        self.player_id = player_id
        self.selection = SelectionState()
        self.clipboard = DictClipboard()
        self.history = OperationStack(max_size=50)
        self.operator = WorldOperator(dimension_id=0)
        self.brush = None
        self.brush_size = 3
        self.brush_pattern = None
        self.mask = None
        self.placement_pos = None

    def get_dimension(self):
        return self.selection.dimension_id

    def set_dimension(self, dim_id):
        self.selection._dimension_id = dim_id
        self.operator.dimension_id = dim_id

    def clear_all(self):
        self.selection.clear()
        self.clipboard.clear()
        self.history.clear()
        self.brush = None
        self.mask = None


# 全局会话管理器
_sessions = {}


def get_player_session(player_id):
    """获取或创建玩家会话"""
    if player_id not in _sessions:
        _sessions[player_id] = PlayerSession(player_id)
    return _sessions[player_id]


def remove_player_session(player_id):
    """清理玩家会话"""
    if player_id in _sessions:
        del _sessions[player_id]
