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
Command registry initialisation.
"""

from . import selection
from . import region
from . import generation
from . import clipboard
from . import utility
from . import historycmd
from . import help as helpcmd
from . import brush
from . import transform


def init_all_commands():
    """Register all command handlers. Called once at server startup."""
    print "[WorldEditPE] Initialising all commands..."
    selection.init_selection_commands()
    region.init_region_commands()
    generation.init_generation_commands()
    clipboard.init_clipboard_commands()
    utility.init_utility_commands()
    historycmd.init_history_commands()
    helpcmd.init_help_command()
    brush.init_brush_commands()
    transform.init_transform_commands()
    print "[WorldEditPE] All commands initialised."
