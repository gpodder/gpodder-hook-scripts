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


class TestOgg2Mp3(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['DeimHart'],
             data.TEST_PODCASTS['TinFoilHat']
            ]
        )
        self.ogg_episode, self.ogg_filename, self.mp3_episode, self.mp3_filename = podcast_list
        self.converted_mp3 = os.path.splitext(self.ogg_filename)[0] + '.mp3'
        
        self.save_filename = self.ogg_episode.download_filename
        self.save_filesize = self.ogg_episode.file_size
        self.save_mimetype = self.ogg_episode.mime_type

        self.core.config.extensions.enabled = [EXTENSION_NAME]
        self.extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        if os.path.exists(self.converted_mp3):
            os.remove(self.converted_mp3)
            
        original_file = data.TEST_PODCASTS['DeimHart']['mediafile']
        if not os.path.exists(self.ogg_filename):
            shutil.copyfile(original_file, self.ogg_filename)
            self.ogg_episode.download_filename = self.save_filename
            self.ogg_episode.file_size = self.save_filesize
            self.ogg_episode.mime_type = self.save_mimetype
            self.ogg_episode.save()
            self.ogg_episode.db.commit()        

        self.core.shutdown()

    def test_ogg2mp3(self):
        self.assertIsNotNone(self.ogg_filename)

        self.assertEqual('dh-20091121-kurz-005.ogg',
            os.path.split(self.ogg_filename)[1])

        gpodder.user_extensions.on_episode_downloaded(self.ogg_episode)

        self.assertTrue(os.path.exists(self.converted_mp3))
        self.assertTrue(os.path.getsize(self.converted_mp3)>0)

    def test_context_menu(self):
        self.assertIn(self.ogg_episode.mime_type, MIME_TYPES)
        self.assertNotIn(self.mp3_episode.mime_type, MIME_TYPES)

        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.ogg_episode,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.mp3_episode,]))
