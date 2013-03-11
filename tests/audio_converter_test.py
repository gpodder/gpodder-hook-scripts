#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import gpodder
from gpodder import util

from config import data
import utils

EXTENSION_NAME = 'audio_converter'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')
MIME_TYPES = ('audio/x-m4a', 'audio/mp4', 'audio/mp4a-latm', 'audio/ogg', )


class TestAudioConverter(unittest.TestCase):
    """
    This test should test all possible audio conversions
    
    m4a -> mp3 .. ok
    m4a -> ogg .. ok
    ogg -> mp3 .. ok
    ogg -> ogg .. ok (no conversion)
    """
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['LogbuchNetzpolitik'],
             data.TEST_PODCASTS['TinFoilHat'],
             data.TEST_PODCASTS['DeimHart']
            ]
        )
        self.episode_m4a, self.filename_m4a, \
            self.episode_mp3, self.filename_mp4, \
            self.episode_ogg, self.filename_ogg = podcast_list
        self.converted_m4a2mp3 = os.path.splitext(self.filename_m4a)[0] + '.mp3'
        self.converted_m4a2ogg = os.path.splitext(self.filename_m4a)[0] + '.ogg'
        self.converted_ogg2mp3 = os.path.splitext(self.filename_ogg)[0] + '.mp3'
        
        self.filename_m4a_save = '%s.save' % self.filename_m4a
        shutil.copyfile(self.filename_m4a, self.filename_m4a_save)
        
        self.filename_ogg_save = '%s.save' % self.filename_ogg
        shutil.copyfile(self.filename_ogg, self.filename_ogg_save)

        self.core.config.extensions.enabled = [EXTENSION_NAME]
        self.extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        if os.path.exists(self.converted_m4a2mp3):
            os.remove(self.converted_m4a2mp3)
        if os.path.exists(self.converted_m4a2mp3):
            os.remove(self.converted_m4a2mp3)
        if os.path.exists(self.converted_ogg2mp3):
            os.remove(self.converted_ogg2mp3)
            
        shutil.copyfile(self.filename_m4a_save, self.filename_m4a)
        util.rename_episode_file(self.episode_m4a, self.filename_m4a)
        
        shutil.copyfile(self.filename_ogg_save, self.filename_ogg)
        util.rename_episode_file(self.episode_ogg, self.filename_ogg)

        self.core.shutdown()

    def test_context_menu(self):
        self.assertNotIn(self.episode_mp3.mime_type, MIME_TYPES)

        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.episode_m4a,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode_mp3,]))

    def test_m4a2mp3(self):
        self.assertIsNotNone(self.filename_m4a)

        self.assertEqual('lnp003-twitter-facebook-american-censorship-day.m4a',
            os.path.split(self.filename_m4a)[1])

        self.core.config.extensions.audio_converter.use_ogg = False
        gpodder.user_extensions.on_episode_downloaded(self.episode_m4a)

        self.assertTrue(os.path.exists(self.converted_m4a2mp3))
        self.assertTrue(os.path.getsize(self.converted_m4a2mp3)>0)

    def test_m4a2ogg(self):
        self.assertIsNotNone(self.filename_m4a)

        self.assertEqual('lnp003-twitter-facebook-american-censorship-day.m4a',
            os.path.split(self.filename_m4a)[1])
        created = os.path.getctime(self.filename_m4a)

        self.core.config.extensions.audio_converter.use_ogg = True
        gpodder.user_extensions.on_episode_downloaded(self.episode_m4a)

        self.assertTrue(os.path.exists(self.converted_m4a2ogg))
        self.assertTrue(os.path.getsize(self.converted_m4a2ogg)>0)
        self.assertTrue(os.path.getctime(self.converted_m4a2ogg)>created)

    def test_ogg2mp3(self):
        self.assertIsNotNone(self.filename_ogg)

        self.assertEqual('dh-20091121-kurz-005.ogg',
            os.path.split(self.filename_ogg)[1])

        self.core.config.extensions.audio_converter.use_ogg = False
        gpodder.user_extensions.on_episode_downloaded(self.episode_ogg)

        self.assertTrue(os.path.exists(self.converted_ogg2mp3))
        self.assertTrue(os.path.getsize(self.converted_ogg2mp3)>0)

    def test_ogg2ogg(self):
        self.assertIsNotNone(self.filename_ogg)

        self.assertEqual('dh-20091121-kurz-005.ogg',
            os.path.split(self.filename_ogg)[1])
            
        filesize = os.path.getsize(self.filename_ogg)
        created = os.path.getctime(self.filename_ogg)

        self.core.config.extensions.audio_converter.use_ogg = True
        gpodder.user_extensions.on_episode_downloaded(self.episode_ogg)

        self.assertEquals(filesize, os.path.getsize(self.filename_ogg))
        self.assertEquals(created, os.path.getctime(self.filename_ogg))

