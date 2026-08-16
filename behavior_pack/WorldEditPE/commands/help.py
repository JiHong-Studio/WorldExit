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
"""帮助命令 =help, =?"""

from WorldEditPE.utils.messages import Notifier
from WorldEditPE.commands.parser import register_command, get_all_commands, get_display_prefix

# 所有帮助行合并为一条 (用 \n 分隔), 避免多次 SetCommand
HELP_TEXT = (u'\xa7e===== WorldEditPE Commands =====\n'
             u'\xa7a=pos1 [x y z]\xa77 - Set position 1\n'
             u'\xa7a=pos2 [x y z]\xa77 - Set position 2\n'
             u'\xa7a=wand\xa77 - Get wooden axe tool\n'
             u'\xa7a=sel\xa77 / =deselect\xa77 - Select / deselect\n'
             u'\xa7a=selinfo\xa77 - Show selection info\n'
             u'\xa7a=set <block>\xa77 - Fill selection\n'
             u'\xa7a=replace [from] <to>\xa77 - Replace blocks\n'
             u'\xa7a=walls <block>\xa77 - Build walls\n'
             u'\xa7a=outline <block>\xa77 - Build outline\n'
             u'\xa7a=line <block>\xa77 - Draw a line\n'
             u'\xa7a=cyl <block> <r> [h]\xa77 - Cylinder\n'
             u'\xa7a=hcyl <block> <r> [h]\xa77 - Hollow cylinder\n'
             u'\xa7a=sphere <block> <r>\xa77 - Sphere\n'
             u'\xa7a=hsphere <block> <r>\xa77 - Hollow sphere\n'
             u'\xa7a=pyramid <block> <size>\xa77 - Pyramid\n'
             u'\xa7a=cone <block> <r> <h>\xa77 - Cone\n'
             u'\xa7a=copy\xa77 - Copy selection\n'
             u'\xa7a=cut\xa77 - Cut selection\n'
             u'\xa7a=paste [-a]\xa77 - Paste clipboard\n'
             u'\xa7a=stack <count> [dir]\xa77 - Stack selection\n'
             u'\xa7a=rotate <angle>\xa77 - Rotate clipboard\n'
             u'\xa7a=flip [dir]\xa77 - Flip clipboard (auto from facing)\n'
             u'\xa7a=fill <block> <r>\xa77 - Fill holes\n'
             u'\xa7a=fillr <block> <r>\xa77 - Recursive fill\n'
             u'\xa7a=drain <radius>\xa77 - Drain liquids\n'
             u'\xa7a=undo\xa77 / =redo\xa77 - Undo/Redo\n'
             u'\xa7a=help\xa77 or =?\xa77 - Show this help')


def cmd_help(player_id, args):
    notifier = Notifier(player_id)
    notifier.raw(HELP_TEXT)


def cmd_test(player_id, args):
    notifier = Notifier(player_id)
    notifier.info('WorldEditPE is working!')
    try:
        pos_comp = None
        import server.extraServerApi as serverApi
        pos_comp = serverApi.GetEngineCompFactory().CreatePos(player_id)
        pos = pos_comp.GetPos()
        notifier.info('Position: (%.1f, %.1f, %.1f)' % (pos[0], pos[1], pos[2]))
    except Exception as e:
        notifier.warn('Could not get position: %s' % str(e))


def init_help_command():
    register_command('help', cmd_help)
    register_command('?', cmd_help)
    register_command('test', cmd_test)
