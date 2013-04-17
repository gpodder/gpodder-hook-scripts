#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

from mutagen import File
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

import gpodder
gpodder.images_folder = os.path.join(os.environ['GPODDER_SRC'], 'share', 'gpodder', 'images')

from config import data
import utils

EXTENSION_NAME = 'tagging'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')


class TestTagging(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['TinFoilHat'],
             data.TEST_PODCASTS['DeimHart'],
             data.TEST_PODCASTS['LogbuchNetzpolitik'],
            ]
        )
        self.episode_mp3, self.filename_mp3, \
            self.episode_ogg, self.filename_ogg, \
            self.episode_m4a, self.filename_m4a = podcast_list

        self.filename_save_mp3 = '%s.save' % self.filename_mp3
        shutil.copyfile(self.filename_mp3, self.filename_save_mp3)
        self.filename_save_ogg = '%s.save' % self.filename_ogg
        shutil.copyfile(self.filename_ogg, self.filename_save_ogg)
        self.filename_save_m4a = '%s.save' % self.filename_m4a
        shutil.copyfile(self.filename_m4a, self.filename_save_m4a)

        self.core.config.extensions.enabled = [EXTENSION_NAME]
        self.tag_extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        shutil.move(self.filename_save_mp3, self.filename_mp3)
        shutil.move(self.filename_save_ogg, self.filename_ogg)
        shutil.move(self.filename_save_m4a, self.filename_m4a)

        self.core.shutdown()

    def test_get_info(self):
        info = self.tag_extension.read_episode_info(self.episode_mp3)

        self.assertEqual('Tin Foil Hat', info['album'])
        self.assertEqual('Pilot show', info['title'])
        self.assertEqual('2010-10-23 21:00', info['pubDate'])
        self.assertEqual(self.filename_mp3, info['filename'])

    def test_write2file(self):
        info = self.tag_extension.read_episode_info(self.episode_mp3)
        self.tag_extension.write_info2file(info, self.episode_mp3)

        audio = File(info['filename'], easy=True)
        self.assertIsNotNone(audio)

        self.assertEqual(info['album'], audio.tags['album'][0])
        self.assertEqual(info['title'], audio.tags['title'][0])
        self.assertEqual(info['pubDate'], audio.tags['date'][0])
        self.assertEqual('Podcast', audio.tags['genre'][0])

    def test_removetags(self):
        self.core.config.extensions.tagging.always_remove_tags = True
        info = self.tag_extension.read_episode_info(self.episode_mp3)
        self.tag_extension.write_info2file(info, self.episode_mp3)

        audio = File(info['filename'], easy=True)
        self.assertIsNotNone(audio)
        self.assertIsNone(audio.tags)

    def test_writecover_mp3(self):
        self.core.config.extensions.tagging.auto_embed_coverart = True

        audio = MP3(self.filename_mp3, ID3=ID3)
        self.assertIsNotNone(audio)
        self.assertIsNotNone(audio.tags)
        self.assertFalse(audio.tags.has_key(u'APIC:Cover'))
        self.assertFalse(audio.tags.has_key(u'APIC'))

        info = self.tag_extension.read_episode_info(self.episode_mp3)
        self.tag_extension.write_info2file(info, self.episode_mp3)

        audio = MP3(self.filename_mp3, ID3=ID3)
        self.assertIsNotNone(audio)
        self.assertIsNotNone(audio.tags)
        self.assertTrue(audio.tags.has_key(u'APIC:Cover'))

    def test_writecover_ogg(self):
        self.core.config.extensions.tagging.auto_embed_coverart = True

        audio = File(self.filename_ogg, easy=True)
        self.assertIsNotNone(audio)
        self.assertIsNotNone(audio.tags)
        self.assertFalse(audio.tags.has_key('METADATA_BLOCK_PICTURE'))

        info = self.tag_extension.read_episode_info(self.episode_ogg)
        self.tag_extension.write_info2file(info, self.episode_ogg)

        audio = File(self.filename_ogg, easy=True)
        self.assertIsNotNone(audio)
        self.assertIsNotNone(audio.tags)
        self.assertTrue(audio.tags.has_key('METADATA_BLOCK_PICTURE'))

    def test_writecover_m4a(self):
        self.core.config.extensions.tagging.auto_embed_coverart = True

        audio = File(self.filename_m4a)
        self.assertIsNotNone(audio)
        self.assertIsNone(audio.tags)

        info = self.tag_extension.read_episode_info(self.episode_m4a)
        self.tag_extension.write_info2file(info, self.episode_m4a)

        audio = File(self.filename_m4a)
        self.assertIsNotNone(audio)
        self.assertIsNotNone(audio.tags)
        self.assertTrue(audio.tags.has_key('covr'))
