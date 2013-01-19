# -*- coding: utf-8 -*-
# Extension script to add a context menu item for enqueueing episodes in a player
# Requirements: gPodder 3.x (or "tres" branch newer than 2011-06-08)
# (c) 2011-06-08 Thomas Perl <thp.io/about>
# Released under the same license terms as gPodder itself.
import os.path

import gpodder
from gpodder import util

import logging
logger = logging.getLogger(__name__)

_ = gpodder.gettext

__title__ = _('Add sync to context menu')
__description__ = _('Add a context menu item for syncing episodes and podcasts')
__author__ = 'Bernd Schlapsi <brot@gmx.info>'
__category__ = 'interface'
__only_for__ = 'gtk'

AMAROK = (['amarok', '--play', '--append'],
    '%s/%s' % (_('Enqueue in'), 'Amarok'))
VLC = (['vlc', '--started-from-file', '--playlist-enqueue'],
    '%s/%s' % (_('Enqueue in'), 'VLC'))


class gPodderExtension:
    def __init__(self, container):
        self.container = container
        self.gpodder = None

    def on_ui_object_available(self, name, ui_object):
        if name == 'gpodder-gtk':
            self.gpodder = ui_object

    def _get_downloaded_episodes(self, episodes):
        return [e for e in episodes if 
            e.channel.sync_to_mp3_player and e.file_exists()]
        
    def _sync_episodes(self, episodes):
        self.gpodder.on_sync_to_device_activate(None, 
            self._get_downloaded_episodes(episodes))
        
    def on_episodes_context_menu(self, episodes):
        if not self.gpodder:
            None
           
        if self.gpodder.config.device_sync.device_sync == "none" or \
            not os.path.exists(self.gpodder.config.device_sync.device_folder):
            None
            
        marked = self._get_downloaded_episodes(episodes)
        if not marked:
            return None

        return [("Sync to device", self._sync_episodes)]
