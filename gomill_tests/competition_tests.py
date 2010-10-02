"""Tests for competitions.py"""

import os

from gomill import competitions

from gomill_tests import gomill_test_support

def make_tests(suite):
    suite.addTests(gomill_test_support.make_simple_tests(globals()))


def test_player_cwd(tc):
    Player_config = competitions.Player_config
    comp = competitions.Competition('test')
    comp.set_base_directory("/base")
    config = {
        'players' : {
            't1' : Player_config("test"),
            't2' : Player_config("test", cwd="/abs"),
            't3' : Player_config("test", cwd="rel/sub"),
            't4' : Player_config("test", cwd="."),
            't5' : Player_config("test", cwd="~/tmp/sub"),
            }
        }
    comp.initialise_from_control_file(config)
    tc.assertIsNone(comp.players['t1'].cwd)
    tc.assertEqual(comp.players['t2'].cwd, "/abs")
    tc.assertEqual(comp.players['t3'].cwd, "/base/rel/sub")
    tc.assertEqual(comp.players['t4'].cwd, "/base/.")
    tc.assertEqual(comp.players['t5'].cwd, os.path.expanduser("~") + "/tmp/sub")
