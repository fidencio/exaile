# Copyright (C) 2009 Aren Olson
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#
# The developers of the Exaile media player hereby grant permission
# for non-GPL compatible GStreamer and Exaile plugins to be used and
# distributed together with GStreamer and Exaile. This permission is
# above and beyond the permissions granted by the GPL license by which
# Exaile is covered. If you modify this code, you may extend this
# exception to your version of the code, but you are not obligated to
# do so. If you do not wish to do so, delete this exception statement
# from your version.

GNOME_MMKEYS = None
EXAILE = None

from xl import common, event
import dbus, logging, traceback
logger = logging.getLogger(__name__)

def callback(key):
    global EXAILE
    if key in ('Play', 'PlayPause', 'Pause'):
        if EXAILE.player.is_playing() or EXAILE.player.is_paused():
            EXAILE.player.toggle_pause()
        elif key != "Pause":
            EXAILE.queue.play()
        else:
            pass
    elif key == 'Stop':
        EXAILE.player.stop()
    elif key == 'Previous':
        EXAILE.queue.prev()
    elif key == 'Next':
        EXAILE.queue.next()

def enable(exaile):
    if exaile.loading:
        event.add_callback(_enable, "player_loaded")
    else:
        _enable(None, exaile, None)

def _enable(eventname, exaile, nothing):
    global GNOME_MMKEYS, EXAILE
    EXAILE = exaile
    def on_gnome_mmkey(app, key):
        if app == "Exaile":
            callback(key)
    try:
        bus = dbus.SessionBus()
        try:
            # new method (for gnome 2.22.x)
            obj = bus.get_object('org.gnome.SettingsDaemon',
                '/org/gnome/SettingsDaemon/MediaKeys')
            GNOME_MMKEYS = gnome = dbus.Interface(obj,
                'org.gnome.SettingsDaemon.MediaKeys')
            gnome.GrabMediaPlayerKeys("Exaile", 0)
            gnome.connect_to_signal('MediaPlayerKeyPressed', on_gnome_mmkey)
            return True
        except:
            traceback.print_exc()
            # old method
            obj = bus.get_object('org.gnome.SettingsDaemon',
                '/org/gnome/SettingsDaemon')
            GNOME_MMKEYS = gnome = dbus.Interface(obj,
                'org.gnome.SettingsDaemon')
            gnome.GrabMediaPlayerKeys("Exaile", 0)
            gnome.connect_to_signal('MediaPlayerKeyPressed', on_gnome_mmkey)
            return True
    except:
        disable(exaile) #disconnect if we failed to load completely
        GNOME_MMKEYS = None
        common.log_exception(logger)
        return False

def disable(exaile):
    global GNOME_MMKEYS
    if GNOME_MMKEYS:
        try:
            GNOME_MMKEYS.ReleaseMediaPlayerKeys("Exaile")
        except:
            common.log_exception()
            GNOME_MMKEYS = None
            return False
    GNOME_MMKEYS = None
    return True
