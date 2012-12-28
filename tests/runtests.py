#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import urllib
import unittest

from mock import patch

import logging
FMT = '%(created)f [%(name)s] %(levelname)s: %(message)s'
logging.basicConfig(format=FMT, level=logging.CRITICAL)
logging.basicConfig()

from config import data

test_dir = os.path.dirname(os.path.abspath(__file__))
extension_dir = os.path.join(os.path.split(test_dir)[0], 'gpodder_extensions')

def read_args():
    #read command line arguments
    parser = argparse.ArgumentParser(description='start gPodder extension script tests')
    parser.add_argument('--gpo', required=True, dest='gpo',
                        help='Path of the gPodder')
    parser.add_argument('--init', required=False, action='store_true', default=False,
                        help='initialization of the test date ' +
                             '(e.g: downloading podcasts needed for the tests')
    return parser.parse_args()


def append_python_path(gpo_path, extension):
    gpo_src_path = os.path.join(gpo_path, 'src')
    if os.path.exists(gpo_src_path):
        sys.path.append(gpo_src_path)

    if os.path.exists(extension):
        sys.path.append(extension)


def my_retrieve_resume(self, url, filename, reporthook=None, data=None):
    fp = urllib.urlopen(url)
    return fp.info(), fp.geturl()


def ins_test_podcast(core, conf):
    from gpodder import download

    with patch.object(download.DownloadURLOpener, 'retrieve_resume', my_retrieve_resume):
        podcast = core.model.load_podcast(conf['url'], create=True)

        if not podcast.pause_subscription:
            podcast.pause_subscription = True
            podcast.save()

        episode2dl = conf['episode']
        if episode2dl is not None and 'mediafile' in conf:
            episode = podcast.get_all_episodes()[episode2dl]
            if (not episode.was_downloaded(and_exists=True)):
                task = download.DownloadTask(episode, core.config)
                task.status = download.DownloadTask.QUEUED
                task.run()
                shutil.copyfile(conf['mediafile'], episode.local_filename(create=False))


def init_data(gpo_dir):
    from gpodder import core

    shutil.rmtree(gpo_dir, ignore_errors=True)

    os.environ['GPODDER_DISABLE_EXTENSIONS'] = 'yes'
    gpo_core = core.Core()

    for name, conf in data.TEST_PODCASTS.items():
        ins_test_podcast(gpo_core, conf)

    gpo_core.shutdown()
    os.environ['GPODDER_DISABLE_EXTENSIONS'] = ''


if __name__ == "__main__":
    args = read_args()
    append_python_path(args.gpo, extension_dir)

    test_dir = os.path.dirname(__file__)
    gpo_dir = os.path.join(test_dir, 'gpodder3')
    os.environ['GPODDER_HOME'] = os.path.join(gpo_dir, 'config')
    os.environ['GPODDER_DOWNLOAD_DIR'] = os.path.join(gpo_dir, 'config', 'Downloads')
    os.environ['GPODDER_EXTENSIONS'] = extension_dir

    init_data(gpo_dir)

    #import all test files
    import enqueue_in_mediaplayer_test
    #import flv2mp4_test
    import m4a_converter_test
    import normalize_audio_test
    import ogg2mp3_converter_test
    import rename_download_test
    import rm_ogg_cover_test
    import rockbox_convert2mp4_test
    import tagging_test
    import ted_subtitles_test

    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(enqueue_in_mediaplayer_test)
    suite.addTests(loader.loadTestsFromModule(m4a_converter_test))
    suite.addTests(loader.loadTestsFromModule(normalize_audio_test))
    suite.addTests(loader.loadTestsFromModule(ogg2mp3_converter_test))
    suite.addTests(loader.loadTestsFromModule(rename_download_test))
    suite.addTests(loader.loadTestsFromModule(rm_ogg_cover_test))
    suite.addTests(loader.loadTestsFromModule(rockbox_convert2mp4_test))
    suite.addTests(loader.loadTestsFromModule(tagging_test))
    suite.addTests(loader.loadTestsFromModule(ted_subtitles_test))

    # this is the last test, because it converts the flv file which is used in tests above
    # dont' work at the moment. Couldn't figure out how to get the flv file instead the mp4
    #suite.addTests(loader.loadTestsFromModule(flv2mp4_test))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
