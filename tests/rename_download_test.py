#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'rename_download'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')


class TestRenameDownloads(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['TinFoilHat']]
        )
        self.episode, self.filename = podcast_list

        self.core.config.extensions.enabled = [EXTENSION_NAME]

    def tearDown(self):
        self.core.shutdown()

    def test_rename_file(self):
        filename_test = os.path.abspath(os.path.join(
            os.environ['GPODDER_DOWNLOAD_DIR'], 'Tin Foil Hat',
            'Pilot show.mp3'))
            
        module = gpodder.user_extensions.containers[0].module
        filename_new = module.make_filename(self.filename, self.episode.title)
        filename_new = os.path.abspath(filename_new)

        self.assertEqual(filename_test, filename_new)
        self.assertNotEqual(self.filename, filename_new)

