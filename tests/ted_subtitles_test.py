#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'ted_subtitles'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')


class TestTedSubtitles(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [data.TEST_PODCASTS['TEDTalks']]
        )
        self.episode, self.filename = podcast_list
        self.srt_filename = os.path.splitext(self.filename)[0] + ".srt"

        # the extension sets the only_for metadata attribute, so we had to
        # set the gpodder.ui variable
        gpodder.ui.cli = True

        self.core.config.extensions.enabled = [EXTENSION_NAME]

    def tearDown(self):
        if os.path.exists(self.srt_filename):
            os.remove(self.srt_filename)

        self.core.shutdown()

    def test_subtitle(self):
        self.assertIsNotNone(self.filename)
        self.assertEqual(self.episode.title, 'TED: Matt Cutts: Try something new for 30 days - Matt Cutts (2011)')

        self.assertFalse(os.path.exists(self.srt_filename))
        cont = gpodder.user_extensions.get_extensions()[0]
        gpodder.user_extensions.on_episode_downloaded(self.episode)
        self.assertTrue(os.path.exists(self.srt_filename))

        gpodder.user_extensions.on_episode_delete(self.episode, self.filename)
        self.assertFalse(os.path.exists(self.srt_filename))
