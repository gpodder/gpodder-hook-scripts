#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'ogg2mp3_converter'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')
MIME_TYPES = ('audio/ogg',)


class TestM4AConversion(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [(data.TEST_PODCASTS['DeimHart'], True),
             (data.TEST_PODCASTS['TinFoilHat'], False)
            ]
        )
        self.episode, self.filename, self.episode1, self.filename1 = podcast_list
        self.converted_mp3 = os.path.splitext(self.filename)[0] + '.mp3'

        self.core.config.extensions.enabled = [EXTENSION_NAME]
        self.extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        if os.path.exists(self.converted_mp3):
            os.remove(self.converted_mp3)

        self.core.shutdown()

    def test_ogg2mp3(self):
        self.assertIsNotNone(self.filename)

        self.assertEqual('dh-20091121-kurz-005.ogg',
            os.path.split(self.filename)[1])

        gpodder.user_extensions.on_episode_downloaded(self.episode)

        self.assertTrue(os.path.exists(self.converted_mp3))
        self.assertTrue(os.path.getsize(self.converted_mp3)>0)

    def test_context_menu(self):
        self.assertIn(self.episode.mime_type, MIME_TYPES)
        self.assertNotIn(self.episode1.mime_type, MIME_TYPES)

        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.episode,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode1,]))
