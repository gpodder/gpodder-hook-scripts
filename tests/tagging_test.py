#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from mutagen import File

import gpodder

from config import data
import utils

EXTENSION_NAME = 'tagging'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')


class TestTagging(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['TinFoilHat']]
        )
        self.episode, self.filename = podcast_list
        self.filename_save = '%s.save' % self.filename
        shutil.copyfile(self.filename, self.filename_save)

        self.core.config.extensions.enabled = [EXTENSION_NAME]

        self.tag_extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        shutil.move(self.filename_save, self.filename)

        self.core.shutdown()

    def test_get_info(self):
        info = self.tag_extension.read_episode_info(self.episode)

        self.assertEqual('Tin Foil Hat', info['album'])
        self.assertEqual('Pilot show', info['title'])
        self.assertEqual('2010-10-23 21:00', info['pubDate'])
        self.assertEqual(self.filename, info['filename'])

    def test_write2file(self):
        info = self.tag_extension.read_episode_info(self.episode)
        self.tag_extension.write_info2file(info)

        audio = File(info['filename'], easy=True)
        self.assertIsNotNone(audio)

        self.assertEqual(info['album'], audio.tags['album'][0])
        self.assertEqual(info['title'], audio.tags['title'][0])
        self.assertEqual(info['pubDate'], audio.tags['date'][0])
        self.assertEqual('Podcast', audio.tags['genre'][0])
