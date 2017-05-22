import argparse
import sys
import warnings

import pymysql as mdb
import sqlite3

from tt import *

warnings.filterwarnings('ignore')


def create_table_command_mysql():
    sql_commands = [('''
        use {db};
        create table if not exists {table} (
            id int not null auto_increment,
            date varchar(10),
            start time(0),
            end time(0),
            project varchar(8),
            primary key (id)
        );
    '''.format(db=args_dict['db'], table=args_dict['table']))]

    return sql_commands

def create_table_command_sqlite():
    sql_commands = [('''
    create table if not exists {table} (
        id integer primary key autoincrement,
        date varchar(10),
        start time(0),
        end time(0),
        project varchar(8)
    );
    '''.format(table=args_dict['table']))]

    return sql_commands

def run(args_dict):
    args_dict = update_args(args_dict)

    if args_dict['dbengine'] == 'mysql':
        db = mdb.connect(
            host='{}'.format(args_dict['host']),
            user='{}'.format(USERNAME),
            password='{}'.format(PASSWORD),
            autocommit=True
        )
        sql_commands = create_table_command_mysql()
    elif args_dict['dbengine'] == 'sqlite':
        db = sqlite3.connect('{}.db'.format(args_dict['db']), isolation_level=None)
        sql_commands = create_table_command_sqlite()
    else:
        raise ValueError, 'dbengine: {} not known'.format(args_dict['dbengine'])

    if args_dict['dbengine'] == 'mysql':
        sql_commands.insert(0, 'create database if not exists {};'.format(args_dict['db']))

    sql_commands.append(('''
        insert into {table} (date, start, end, project)
            values ('01/01/2016', '0:00', '1:00', 'test');
    '''.format(table=args_dict['table'])))

    for sql in sql_commands:
        db.cursor().execute(sql)
    db.cursor().close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a time-tracking table to '
                                     'database.')
    parser.add_argument('-d', '--db', required=True, help='Name of the database '
                        'to create.')
    parser.add_argument('-t', '--table', required=False, help='Name of the table to '
                        'create.')
    parser.add_argument('--host', required=False, help='Database host; will default to '
                        'config settings.')
    parser.add_argument('-e', '--dbengine', required=False, choices=['mysql', 'sqlite'],
                        help='Database engine; will default to config settings.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
