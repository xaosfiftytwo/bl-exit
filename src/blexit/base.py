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

from __future__ import print_function

import os
import sys
import argparse

from defs import display

class BlexitBase(object):

    def __init__(self):
        self.dbus_iface = None

    def setup_dbus_connection(self):
        try:
            bus = dbus.SystemBus()
            dbus_object = bus.get_object('org.freedesktop.login1',
                                         '/org/freedesktop/login1')
            self.dbus_iface = dbus.Interface(dbus_object,
                                             'org.freedesktop.login1.Manager')
        except bus.DBusException as e:
            self.on_error(str(e))

    def can_do_action(self, action):
        # There is no 'CanLogout' method
        if action == "Logout":
            return "yes"
        actionMethod = "Can{}".format(action)
        response = self.send_dbus(actionMethod)
        return str(response)

    def do_action(self, action):
        print("do_action: {}".format(action), file=sys.stderr)
        self.send_dbus(action)

    def send_dbus(self, method):
        try:
            if self.dbus_iface is None:
                self.setup_dbus_connection()
            if method[:3] == "Can":
                command = "self.dbus_iface.{}()".format(method)
            else:
                command = "self.dbus_iface.{}(['True'])".format(method)
            response = eval(command)
            return str(response)
        except dbus.DBusException as e:
            self.on_error(str(e))

    def on_error(self, string):
        print ("{}".format(string), file=sys.stderr)
        sys.exit(1)

    def openbox_exit(self):
        subprocess.check_output(["openbox", "--exit"])

    def logout(self):
        try:
            self.openbox_exit()
        except subprocess.CalledProcessError as e:
            self.on_error(e.output)

    def action_from_command_line(self, action):
        try:
            self.do_action(action)
        except (subprocess.CalledProcessError, CanDoItError, KeyError) as e:
            self.on_error(str(e))

    def main(self):
        opts = get_options()
        if opts.logout:
            self.logout()
        else:
            if opts.suspend:
                action = "suspend"
            elif opts.hibernate:
                action = "hibernate"
            elif opts.hybridsleep:
                action = "hybridsleep"
            elif opts.reboot:
                action = "reboot"
            elif opts.poweroff:
                action = "poweroff"
            self.setup_dbus_connection()
            self.action_from_command_line(actionToMethod[action])


def get_options():
    result = None
    parser = argparse.ArgumentParser(description="Bunsenlabs exit")
    if display:
        parser.add_argument("-l", "--logout", help="Log out",
                            action="store_true")
    parser.add_argument("-s", "--suspend", help="Suspend",
                        action="store_true")
    parser.add_argument("-i", "--hibernate", help="Hibernate",
                        action="store_true")
    parser.add_argument("-y", "--hybridsleep", help="Hybrid sleep",
                        action="store_true")
    parser.add_argument("-b", "--reboot", help="Reboot",
                        action="store_true")
    parser.add_argument("-p", "--poweroff", help="Power off",
                        action="store_true")
    parser.parse_args(sys.argv[1:])
    """No check if more than one option was specified. Take the first option and
    discard the other"""
    result = parser.parse_args()
    return result


def main():
    '''
    The script works both in a graphical and a non-graphical environment.

    In a graphical environment, the BlExitWindow instance is only shown when
    the script is launched without arguments. The user selects the action she
    wants by clicking the right button.

    WHen  the script is launched In a graphical environment the requested
    action should be one of the accepted arguments and the action is executed
    without asking for confirmation - as if the script was launched from the
    command line.

    In a non-graphical environment, one of the accepted actions must be
    specified as an argument.
    '''
    
    if display and len(sys.argv[1:]) == 0:
        from derived import BlexitWindow
        blexit = BlexitWindow()
    else:
        blexit = BlexitBase()
    return blexit.main()
            
