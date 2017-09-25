#!/usr/bin/python
import argparse
import sys

import pymysql as mdb
import sqlite3

from tt import *

def insert_error_message(is_ok):
    return '\n'.join(['{} '.format(s) for s in is_ok.items()])

def formulate_insert_query(args_dict):
    if args_dict['full_record'] is not None:
        return ('insert into {table} (date, start, end, project) '
                'values ("{date}", "{time_start}", "{time_end}", "{proj}");'.format(
            table=args_dict['table'], date=args_dict['date'],
            time_start=args_dict['full_record'][0],
            time_end=args_dict['full_record'][1],
            proj=args_dict['project']
        ))
    else:
        return ('insert into {table} (date, start, project) '
                'values ("{date}", "{time_start}", "{proj}");'.format(
            table=args_dict['table'], date=args_dict['date'],
            time_start=args_dict['time'],
            proj=args_dict['project']
        ))

def safe_insert(args_dict, sql_cursor, required_args=['table', 'time', 'date', 'project']):
    is_ok = {}

    for arg_name in required_args:
        is_ok[arg_name] = arg_name in args_dict and not args_dict.get(arg_name) is None

    if all(is_ok.values()):
        sql_cursor.execute(formulate_insert_query(args_dict))
    else:
        sys.exit('You\'re trying to start a new entry, but some required keys are undefined;\n' + insert_error_message(is_ok))


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

    if args_dict['full_record'] is not None:
        cur = db.cursor()
        safe_insert(args_dict, cur, required_args=['table', 'full_record', 'date', 'project'])
        cur.close()
        return True

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
        cur = db.cursor()
        safe_insert(args_dict, cur)

    db.cursor().close()
    db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add entry to timesheet')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--time', required=False, help='Enter time as '
                        'HH:MM using the 24-hour clock.')
    parser.add_argument('-d', '--date', required=False, help='Enter date of '
                        'entry as a string in the form, `mm/dd/yyy`')
    parser.add_argument('-p', '--project', required=False, help='Enter client '
                        'code to which work is to be billed.')
    parser.add_argument('-c', '--close_entry', action='store_true', help='Flag to '
                        'determine if entry should be `start` or `end` for the entry; '
                        'with flag, entry is closed.')
    group.add_argument('-r', '--full_record', nargs=2, help='Store a full record, i.e. '
                        'an open time and a close time. Must be followed by exactly two time strings.',
                        required=False, default=None)
    parser.add_argument('--host', required=False, help='Database host; will default to '
                        'config settings.')
    parser.add_argument('--db', required=False, help='Database name; will default to '
                        'config settings.')
    parser.add_argument('--table', required=False, help='Table name; will default to '
                        'config settings.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
