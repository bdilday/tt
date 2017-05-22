#!/usr/bin/python
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
    else:
        sys.exit(DB_ERROR_MESSAGE)

    if args_dict['close_entry']:
        if args_dict['dbengine'] == 'mysql':
            sql = ('''
                select @last_row := max(id) from {table};
                update {table} set end="{time}" where id=@last_row;
            '''.format(table=args_dict['table'], time=args_dict['time']))
        elif args_dict['dbengine'] == 'sqlite':
            sql = ('''
                update {table} set end="{time}" where id=(select max(id) from {table});
            '''.format(table=args_dict['table'], time=args_dict['time']))
        else:
            sys.exit(DB_ERROR_MESSAGE)
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
                                                               end_val[0][2]))
        if args_dict['date'] and args_dict['project']:
            db.cursor().execute('insert into {table} (date, start, project) '
                                'values ("{date}", "{time}", "{proj}");'.format(
                                table=args_dict['table'], date=args_dict['date'],
                                time=args_dict['time'], proj=args_dict['project']))
        else:
            sys.exit('You\'re trying to start a new entry; you must include a date '
                     'and a project.')

    db.cursor().close()
    db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add entry to timesheet')
    parser.add_argument('-t', '--time', required=True, help='Enter time as '
                        'HH:MM using the 24-hour clock.')
    parser.add_argument('-d', '--date', required=False, help='Enter date of '
                        'entry as a string in the form, `mm/dd/yyy`')
    parser.add_argument('-p', '--project', required=False, help='Enter client '
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
