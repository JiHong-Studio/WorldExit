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
"""历史命令 //undo, //redo, //clearhistory"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.commands.parser import register_command

def cmd_undo(player_id, args):
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    result = session.history.undo()
    if result is None:
        notifier.error('Nothing to undo.')
        return
    old_blocks, name = result
    operator = session.operator
    operator.dimension_id = session.get_dimension()
    count = operator.set_blocks_batch(old_blocks)
    notifier.info('Undo %s: restored %d blocks.' % (name, count))

def cmd_redo(player_id, args):
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    result = session.history.redo()
    if result is None:
        notifier.error('Nothing to redo.')
        return
    new_blocks, name = result
    operator = session.operator
    operator.dimension_id = session.get_dimension()
    count = operator.set_blocks_batch(new_blocks)
    notifier.info('Redo %s: applied %d blocks.' % (name, count))

def cmd_clearhistory(player_id, args):
    get_player_session(player_id).history.clear()
    Notifier(player_id).info('History cleared.')

def init_history_commands():
    register_command('undo', cmd_undo)
    register_command('redo', cmd_redo)
    register_command('clearhistory', cmd_clearhistory)
