import argparse
import sys

import pymysql as mdb
import sqlite3

from tt import *


def run(args_dict):
    args_dict = update_args(args_dict)

    if args_dict['dbengine'] == 'mysql':
        db = mdb.connect(user='{}'.format(USERNAME), host=args_dict['host'],
                         password='{}'.format(PASSWORD), db=args_dict['db'],
                         charset='utf8', autocommit=True)
    elif args_dict['dbengine'] == 'sqlite':
        db = sqlite3.connect('{}.db'.format(args_dict['db']), isolation_level=None)

    if args_dict['close_entry']:
        sql = ('''
            update {table} set end={time} where id=(select max(id) from {table});
        '''.format(table=args_dict['table'], time=args_dict['time']))
        db.cursor().execute(sql)
    else:
        cur = db.cursor()
        sql = ('''
            select * from {table} where id=(select max(id) from {table});
        '''.format(table=args_dict['table']))
        cur.execute(sql)
        end_val = cur.fetchall()
        cur.close()
        if not end_val[0][3]:
            sys.exit('You\'re trying to make a new entry without closing out an '
                     'open entry. Please close this entry first:\n\n'
                     'Project: {}, Date: {}, Start: {}'.format(end_val[0][4],
                                                               end_val[0][1],
                                                               float(end_val[0][2])))
        if args_dict['date'] and args_dict['project']:
            s = ('insert into {} (date, start, project) '
                 'values (\'{}\', {}, \'{}\');'.format(
                args_dict['table'], args_dict['date'],
                args_dict['time'],args_dict['project']))
            print s
            db.cursor().execute(s)
        else:
            sys.exit('You\'re trying to start a new entry; you must include a date '
                     'and a project.')

    db.cursor().close()
    db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add entry to timesheet')
    parser.add_argument('-t', '--time', required=True, type=float, help='Enter time as '
                        'decimal/time combination. So, `8.25` represents 8:15am')
    parser.add_argument('-d', '--date', required=False, type=str, help='Enter date of '
                        'entry as a string in the form, `mm/dd/yyy`')
    parser.add_argument('-p', '--project', required=False, type=str, help='Enter client '
                        'code to which work is to be billed.')
    parser.add_argument('-c', '--close_entry', action='store_true', help='Flag to '
                        'determine if entry should be `start` or `end` for the entry; '
                        'with flag, entry is closed.')
    parser.add_argument('--host', required=False, help='Database host; will default to '
                        'config settings.')
    parser.add_argument('--db', required=False, help='Database name; will default to '
                        'config settings.')
    parser.add_argument('--table', required=False, help='Table name; will default to '
                        'config settings.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
