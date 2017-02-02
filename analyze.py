import argparse
import sqlite3
import subprocess
import sys

import numpy as np
import pandas as pd
import pandas.io.sql as pdsql
import pymysql as mdb

from datetime import datetime

from tt import *


def convert_str_time(arr):
    tmp = arr.apply(lambda x: x.split(':'))
    return [np.timedelta64(int(x[0])*60 + int(x[1]), 'm') for x in tmp]


def write_plot(d, nbr):
    for i in xrange(1, nbr):
        if i==1:
            gnu = 'plot "-" u 1:2 t "{}" w lp'.format(d.columns[i])
        else:
            gnu += ', "-" u 1:2 t "{}" w lp'.format(d.columns[i])
    gnu += '\n'
    return gnu


def make_graph(d):
    plot_statement = write_plot(d, d.shape[1])

    gp = subprocess.Popen(args_dict['gnuplot'], stdin=subprocess.PIPE)
    gp.stdin.write('set terminal dumb 90 30\n')
    gp.stdin.write('set xdata time\n')
    gp.stdin.write('set timefmt "%m/%d/%Y"\n')
    gp.stdin.write(plot_statement)
    for col in xrange(1, d.shape[1]):
        for row in xrange(d.shape[0]):
            gp.stdin.write('{} {}\n'.format(d.ix[row, 0], d.ix[row, col]))
        gp.stdin.write('e\n')
    gp.stdin.flush()


def round_time(df, rd):
    print df[0]
    return [round(x/np.timedelta64(1, 'h') * rd) / rd for x in df[0]]


def run(args_dict):
    args_dict = update_args(args_dict)
    if args_dict['round']:
        args_dict['round'] = map_time(args_dict['round'])

    if len(args_dict['date'])==1:
        args_dict['date'].append(args_dict['date'][0])
    args_dict['date'] = [datetime.strptime(x, '%m/%d/%Y') for x in args_dict['date']]

    if args_dict['dbengine'] == 'mysql':
        db = mdb.connect(user='{}'.format(USERNAME), host=args_dict['host'],
                         password='{}'.format(PASSWORD), db=args_dict['db'], charset='utf8')
    elif args_dict['dbengine'] == 'sqlite':
        db = sqlite3.connect('{}.db'.format(args_dict['db']), isolation_level=None)
    else:
        sys.exit(DB_ERROR_MESSAGE)

    df = pdsql.read_sql('select * from {table}'.format(table=args_dict['table']), db)

    df.date = df.date.apply(lambda x: datetime.strptime(x, '%m/%d/%Y'))

    df = df[(df.date>=args_dict['date'][0]) & (df.date<=args_dict['date'][1])]
    if args_dict['dbengine'] == 'sqlite':
        df.start = convert_str_time(df.start)
        df.end = convert_str_time(df.end)

    vals = df.groupby(['date', 'project']).apply(lambda x: (x['end'] - x['start']).sum())

    print '*************************'
    print 'type(vals)', type(vals)
    print 'vals.dtype', vals.dtype
    print '*************************'

    if args_dict['round']:
        vals[0] = round_time(vals, args_dict['round'])

    if args_dict['analysis'] in ['all', 'graph']:
        vals_graph = vals.copy()
        if not args_dict['round']:
            vals_graph[0] = round_time(vals_graph, 15)

        graph = (vals_graph
                 .reset_index()
                 .pivot(index='date', columns='project', values=0)
                 .reset_index(level=0)
                 .fillna(0))
        graph.date = graph.date.apply(lambda x: datetime.strftime(x, '%m/%d/%Y'))

    if args_dict['analysis']=='table':
        print vals
    elif args_dict['analysis']=='graph':
        make_graph(graph)
    else:
        print vals
        make_graph(graph)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze timesheet data.')
    parser.add_argument('-d', '--date', required=True, nargs='+', type=str,
                        help='Enter date(s) for analysis; enter string(s) in the '
                        'form, `mm/dd/yyy`.')
    parser.add_argument('-a', '--analysis', required=True, choices=['table', 'graph',
                        'all'], help='Enter how data should be analyzed - `table`, '
                        '`graph`, or `all`.')
    parser.add_argument('-r', '--round', required=False, type=int, choices=[5, 10, 15, 30],
                        help='Optional; rounds times to specified minute interval.')
    parser.add_argument('--host', required=False, help='Database host; will default to '
                        'config settings.')
    parser.add_argument('--db', required=False, help='Database name; will default to '
                        'config settings.')
    parser.add_argument('--table', required=False, help='Table name; will default to '
                        'config settings.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
