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
"""\u533a\u57df\u64cd\u4f5c\u547d\u4ee4 //set, //replace, //walls, //outline, //line"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.core.history import Operation
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.utils.blocks import parse_block_str, is_air
from WorldEditPE.algorithms.line import draw_walls, draw_outline, draw_line
from WorldEditPE.commands.parser import register_command


def cmd_set(player_id, args):
    if not args:
        Notifier(player_id).error('Usage: //set <block>')
        return
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    if not sel.is_complete():
        notifier.error('Make a selection first (//pos1, //pos2).')
        return
    block = parse_block_str(' '.join(args))
    if not block:
        notifier.error('Invalid block name.')
        return
    operator = session.operator
    operator.dimension_id = sel.dimension_id
    changes = {}
    old_blocks = {}
    for vec in sel.iter_positions():
        pt = vec.to_tuple()
        old = operator.get_block(vec)
        old_blocks[pt] = old
        changes[pt] = block
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=set', old_blocks, changes))
    notifier.info('Set %d blocks.' % count)


def cmd_replace(player_id, args):
    if len(args) < 1:
        Notifier(player_id).error('Usage: //replace [from] <to>')
        return
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    if not sel.is_complete():
        notifier.error('Make a selection first.')
        return
    if len(args) >= 2:
        from_block = parse_block_str(args[0])
        to_block = parse_block_str(args[1])
    else:
        from_block = None
        to_block = parse_block_str(args[0])
    if not to_block:
        notifier.error('Invalid block name.')
        return
    operator = session.operator
    operator.dimension_id = sel.dimension_id
    changes = {}
    old_blocks = {}
    for vec in sel.iter_positions():
        old = operator.get_block(vec)
        if old is None:
            continue
        if from_block is None:
            if is_air(old):
                continue
        else:
            if old.get('name') != from_block.get('name'):
                continue
        pt = vec.to_tuple()
        old_blocks[pt] = old
        changes[pt] = to_block
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=replace', old_blocks, changes))
    notifier.info('Replaced %d blocks.' % count)


def cmd_walls(player_id, args):
    if not args:
        Notifier(player_id).error('Usage: //walls <block>')
        return
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    if not sel.is_complete():
        notifier.error('Make a selection first.')
        return
    block = parse_block_str(' '.join(args))
    if not block:
        notifier.error('Invalid block name.')
        return
    minp, maxp = sel.get_min_max()
    operator = session.operator
    operator.dimension_id = sel.dimension_id
    # draw_walls now returns a dict directly
    changes = draw_walls(minp, maxp, block)
    old_blocks = {}
    for pt in changes:
        old_blocks[pt] = operator.get_block(pt)
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=walls', old_blocks, changes))
    notifier.info('Walls created: %d blocks.' % count)


def cmd_outline(player_id, args):
    if not args:
        Notifier(player_id).error('Usage: //outline <block>')
        return
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    if not sel.is_complete():
        notifier.error('Make a selection first.')
        return
    block = parse_block_str(' '.join(args))
    if not block:
        notifier.error('Invalid block name.')
        return
    minp, maxp = sel.get_min_max()
    operator = session.operator
    operator.dimension_id = sel.dimension_id
    # draw_outline now returns a dict directly
    changes = draw_outline(minp, maxp, block)
    old_blocks = {}
    for pt in changes:
        old_blocks[pt] = operator.get_block(pt)
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=outline', old_blocks, changes))
    notifier.info('Outline created: %d blocks.' % count)


def cmd_line(player_id, args):
    if not args:
        Notifier(player_id).error('Usage: //line <block>')
        return
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    if not sel.is_complete():
        notifier.error('Make a selection first.')
        return
    block = parse_block_str(' '.join(args))
    if not block:
        notifier.error('Invalid block name.')
        return
    operator = session.operator
    operator.dimension_id = sel.dimension_id
    # draw_line now returns a dict directly
    changes = draw_line(sel.pos1, sel.pos2, block)
    old_blocks = {}
    for pt in changes:
        old_blocks[pt] = operator.get_block(pt)
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=line', old_blocks, changes))
    notifier.info('Line drawn: %d blocks.' % count)


def init_region_commands():
    register_command('set', cmd_set)
    register_command('replace', cmd_replace)
    register_command('walls', cmd_walls)
    register_command('outline', cmd_outline)
    register_command('line', cmd_line)
