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
# Block parsing and matching utilities for WorldEditPE

AIR = {'name': 'air', 'aux': 0}

# Known liquids (Minecraft 1.12 / PE names)
_LIQUID_NAMES = frozenset([
    'water', 'flowing_water', 'water_still', 'water_flowing',
    'lava', 'flowing_lava', 'lava_still', 'lava_flowing',
])


def parse_block_str(block_str):
    """Parse a block string like 'stone' or 'wool:1' into {'name': ..., 'aux': ...}.

    Supported forms:
      'stone'               -> {'name': 'minecraft:stone', 'aux': 0}
      'wool:1'              -> {'name': 'minecraft:wool', 'aux': 1}
      'minecraft:stone'     -> {'name': 'minecraft:stone', 'aux': 0}
      'minecraft:wool:1'    -> {'name': 'minecraft:wool', 'aux': 1}
      'air'                 -> {'name': 'air', 'aux': 0}

    Returns a dict with 'name' and 'aux' keys, or None if parsing fails.
    """
    if block_str is None:
        return None
    block_str = block_str.strip().lower()
    if not block_str:
        return None

    # Handle 'minecraft:block:aux' - split on the FIRST two colons only
    name = None
    aux = 0

    if ':' not in block_str:
        # plain block name, e.g. 'stone'
        name = block_str
    else:
        # Split at the first colon to separate the namespace if present.
        head, sep, tail = block_str.partition(':')
        if ':' in tail:
            # 'minecraft:block:aux' or 'ns:block:aux'
            ns, block, rest_aux = head, tail.split(':', 1)[0], tail.split(':', 1)[1]
            name = ns + ':' + block
            try:
                aux = int(rest_aux)
            except ValueError:
                aux = 0
        else:
            # either 'minecraft:stone' or 'wool:1'
            try:
                aux = int(tail)
                name = head
            except ValueError:
                name = block_str  # 'minecraft:stone'

    if not name:
        return None

    # Normalise namespace
    if ':' not in name:
        name = 'minecraft:' + name

    return {'name': name, 'aux': aux}


def is_air(block_dict):
    """Check if the block dict represents air (or is None)."""
    if block_dict is None:
        return True
    name = block_dict.get('name', '')
    if name is None:
        name = ''
    name = name.lower()
    return name in ('', 'air', 'minecraft:air') or 'air' in name


def is_liquid(block_dict):
    """Check if the block dict represents a liquid."""
    if block_dict is None:
        return False
    name = block_dict.get('name', '')
    if name is None:
        return False
    name = name.lower()
    for liquid_name in _LIQUID_NAMES:
        if liquid_name in name:
            return True
    return False


def block_dict_matches(a, b):
    """Check if two block dicts represent the same block (name + aux)."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    a_name = (a.get('name') or '').lower()
    b_name = (b.get('name') or '').lower()
    a_aux = int(a.get('aux', 0))
    b_aux = int(b.get('aux', 0))
    return a_name == b_name and a_aux == b_aux
