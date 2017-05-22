import argparse
import sqlite3
import sys
import warnings

import pandas.io.sql as pdsql
import pymysql as mdb

from tt import *

warnings.filterwarnings('ignore')


def table_check(args_dict, db, exists=True):
    check_table = db.cursor()
    if args_dict['dbengine'] == 'mysql':
        check_table.execute('''
            select count(*) from information_schema.tables where
                table_name = "{table}";
        '''.format(table=args_dict['proj_table']))
    else:
        check_table.execute('''
            select count(*) from sqlite_master where type = 'table' and
                name = "{table}";
        '''.format(table=args_dict['proj_table']))
    if exists:
        if check_table.fetchone()[0] == 1:
            check_table.close()
            pass
        else:
            sys.exit('STOP! The table {} does not exist.'
                     .format(args_dict['proj_table']))
    else:
        if check_table.fetchone()[0] != 1:
            check_table.close()
            pass
        else:
            sys.exit('STOP! The table {} already exists.'
                     .format(args_dict['proj_table']))


def entry_check(args_dict, db):
    check_entry = db.cursor()
    check_entry.execute('''
        select exists(select * from {} where (
            project_code="{}" or project_bill_nbr="{}"));
    '''.format(args_dict['proj_table'], args_dict['add'][1], args_dict['add'][2]))
    if check_entry.fetchone()[0] == 0:
        check_entry.close()
        pass
    else:
        sys.exit('STOP! The entry `project_code`: {} and/or '
                 '`project_bill_nbr`: {} already exist.'
                 .format(args_dict['add'][1], args_dict['add'][2]))


def create_projects(args_dict, db):
    table_check(args_dict, db, exists=False)
    if args_dict['dbengine']=='mysql':
        sql_commands = [('''
            use {db};
            create table if not exists {table} (
                id int not null auto_increment,
                project_description varchar(128),
                project_code varchar(8),
                project_bill_nbr varchar(10),
                primary key (id)
            );
        '''.format(db=args_dict['db'], table=args_dict['proj_table']))]
    elif args_dict['dbengine'] == 'sqlite':
        sql_commands = [('''
            create table if not exists {table} (
                id integer primary key autoincrement,
                project_description varchar(128),
                project_code varchar(8),
                project_bill_nbr varchar(10)
            );
        '''.format(table=args_dict['proj_table']))]
    else:
        sys.exit(DB_ERROR_MESSAGE)

    if args_dict['dbengine'] == 'mysql':
        sql_commands.insert(0, 'create database if not exists {};'.format(args_dict['db']))

    sql_commands.append(('''
        insert into {table} (project_description, project_code, project_bill_nbr)
            values ('MyFirstProject', 'proj1', '111111');
    '''.format(table=args_dict['proj_table'])))

    return sql_commands


def add_projects(args_dict, db):
    table_check(args_dict, db)
    entry_check(args_dict, db)
    sql_commands = [('''
        insert into {table} (project_description, project_code, project_bill_nbr)
            values ("{desc}", "{code}", "{nbr}");
    '''.format(table=args_dict['proj_table'],
               desc=args_dict['add'][0],
               code=args_dict['add'][1],
               nbr=args_dict['add'][2]))]

    if args_dict['dbengine'] == 'mysql':
        sql_commands.insert(0, 'use {};'.format(args_dict['db']))

    return sql_commands


def check_projects(args_dict, db):
    table_check(args_dict, db)
    return pdsql.read_sql('select * from {table}'.format(table=args_dict['proj_table']), db)

def run(args_dict):
    args_dict = update_args(args_dict)
    if args_dict['check'] and args_dict['add']:
        sys.exit('STOP! You can\'t `check` and `add` entries at once.')

    if args_dict['dbengine'] == 'mysql':
        db = mdb.connect(
            host='{}'.format(args_dict['host']),
            user='{}'.format(USERNAME),
            password='{}'.format(PASSWORD),
            db=args_dict['db'],
            autocommit=True
        )
    elif args_dict['dbengine'] == 'sqlite':
        db = sqlite3.connect('{}.db'.format(args_dict['db']), isolation_level=None)
    else:
        sys.exit(DB_ERROR_MESSAGE)

    if args_dict['check']:
        print check_projects(args_dict, db)
    else:
        if args_dict['add']:
            sql_commands = add_projects(args_dict, db)
        else:
            sql_commands = create_projects(args_dict, db)

        for sql in sql_commands:
            db.cursor().execute(sql)
        db.cursor().close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a project table to database.')
    parser.add_argument('-d', '--db', required=False, help='Name of the database '
                        'to create.')
    parser.add_argument('-t', '--proj_table', required=False, help='Name of the '
                        'table to create.')
    parser.add_argument('-e', '--dbengine', required=False, choices=['mysql', 'sqlite'],
                        help='Database engine; will default to config settings.')
    parser.add_argument('-c', '--check', required=False, action='store_true',
                        help='Optional; check all entries in a database.')
    parser.add_argument('-a', '--add', required=False, nargs=3, help='Add an entry to '
                        'database; use three arguments in order: Project Description, '
                        'Project Code, Project Bill Number.')
    parser.add_argument('--host', required=False, help='Database host; will default to '
                        'config settings.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
