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
"""\u51e0\u4f55\u751f\u6210\u547d\u4ee4 //cyl, //hcyl, //sphere, //hsphere, //pyramid, //cone"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.core.history import Operation
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.utils.blocks import parse_block_str
from WorldEditPE.utils.vectors import BlockVector3
from WorldEditPE.algorithms.shapes import (
    generate_cylinder, generate_hollow_cylinder,
    generate_sphere, generate_hollow_sphere,
    generate_pyramid, generate_cone
)
from WorldEditPE.commands.parser import register_command


def _get_center(player_id):
    try:
        import server.extraServerApi as serverApi
        pos_comp = serverApi.GetEngineCompFactory().CreatePos(player_id)
        pos = pos_comp.GetPos()
        dim_comp = serverApi.GetEngineCompFactory().CreateDimension(player_id)
        dim_id = dim_comp.GetEntityDimensionId()
        session = get_player_session(player_id)
        session.set_dimension(dim_id)
        return BlockVector3(int(pos[0]), int(pos[1]), int(pos[2]))
    except Exception:
        return None


def _do_generate(player_id, args, shape_name, shape_type, hollow=False):
    if not args:
        Notifier(player_id).error('Usage: //%s <block> <radius> [height]' % shape_name)
        return
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    block = parse_block_str(args[0])
    if not block:
        notifier.error('Invalid block name.')
        return
    if len(args) < 2:
        notifier.error('Radius required.')
        return
    try:
        radius = int(args[1])
    except ValueError:
        notifier.error('Invalid radius.')
        return
    center = _get_center(player_id)
    if center is None:
        notifier.error('Failed to get position.')
        return
    height = int(args[2]) if len(args) >= 3 else 1

    # Generate shape positions (generator yields (x,y,z) tuples)
    if shape_type == 'cylinder':
        if hollow:
            pos_gen = generate_hollow_cylinder(center, radius, height, block)
        else:
            pos_gen = generate_cylinder(center, radius, height, block)
    elif shape_type == 'sphere':
        if hollow:
            pos_gen = generate_hollow_sphere(center, radius, block)
        else:
            pos_gen = generate_sphere(center, radius, block)
    elif shape_type == 'pyramid':
        pos_gen = generate_pyramid(center, radius, block)
    elif shape_type == 'cone':
        pos_gen = generate_cone(center, radius, height, block)
    else:
        notifier.error('Unknown shape.')
        return

    # Convert generator to {pos: block_dict}
    changes = {}
    for pt in pos_gen:
        changes[pt] = block

    if not changes:
        notifier.error('No blocks generated.')
        return

    operator = session.operator
    operator.dimension_id = session.get_dimension()
    old_blocks = {}
    for pt in changes:
        old_blocks[pt] = operator.get_block(pt)

    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=' + shape_name, old_blocks, changes))
    notifier.info('%s created: %d blocks.' % (shape_name, count))


def cmd_cyl(player_id, args):
    _do_generate(player_id, args, 'cyl', 'cylinder', hollow=False)

def cmd_hcyl(player_id, args):
    _do_generate(player_id, args, 'hcyl', 'cylinder', hollow=True)

def cmd_sphere(player_id, args):
    _do_generate(player_id, args, 'sphere', 'sphere', hollow=False)

def cmd_hsphere(player_id, args):
    _do_generate(player_id, args, 'hsphere', 'sphere', hollow=True)

def cmd_pyramid(player_id, args):
    _do_generate(player_id, args, 'pyramid', 'pyramid', hollow=False)

def cmd_cone(player_id, args):
    _do_generate(player_id, args, 'cone', 'cone', hollow=False)


def init_generation_commands():
    register_command('cyl', cmd_cyl)
    register_command('hcyl', cmd_hcyl)
    register_command('sphere', cmd_sphere)
    register_command('hsphere', cmd_hsphere)
    register_command('pyramid', cmd_pyramid)
    register_command('cone', cmd_cone)
