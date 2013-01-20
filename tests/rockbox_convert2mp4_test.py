#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'rockbox_convert2mp4'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')


class TestRockboxMP4Convert(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['TEDTalks']]
        )
        self.episode, self.filename = podcast_list

        self.core.config.extensions.enabled = [EXTENSION_NAME]

        self.rb_extension = gpodder.user_extensions.containers[0].module

    def tearDown(self):
        converted_file = self.rb_extension._get_rockbox_filename(self.filename)
        if (os.path.exists(converted_file)):
            os.remove(converted_file)

        self.core.shutdown()

    def test_file_renaming(self):
        self.assertIsNotNone(self.filename)
        self.assertEqual(os.path.basename(self.filename), 'MattCutts_2011U.mp4')

        filename_new = self.rb_extension._get_rockbox_filename(self.filename)
        filename_test = os.path.join(os.path.dirname(self.filename), 'MattCutts_2011U.mpg')
        self.assertEqual(filename_new, filename_test)

    def test_calc_resolution(self):
        resolution = self.rb_extension._calc_resolution(512, 288, 224.0, 176.0)
        self.assertEqual(resolution, (224, 126))

        resolution = self.rb_extension._calc_resolution(1024, 768, 224.0, 176.0)
        self.assertEqual(resolution, (224, 168))

    def test_mp4convert(self):
        self.assertIsNotNone(self.filename)
        self.assertEqual(self.episode.title, 'TED: Matt Cutts: Try something new for 30 days - Matt Cutts (2011)')

        new_filename = self.rb_extension._convert_mp4(self.episode, self.filename)
        self.assertIsNotNone(new_filename)
        self.assertTrue(os.path.exists(new_filename))
