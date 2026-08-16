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
WorldEditPE
基于 EngineHub/WorldEdit 架构的我的世界中国版模组

入口文件（对应 WorldEdit.java）
- 注册服务端/客户端 System（第三个参数必须是字符串类路径）
- 初始化命令系统
"""

_Mod = None
_serverApi = None
_clientApi = None

try:
    from common.mod import Mod
    _Mod = Mod
except ImportError:
    from mod.common.mod import Mod
    _Mod = Mod

try:
    import server.extraServerApi as serverApi
    _serverApi = serverApi
except ImportError:
    import mod.server.extraServerApi as serverApi
    _serverApi = serverApi

try:
    import client.extraClientApi as clientApi
    _clientApi = clientApi
except ImportError:
    import mod.client.extraClientApi as clientApi
    _clientApi = clientApi

Mod = _Mod
serverApi = _serverApi
clientApi = _clientApi

ModName = 'WorldEditPE'
ModClient = 'WorldEditPEClientSystem'
ModServer = 'WorldEditPEServerSystem'


@Mod.Binding(name = ModName, version = '0.1.0')
class WorldEditPEMod(object):
    def __init__(self):
        print '[WorldEditPE] Mod initialized.'

    @Mod.InitServer()
    def WorldEditPEServerInit(self):
        # RegisterSystem 第三个参数必须是字符串类路径（官方 API 要求）
        print '[WorldEditPE] Registering server system...'
        serverApi.RegisterSystem(ModName, ModServer, "WorldEditPE.Server.WorldEditPEServerSystem")
        print '[WorldEditPE] Server system registered.'

    @Mod.InitClient()
    def WorldEditPEClientInit(self):
        print '[WorldEditPE] Registering client system...'
        clientApi.RegisterSystem(ModName, ModClient, "WorldEditPE.Client.WorldEditPEClientSystem")
        print '[WorldEditPE] Client system registered.'

    @Mod.DestroyServer()
    def WorldEditPEServerDestroy(self):
        print '[WorldEditPE] Server destroy.'

    @Mod.DestroyClient()
    def WorldEditPEClientDestroy(self):
        print '[WorldEditPE] Client destroy.'
