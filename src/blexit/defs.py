#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: xaos52 <xaos52@bunsenlabs.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__me__ = 'bl-exit'
__version__ = '2.0.1'

import os

display = os.environ.get('DISPLAY') is not None
"""Testing for display here because we want to be able to run the script
in a non-graphical environment as well. Without the test, importing 
gtk.Window in a non-graphical environment spits out some errors and crashes
the application."""

# Translate command-line option to method - command line only
actionToMethod = dict(
    cancel='Cancel', c='Cancel',
    logout='Logout', l='Logout',
    suspend='Suspend', s='Suspend',
    hybridsleep='HybridSleep', y='HybridSleep',
    hibernate='Hibernate', i='Hibernate',
    reboot='Reboot', b='Reboot',
    poweroff='PowerOff', p='PowerOff'
)
