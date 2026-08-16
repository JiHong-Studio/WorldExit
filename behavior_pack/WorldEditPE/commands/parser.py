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
Command parser.
In Netease Minecraft PE, ALL messages starting with / are intercepted by the
vanilla command system as native commands. Therefore // NEVER reaches ServerChatEvent.
We use = as the command prefix instead (e.g. =help, =pos1, =set stone).
"""

from WorldEditPE.utils.messages import Notifier

# 显示用的前缀（在帮助和消息中显示）
DISPLAY_PREFIX = '='
# 实际支持的前缀（解析时接受多种）
SUPPORTED_PREFIXES = ('=', '//')

# Command registry: {name: handler_function}
_command_registry = {}


def register_command(name, handler):
    """Register a command handler."""
    _command_registry[name] = handler
    print "[WorldEditPE] Registered command: %s%s" % (DISPLAY_PREFIX, name)


def get_command(name):
    """Look up a command handler."""
    return _command_registry.get(name)


def get_all_commands():
    """Return all registered command names."""
    return _command_registry.keys()


def get_display_prefix():
    """Return the display prefix for help text."""
    return DISPLAY_PREFIX


def parse_and_execute(player_id, message):
    """
    Parse a chat message and dispatch to the registered handler.
    Returns True if the message was handled (should cancel original chat).
    """
    msg = message.strip()

    print "[WorldEditPE] parse_and_execute: player=%s msg='%s'" % (player_id, msg)

    # 检查支持的任意前缀
    prefix_used = None
    for prefix in SUPPORTED_PREFIXES:
        if msg.startswith(prefix):
            prefix_used = prefix
            break

    if prefix_used is None:
        print "[WorldEditPE] Message doesn't start with any supported prefix"
        return False

    # Strip the prefix
    msg = msg[len(prefix_used):].strip()
    if not msg:
        print "[WorldEditPE] Empty command after prefix"
        return False

    # Split into command name and arguments
    parts = msg.split()
    cmd_name = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    print "[WorldEditPE] Parsed command: cmd=%s args=%s" % (cmd_name, args)

    handler = get_command(cmd_name)
    if handler is None:
        notifier = Notifier(player_id)
        notifier.error('Unknown command: ' + DISPLAY_PREFIX + cmd_name)
        notifier.info('Type ' + DISPLAY_PREFIX + 'help for a list of commands.')
        print "[WorldEditPE] Unknown command: %s" % cmd_name
        return True

    try:
        print "[WorldEditPE] Executing command: %s for player %s" % (cmd_name, player_id)
        handler(player_id, args)
        print "[WorldEditPE] Command %s executed successfully" % cmd_name
    except Exception as e:
        notifier = Notifier(player_id)
        notifier.error('Error executing %s%s: %s' % (DISPLAY_PREFIX, cmd_name, str(e)))
        import traceback
        traceback.print_exc()
        print "[WorldEditPE] Command %s error: %s" % (cmd_name, str(e))

    return True
