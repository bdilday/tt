import ConfigParser
import os

USERNAME = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASS')
PATH = os.getenv('TT_PATH')

DB_ERROR_MESSAGE = ('''You\'re trying to use a DB engine '''
                    '''that\'s not currently supported. '''
                    '''Try again, specifying `mysql` or `sqlite`.''')

time_map = {
    5: 20,
    10: 10,
    15: 4,
    30: 2,
}


def update_args(args):
    cfg = ConfigParser.ConfigParser()
    cfg.read('{}/config.cfg'.format(PATH))
    for field, field_value in cfg.items('database'):
        if (field not in args) or (args[field] is None):
            args[field] = field_value

    return args

def map_time(arg):
    return time_map[arg]
