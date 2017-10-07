from configparser import ConfigParser
import ast
from os.path import join

track_vehicles = {'test_straight': 3.7,
                  'test_narrow': 10.0,
                  'test_join': 3.9,
                  'test_curves': 3.7,
                  'test_roadwork': 4.6}

track_nicks = {'test_straight': 'straight',
               'test_narrow': 'narrow',
               'test_join': 'join',
               'test_curves': 'curves',
               'test_roadwork': 'roadworks'}

# change these to evaluate different networks and tracks
NET_NAME = 'fcn_iou_deepres'
TRACK_NAME = 'test_curves'

TRACK_NICK = track_nicks.get(TRACK_NAME, TRACK_NAME)
AVG_VEHICLES = track_vehicles.get(TRACK_NAME, -1.0)
HISTO_NAME = NET_NAME + '_' + TRACK_NAME
#HISTO_NAME = 'TESTING'

LOG_DIR = join('log_data', NET_NAME)
EVAL_DIR = join('eval_data', TRACK_NAME)
#CONFIG_PATH = join(LOG_DIR, 'config.ini')  # use this for evaluation
CONFIG_PATH = 'config.ini'  # use this for training and simulation

CONFIG = ConfigParser()


def initialize(path=CONFIG_PATH):
    CONFIG.read(path)


def parse_param(param):
    return ast.literal_eval(param)
