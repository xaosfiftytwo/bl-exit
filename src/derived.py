# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import gtk
import getpass
import pygtk
pygtk.require('2.0')
import ConfigParser

from base import BlexitBase
from defs import actionToMethod


class CanDoItError(Exception):
    pass


class BlexitWindow(BlexitBase, gtk.Window):
    """A dialog offering the user to log out, suspend, reboot or shut down.
    """

    def __init__(self):
        BlexitBase.__init__(self)
        gtk.Window.__init__(self)

    def configure(self):
        """Determine config directory: first try the environment variable
        XDG_CONFIG_HOME according to XDG specification and as a fallback
        use ~/.config/bl-exit. Use /etc/bl-exit/bl-exitrc as a last
        resort."""
        config_dirs = []
        xdg_config_dir = os.getenv('XDG_CONFIG_HOME')
        if xdg_config_dir:
            config_dirs.append(xdg_config_dir)
        user_config_dir = os.path.expanduser('~/.config')
        try:
            if not (xdg_config_dir and os.path.samefile(user_config_dir,
                                                        xdg_config_dir)):
                config_dirs.append(user_config_dir)
        except OSError as e:
            print ("{}: {}".format(__me__, str(e)), file=sys.stderr)
            pass
        config_dirs.append('/etc')
        config_file = None
        for config_dir in config_dirs:
            config_dir = config_dir + '/bl-exit'
            if os.path.isdir(config_dir):
                maybe_config_file = config_dir + '/bl-exitrc'
                if os.path.isfile(maybe_config_file):
                    config_file = maybe_config_file
                    break

        if config_file:
            try:
                self.config = ConfigParser.RawConfigParser()
                self.config.read(config_file)
            except ConfigParser.ParsingError as e:
                print ("{}: {}".format(__me__, str(e)), file=sys.stderr)
                self.config = None
                sys.exit(1)
        else:
            self.config = None

    def construct_ui(self):
        self.set_title("Log out " + getpass.getuser()
                       + "? Choose an option:")
        self.set_border_width(5)
        self.set_size_request(-1, 80)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.stick
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("delete_event", gtk.main_quit)
        windowicon = self.render_icon(gtk.STOCK_QUIT, gtk.ICON_SIZE_DIALOG)
        self.set_icon(windowicon)

        # Cancel key (Escape)
        accelgroup = gtk.AccelGroup()
        key, mod = gtk.accelerator_parse('Escape')
        accelgroup.connect_group(key, mod, gtk.ACCEL_VISIBLE,
                                 gtk.main_quit)
        self.add_accel_group(accelgroup)
        self.button_box = gtk.HBox()
        self.build_button_visibility_array()
        for button in self.bva:
            (action, label, actionfunc, method, show, onError) = button
            if not show == 0:
                self.add_button(show, actionfunc, label=label)
        self.status = gtk.Label()
        label_box = gtk.HBox()
        label_box.pack_start(self.status)

        vbox = gtk.VBox()
        vbox.pack_start(self.button_box)
        vbox.pack_start(label_box)

        self.add(vbox)
        self.show_all()

    def destroy(self):
        self.hide_all()
        gtk.main_quit()

    def build_button_visibility_array(self):
        """Determine button visibily using bl-exit configuration file.
        Build self.bva, an array of tuples, one entry per button,
        containing (action, label, actionfunction, actionMethod, show,
        onerror)
        """
        self.bva = []
        bva = [
            ('cancel', '_Cancel', self.cancel_action),
            ('logout', '_Log out', self.logout_action),
            ('suspend', '_Suspend', self.suspend_action),
            ('hibernate', 'H_ibernate', self.hibernate_action),
            ('hybridsleep', 'H_ybrid sleep', self.hybridsleep_action),
            ('reboot', 'Re_boot', self.reboot_action),
            ('poweroff', '_Power off', self.shutdown_action)
        ]
        show_values = dict(never=0, always=1, maybe=2)
        """Values that the 'show' keyword can take in the configuration
        file."""
        onerror_values = dict(novisual=0, visual=1)
        """Values that the 'onerror' keyword can take in the configuration
        file."""
        # Per button default settings
        per_button_defaults = dict(
            cancel='never',
            logout='always',
            suspend='always',
            hibernate='never',
            hybridsleep='never',
            reboot='always',
            poweroff='always'
        )
        for (action, label, actionfunction) in bva:
            # Defaults.
            show = show_values[per_button_defaults[action]]
            onError = onerror_values['novisual']
            if self.config:
                for section in ['default', action]:
                    try:
                        try:
                            getshow = self.config.get(section, 'show')
                            if getshow in show_values:
                                show = show_values[getshow]
                                if show == 2:
                                    candoit = self.can_do_action(
                                        actionToMethod[action])
                                    if not candoit == 'yes':
                                        show = 3
                        except ConfigParser.NoOptionError as e:
                            pass

                        try:
                            getonerror = self.config.get(section,
                                                         'onerror')
                            if getonerror in onerror_values:
                                onError = onerror_values[getonerror]
                        except ConfigParser.NoOptionError as e:
                            pass
                    except ConfigParser.NoSectionError as e:
                        pass

            self.bva.append(tuple([action, label, actionfunction,
                                   actionToMethod[action], show,
                                   onError]))

    def main(self):
        self.configure()
        self.construct_ui()
        gtk.main()

    def add_button(self, show, action, label=None, stock=None):
        if stock is not None:
            button = gtk.Button(stock=stock)
        else:
            button = gtk.Button(label=label)
        button.set_size_request(100, 40)
        if show == 3:
            button.set_sensitive(False)
        button.set_border_width(4)
        button.connect("clicked", action)
        self.button_box.pack_start(button)

    def disable_buttons(self):
        self.button_box.foreach(lambda button:
                                button.set_sensitive(False))

    def cancel_action(self, button):
        self.disable_buttons()
        gtk.main_quit()

    def get_onerror(self):
        for item in self.bva:
            (action, label, actionfunction, actionMethod, show,
             onerror) = item
            if action == self.selected_action:
                return onerror

    def on_error(self, e):
        onerror = self.get_onerror()
        if onerror == 0:
            print ("{}: {}".format(__me__, str(e)), file=sys.stderr)
            sys.exit(1)
        else:
            emDialog = gtk.MessageDialog(parent=None, flags=0,
                                         type=gtk.MESSAGE_INFO,
                                         buttons=gtk.BUTTONS_OK,
                                         message_format=None)
            if emDialog:
                emDialog.set_markup("{}".format(e))
                emDialog.run()

    def cancel_action(self, button):
        self.destroy()

    def logout_action(self, button):
        self.disable_buttons()
        self.selected_action = 'logout'
        self.status.set_label("Exiting Openbox, please standby...")
        self.openbox_exit()
        self.destroy()

    def suspend_action(self, button):
        self.disable_buttons()
        self.selected_action = 'suspend'
        self.status.set_label("Suspending, please standby...")
        self.do_action("Suspend")
        self.destroy()

    def hibernate_action(self, button):
        self.disable_buttons()
        self.selected_action = 'hibernate'
        self.status.set_label("Hibernating, please standby...")
        self.do_action("Hibernate")
        self.destroy()

    def hybridsleep_action(self, button):
        self.disable_buttons()
        self.selected_action = 'hybridsleep'
        self.status.set_label("Hibernating + Sleeping, please standby...")
        self.do_action("HybridSleep")
        self.destroy()

    def reboot_action(self, button):
        self.disable_buttons()
        self.selected_action = 'reboot'
        self.status.set_label("Rebooting, please standby...")
        self.do_action("Reboot")
        self.destroy()

    def shutdown_action(self, button):
        self.disable_buttons()
        self.selected_action = 'poweroff'
        self.status.set_label("Shutting down, please standby...")
        self.do_action("PowerOff")
        self.destroy()

