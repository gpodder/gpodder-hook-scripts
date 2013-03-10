#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import gpodder
from gpodder import util

from config import data
import utils

EXTENSION_NAME = 'convert2avi'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')
MIME_TYPES = ['video/mp4', 'video/m4v', 'video/x-flv']


class TestM4AConversion(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['TEDTalks'],
             data.TEST_PODCASTS['TinFoilHat']
            ]
        )
        self.episode_mp4, self.filename_mp4, \
            self.episode_mp3, self.filename1_mp3 = podcast_list
        self.converted = os.path.splitext(self.filename_mp4)[0] + '.avi'
        
        self.filename_mp4_save = '%s.save' % self.filename_mp4
        shutil.copyfile(self.filename_mp4, self.filename_mp4_save)

        self.core.config.extensions.enabled = [EXTENSION_NAME]
        self.extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        if os.path.exists(self.converted):
            os.remove(self.converted)

        shutil.copyfile(self.filename_mp4_save, self.filename_mp4)
        util.rename_episode_file(self.episode_mp4, self.filename_mp4)

        self.core.shutdown()

    def test_context_menu(self):
        self.assertNotIn(self.episode_mp3.mime_type, MIME_TYPES)

        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.episode_mp4,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode_mp3,]))

    def test_mp42avi(self):
        self.assertIsNotNone(self.filename_mp4)

        self.assertEqual('MattCutts_2011U.mp4', os.path.split(self.filename_mp4)[1])

        gpodder.user_extensions.on_episode_downloaded(self.episode_mp4)

        self.assertTrue(os.path.exists(self.converted))
        self.assertTrue(os.path.getsize(self.converted)>0)
