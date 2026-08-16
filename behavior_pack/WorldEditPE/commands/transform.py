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
"""变换命令 =rotate, =flip"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.commands.parser import register_command
import server.extraServerApi as serverApi


def _get_player_yaw(player_id):
    """获取玩家 Yaw 角度 (偏航角)
    Minecraft: -180=北, -90=东, 0=南, 90=西, 180=北
    """
    try:
        comp = serverApi.GetEngineCompFactory().CreateRot(player_id)
        rot = comp.GetRot()
        # rot = (pitch, yaw) 或 (yaw, pitch)? 官方文档: GetRot返回(俯仰, 偏航)
        # 实际上是 (pitch, yaw)
        yaw = rot[1]  # 第二个是偏航角
        return yaw
    except Exception as e:
        print '[WorldEditPE] GetRot error: %s' % str(e)
        return None


def _yaw_to_direction(yaw):
    """将 yaw 角度转换为基本方向
    Yaw: -180=北, -90=东, 0=南, 90=西, 180=北
    """
    if yaw is None:
        return None
    # 标准化到 0-360
    yaw = yaw % 360
    if yaw < 0:
        yaw += 360
    # 判断方向
    if yaw >= 315 or yaw < 45:
        return 'south'  # 面向正Z+
    elif yaw >= 45 and yaw < 135:
        return 'west'   # 面向正X-
    elif yaw >= 135 and yaw < 225:
        return 'north'  # 面向正Z-
    else:
        return 'east'   # 面向正X+


def cmd_rotate(player_id, args):
    """=rotate <angle> - 旋转剪贴板中的内容"""
    session = get_player_session(player_id)
    notifier = Notifier(player_id)

    if session.clipboard.is_empty():
        notifier.error('Clipboard is empty. Use =copy first.')
        return

    if not args:
        notifier.error('Usage: =rotate <angle> (90, 180, 270)')
        return

    try:
        angle = int(args[0])
        if angle % 90 != 0:
            notifier.error('Angle must be a multiple of 90.')
            return
        angle = angle % 360
        if angle == 0:
            notifier.info('No rotation needed.')
            return
    except ValueError:
        notifier.error('Invalid angle: %s' % args[0])
        return

    count = len(session.clipboard)
    session.clipboard.rotate(angle)
    notifier.info('Rotated %d blocks by %d degrees.' % (count, angle))


def cmd_flip(player_id, args):
    """=flip [direction] - 翻转剪贴板中的内容
    不带参数时根据玩家准心朝向自动判断方向
    """
    session = get_player_session(player_id)
    notifier = Notifier(player_id)

    if session.clipboard.is_empty():
        notifier.error('Clipboard is empty. Use =copy first.')
        return

    # 确定方向
    direction = None
    if args:
        valid_dirs = {
            'north': 'north', 'south': 'south', 'east': 'east', 'west': 'west',
            'up': 'up', 'down': 'down',
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
            'u': 'up', 'd': 'down',
        }
        direction = valid_dirs.get(args[0].lower())
        if not direction:
            notifier.error('Invalid direction. Use: north, south, east, west, up, down')
            return
    else:
        # 无参数时自动从准心朝向判断
        yaw = _get_player_yaw(player_id)
        direction = _yaw_to_direction(yaw)
        if direction is None:
            notifier.error('Could not determine facing direction.')
            return
        notifier.info('Facing: %s' % direction)

    count = len(session.clipboard)
    session.clipboard.flip(direction)
    notifier.info('Flipped %d blocks along %s axis.' % (count, direction))


def init_transform_commands():
    register_command('rotate', cmd_rotate)
    register_command('flip', cmd_flip)
