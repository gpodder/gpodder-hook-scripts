#!/usr/bin/python
# -*- coding: utf-8 -*-
# Requirements: apt-get install python-kaa-metadata  ffmpeg python-dbus
# To use, copy it as a Python script into ~/.config/gpodder/hooks/rockbox_mp4_convert.py
# See the module "gpodder.hooks" for a description of when each hook
# gets called and what the parameters of each hook are.
#Based on Rename files after download based on the episode title
#And patch in Bug https://bugs.gpodder.org/show_bug.cgi?id=1263
# Copyright (c) 2011-04-06 Guy Sheffer <guysoft at gmail.com>
# Copyright (c) 2011-04-04 Thomas Perl <thp.io>
# Licensed under the same terms as gPodder itself
from gpodder import util
from metadata import metadata
from util import check_command, init_dbus, message

import kaa.metadata
import os
import shlex
import subprocess

import logging
logger = logging.getLogger(__name__)


DEFAULT_PARAMS = {
    "device_height": {
        "desc": u'Device height',
        "value": 176.0,
        "type": u'spinbutton',
        "sort": 1
    },
    "device_width": {
        "desc": u'Device width',
        "value": 224.0,
        "type": u'spinbutton',
        "sort": 2
    },
    "ffmpeg_options": {
        "desc": u'ffmpeg options',
        "value": u'-vcodec mpeg2video -b 500k -ab 192k -ac 2 -ar 44100 -acodec libmp3lame',
        "type": u'textitem',
        "sort": 3
    }
}

ROCKBOX_EXTENTION = "mpg"
EXTENTIONS_TO_CONVERT = ['.mp4',"." + ROCKBOX_EXTENTION]
FFMPEG_CMD = 'ffmpeg -y -i "%(from)s" -s %(width)sx%(height)s %(options)s "%(to)s"'


class gPodderHooks(object):
    notify_id = 0
    notify_msg = []

    def __init__(self, params=DEFAULT_PARAMS):
        logger.info("RockBox mp4 converter hook loaded")
        self.params = params
        self.notify_interface = init_dbus()

        check_command(FFMPEG_CMD)

    def on_episode_downloaded(self, episode):
        current_filename = episode.local_filename(False)
        converted_filename = self._convert_mp4(current_filename, self.params)

        if converted_filename is not None:
            episode.filename = os.path.basename(converted_filename)
            episode.save()
            os.remove(current_filename)
            logger.info('Conversion for %s was successfully' % current_filename)
        else:
            logger.info('Conversion for %s had errors' % current_filename)

    def _get_rockbox_filename(self, origin_filename):
        if not os.path.exists(origin_filename):
            return None

        dirname = os.path.dirname(origin_filename)
        filename = os.path.basename(origin_filename)
        basename, ext = os.path.splitext(filename)

        if ext not in EXTENTIONS_TO_CONVERT:
            return None

        if filename.endswith(ROCKBOX_EXTENTION):
            new_filename = "%s-convert.%s" % (basename, ROCKBOX_EXTENTION)
        else:
            new_filename = "%s.%s" % (basename, ROCKBOX_EXTENTION)
        return os.path.join(dirname, new_filename)


    def _calc_resolution(self, video_width, video_height, device_width, device_height):
        if video_height is None:
            return None
            
        width_ratio = device_width / video_width
        height_ratio = device_height / video_height
                    
        dest_width = device_width
        dest_height = width_ratio * video_height
                    
        if dest_height > device_height:
            dest_width = height_ratio * video_width
            dest_height = device_height

        return (int(round(dest_width)), round(int(dest_height)))


    def _convert_mp4(self, from_file, params):
        """Convert MP4 file to rockbox mpg file"""
        # generate new filename and check if the file already exists
        to_file = self._get_rockbox_filename(from_file)
        if os.path.isfile(to_file):
            return to_file

        logger.info("Converting: %s", from_file)

        # calculationg the new screen resolution
        info = kaa.metadata.parse(from_file)
        resolution = self._calc_resolution(
            info.video[0].width,
            info.video[0].height,
            params['device_width']['value'],
            params['device_height']['value']
        )
        if resolution is None:
            logger.error("Error calculating the new screen resolution") 
            return None
            
        # Running conversion command (ffmpeg)
        self.notify_msg.append("Converting '%s'" % from_file)
        self.notify_id = message(self.notify_interface, metadata['name'], 
            '\n'.join(self.notify_msg), self.notify_id
        )
        convert_command = FFMPEG_CMD % {
            'from': from_file,
            'to': to_file,
            'width': str(resolution[0]),
            'height': str(resolution[1]),
            'options': params['ffmpeg_options']['value']
        }

        # Prior to Python 2.7.3, this module (shlex) did not support Unicode input.
        if isinstance(convert_command, unicode):
            convert_command = convert_command.encode('ascii', 'ignore')

        process = subprocess.Popen(shlex.split(convert_command),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logger.error(stderr)
            return None

        return to_file
