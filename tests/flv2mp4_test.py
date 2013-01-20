#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'flv2mp4'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')


class TestFlv2Mp4(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['drovics'],
             data.TEST_PODCASTS['TinFoilHat']
            ]
        )
        self.episode, self.filename, self.episode1, self.filename1 = podcast_list
        # the real mime-type is only known when downloading the file
        self.episode.mime_type = 'video/x-flv'
        self.converted_file = os.path.splitext(self.filename)[0] + '.mp4'

        self.core.config.extensions.enabled = [EXTENSION_NAME]

    def tearDown(self):
        if os.path.exists(self.converted_file):
            os.remove(self.converted_file)

        self.core.shutdown()

    def test_mp4convert(self):
        self.assertIsNotNone(self.filename)
        self.assertTrue(os.path.exists(self.filename))
        self.assertTrue(gpodder.youtube.is_video_link(self.episode.url))

        gpodder.user_extensions.on_episode_downloaded(self.episode)

        self.assertTrue(os.path.exists(self.converted_file))
        self.assertTrue(os.path.getsize(self.converted_file)>0)

    def test_context_menu(self):
        self.assertEqual(self.episode.mime_type, 'video/x-flv')
        self.assertNotEqual(self.episode1.mime_type, 'video/x-flv')

        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.episode,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode1,]))
