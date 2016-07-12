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
