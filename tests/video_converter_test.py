#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import gpodder
from gpodder import util

from config import data
import utils

EXTENSION_NAME = 'video_converter'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')
MIME_TYPES = ('video/mp4', 'video/m4v', 'video/x-flv', )


class TestVideoConverter(unittest.TestCase):
    """
    This test should test all possible video conversions, but at the moment
    I couldn't test a flv file as source format, because I couldn't find a
    flv video podcast.
    YouTube is impossible to use for a test because of gPodders implementation

    Also I couldn't find a video podcast with real m4v format. The mime-type
    of the founded podcast is always video/mp4.
    I'm not sure what's the difference between mp4 and m4v?

    mp4 -> avi .. ok
    mp4 -> mp4 .. ok
    m4v -> avi .. missing
    m4v -> mp4 .. missing
    flv -> avi .. missing
    flv -> mp4 .. missing
    mp3 -> mp4 .. ok (no conversion)
    """
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['TEDTalks'],
             data.TEST_PODCASTS['TinFoilHat']
            ]
        )
        self.episode_mp4, self.filename_mp4, \
            self.episode_mp3, self.filename_mp3 = podcast_list
        self.converted_avi = os.path.splitext(self.filename_mp4)[0] + '.avi'

        self.filename_mp4_save = '%s.save' % self.filename_mp4
        shutil.copyfile(self.filename_mp4, self.filename_mp4_save)

        self.core.config.extensions.enabled = [EXTENSION_NAME]
        self.extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        if os.path.exists(self.converted_avi):
            os.remove(self.converted_avi)

        shutil.copyfile(self.filename_mp4_save, self.filename_mp4)
        util.rename_episode_file(self.episode_mp4, self.filename_mp4)

        self.core.shutdown()

    def test_context_menu2avi(self):
        self.assertNotIn(self.episode_mp3.mime_type, MIME_TYPES)

        self.core.config.extensions.video_converter.output_format = 'avi'
        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.episode_mp4,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode_mp3,]))

    def test_context_menu2mp4(self):
        self.assertNotIn(self.episode_mp3.mime_type, MIME_TYPES)

        self.core.config.extensions.video_converter.output_format = 'mp4'
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode_mp4,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode_mp3,]))

    def test_mp42avi(self):
        self.assertIsNotNone(self.filename_mp4)

        self.assertEqual('MattCutts_2011U.mp4', os.path.split(self.filename_mp4)[1])

        self.core.config.extensions.video_converter.output_format = 'avi'
        gpodder.user_extensions.on_episode_downloaded(self.episode_mp4)

        self.assertTrue('MattCutts_2011U.avi', self.converted_avi)
        self.assertTrue(os.path.exists(self.converted_avi))
        self.assertTrue(os.path.getsize(self.converted_avi)>0)

    def test_mp42mp4(self):
        self.assertIsNotNone(self.filename_mp4)

        self.assertEqual('MattCutts_2011U.mp4', os.path.split(self.filename_mp4)[1])
        
        filesize = os.path.getsize(self.filename_mp4)
        created = os.path.getctime(self.filename_mp4)

        self.core.config.extensions.video_converter.output_format = 'mp4'
        gpodder.user_extensions.on_episode_downloaded(self.episode_mp4)

        self.assertEquals(filesize, os.path.getsize(self.filename_mp4))
        self.assertEquals(created, os.path.getctime(self.filename_mp4))

    def test_mp32mp4(self):
        self.assertIsNotNone(self.filename_mp3)

        filename = os.path.split(self.filename_mp3)[1]
        self.assertEqual('TFH-001.mp3', filename)

        self.core.config.extensions.video_converter.output_format = 'mp4'
        gpodder.user_extensions.on_episode_downloaded(self.episode_mp3)

        self.assertFalse(os.path.exists(os.path.splitext(filename)[0] + '.mp4'))
