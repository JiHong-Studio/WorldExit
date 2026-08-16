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
WorldOperator \u65b9\u5757\u64cd\u4f5c\u5c01\u88c5
\u5bf9\u5e94 WorldEdit \u7684 EditSession/Extent \u5c42
"""

from WorldEditPE.utils.blocks import AIR

OLD_HANDLING_REPLACE = 0


class WorldOperator(object):
    """\u65b9\u5757\u64cd\u4f5c\u5668\uff0c\u5c01\u88c5\u65b9\u5757\u8bfb\u5199"""

    def __init__(self, dimension_id=0):
        self.dimension_id = dimension_id
        self._block_info_comp = None

    def _get_comp(self):
        if self._block_info_comp is None:
            import server.extraServerApi as serverApi
            self._block_info_comp = serverApi.GetEngineCompFactory().CreateBlockInfo(
                serverApi.GetLevelId())
        return self._block_info_comp

    def get_block(self, pos):
        """\u83b7\u53d6\u65b9\u5757\uff0c\u8fd4\u56de blockDict \u6216 None"""
        comp = self._get_comp()
        try:
            result = comp.GetBlockNew(tuple(pos), self.dimension_id)
            if result is None:
                return None
            name = result.get('name', 'minecraft:air')
            aux = int(result.get('aux', 0))
            return {"name": name, "aux": aux}
        except Exception:
            return None

    def set_block(self, pos, block_dict, old_handling=OLD_HANDLING_REPLACE, update_neighbors=True):
        """\u8bbe\u7f6e\u65b9\u5757\uff0c\u8fd4\u56de True \u8868\u793a\u65b9\u5757\u53d1\u751f\u4e86\u6539\u53d8"""
        comp = self._get_comp()
        try:
            return comp.SetBlockNew(
                tuple(pos),
                block_dict,
                old_handling,
                self.dimension_id,
                True,
                update_neighbors
            )
        except Exception:
            return False

    def delete_block(self, pos, update_neighbors=True):
        """\u5220\u9664\u65b9\u5757\uff08\u8bbe\u4e3a\u7a7a\u6c14\uff09"""
        return self.set_block(pos, AIR, OLD_HANDLING_REPLACE, update_neighbors)

    def set_blocks_batch(self, changes):
        """\u6279\u91cf\u8bbe\u7f6e\u65b9\u5757\uff0c\u8fd4\u56de\u5b9e\u9645\u6539\u53d8\u7684\u4e2a\u6570"""
        count = 0
        for pt, block_dict in changes.items():
            if self.set_block(pt, block_dict):
                count += 1
        return count
