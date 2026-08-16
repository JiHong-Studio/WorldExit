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
撤销/重做栈
对应 WorldEdit 的 ChangeSet / BlockOptimizedHistory
"""


class Operation(object):
    """一次操作记录"""

    def __init__(self, name, old_blocks, new_blocks):
        self.name = name
        self.old_blocks = dict(old_blocks)
        self.new_blocks = dict(new_blocks)


class OperationStack(object):
    """操作历史栈，支持撤销/重做"""

    def __init__(self, max_size=50):
        self._undo_stack = []
        self._redo_stack = []
        self._max_size = max_size

    def push(self, operation):
        self._undo_stack.append(operation)
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0)
        self._redo_stack = []

    def undo(self):
        if not self._undo_stack:
            return None
        op = self._undo_stack.pop()
        self._redo_stack.append(op)
        return op.old_blocks, op.name

    def redo(self):
        if not self._redo_stack:
            return None
        op = self._redo_stack.pop()
        self._undo_stack.append(op)
        return op.new_blocks, op.name

    def can_undo(self):
        return len(self._undo_stack) > 0

    def can_redo(self):
        return len(self._redo_stack) > 0

    def clear(self):
        self._undo_stack = []
        self._redo_stack = []
