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
"""刷子命令 //brush, //mask, //size"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.utils.blocks import parse_block_str
from WorldEditPE.commands.parser import register_command

def cmd_brush(player_id, args):
    if len(args) < 2:
        Notifier(player_id).error('Usage: //brush <sphere|cylinder> <block> <radius>')
        return
    brush_type = args[0].lower()
    block = parse_block_str(args[1])
    radius = int(args[2]) if len(args) >= 3 and args[2].isdigit() else 3
    session = get_player_session(player_id)
    session.brush = brush_type
    session.brush_size = radius
    session.brush_pattern = block
    Notifier(player_id).info('Brush set: %s, size=%d' % (brush_type, radius))

def cmd_size(player_id, args):
    if not args:
        Notifier(player_id).error('Usage: //size <radius>')
        return
    try:
        size = int(args[0])
    except ValueError:
        Notifier(player_id).error('Invalid size.')
        return
    get_player_session(player_id).brush_size = size
    Notifier(player_id).info('Brush size set to %d.' % size)

def cmd_mask(player_id, args):
    session = get_player_session(player_id)
    if not args:
        session.mask = None
        Notifier(player_id).info('Mask cleared.')
        return
    session.mask = parse_block_str(' '.join(args))
    Notifier(player_id).info('Mask set.')

def init_brush_commands():
    register_command('brush', cmd_brush)
    register_command('size', cmd_size)
    register_command('mask', cmd_mask)
