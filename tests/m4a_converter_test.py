#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'm4a_converter'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')
MIME_TYPES = ['audio/x-m4a', 'audio/mp4']


class TestM4AConversion(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['LogbuchNetzpolitik'],
             data.TEST_PODCASTS['TinFoilHat']
            ]
        )
        self.episode, self.filename, self.episode1, self.filename1 = podcast_list
        self.converted_mp3 = os.path.splitext(self.filename)[0] + '.mp3'
        self.converted_ogg = os.path.splitext(self.filename)[0] + '.ogg'

        # workaround for wrong mimetype from the metaebene server
        # I already contacted Tim Pritlove to correct the wrong mimetype
        if os.path.splitext(self.filename)[1] == '.m4a' and self.episode.mime_type != 'audio/mp4':
            self.episode.mime_type = 'audio/mp4'
        ## end of workaround

        self.core.config.extensions.enabled = [EXTENSION_NAME]

        self.extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        if os.path.exists(self.converted_mp3):
            os.remove(self.converted_mp3)
        if os.path.exists(self.converted_ogg):
            os.remove(self.converted_ogg)

        self.core.shutdown()

    def test_context_menu(self):
        self.assertIn(self.episode.mime_type, MIME_TYPES)
        self.assertNotIn(self.episode1.mime_type, MIME_TYPES)

        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.episode,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode1,]))

    def test_m4a2mp3(self):
        self.assertIsNotNone(self.filename)

        self.assertEqual('lnp003-twitter-facebook-american-censorship-day.m4a',
            os.path.split(self.filename)[1])

        self.core.config.extensions.m4a_converter.use_ogg = False
        gpodder.user_extensions.on_episode_downloaded(self.episode)

        self.assertTrue(os.path.exists(self.converted_mp3))
        self.assertTrue(os.path.getsize(self.converted_mp3)>0)

    # at the moment only one conversion tests works because the conversion
    # changes the filename and the mime-type
    def dontrun_test_m4a2ogg(self):
        self.assertIsNotNone(self.filename)

        self.assertEqual('lnp003-twitter-facebook-american-censorship-day.m4a',
            os.path.split(self.filename)[1])

        self.core.config.extensions.m4a_converter.use_ogg = True
        gpodder.user_extensions.on_episode_downloaded(self.episode)

        self.assertTrue(os.path.exists(self.converted_ogg))
        self.assertTrue(os.path.getsize(self.converted_ogg)>0)

