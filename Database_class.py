import os
import psycopg2
import asyncio

from windyquery import DB
# !/usr/bin/python
from configparser import ConfigParser

import DOM_class


def config_db(filename=os.getcwd() + '\\database\\database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


# !/usr/bin/python


def connect_to_db():
    """ Connect to the PostgreSQL database server """
    db = DB()
    try:

        # read connection parameters
        params = config_db()

        print('Connecting to the PostgreSQL database...')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.get_event_loop().run_until_complete(db.connect("dom", config=params, default=True,
                                                               max_inactive_connection_lifetime=100))
        print('PostgreSQL database version:')
        asyncio.get_event_loop().run_until_complete(insert_to_db_query(db))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        asyncio.get_event_loop().run_until_complete(db.stop())
        print('Database connection closed.')


async def insert_to_db_query(db):
    data_list = DOM_class.get_dom_list()
    if data_list is None:
        return

    for dom in data_list:
        dict_row = {"id": dom.dom_id,
                    "dom": dom.dom,
                    "project": dom.project,
                    "next_dom": dom.next_dom,
                    "previous_dom": dom.previous_dom,
                    "url": dom.url,
                    "time": dom.time}
        try:
            await db.table('dom').insert(dict_row)
            await db.table('progress').delete()
            await db.table('progress').insert({
                "id": dom.dom_id,
                "url": dom.url,
                "project": dom.project,
                "timestamp": dom.time
            })
        except Exception as e:
            print("error occurred while inserting:" + str(e))
            continue

    return


def get_progress():
    db = DB()
    current_progress = []
    try:
        params = config_db()
        print('Connecting to the PostgreSQL database...')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.get_event_loop().run_until_complete(db.connect("dom", config=params, default=True,
                                                               max_inactive_connection_lifetime=100))

        current_progress = asyncio.get_event_loop().run_until_complete(progress_query(db))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        asyncio.get_event_loop().run_until_complete(db.stop())
        print('Database connection closed after getting progress.')
        return current_progress


async def progress_query(db):
    return await db.table('progress').select('*')


def experiment_insert(dom):
    db = DB()
    try:
        # read connection parameters
        params = config_db()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        # conn = psycopg2.connect(**params)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.get_event_loop().run_until_complete(db.connect("dom", config=params, default=True,
                                                               max_inactive_connection_lifetime=100))
        asyncio.get_event_loop().run_until_complete(insert_list(db, dom))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        asyncio.get_event_loop().run_until_complete(db.stop())
        print('Database connection closed.')


async def insert_list(db, dom):
    data_dict = {"id": dom.dom_id,
                 "dom": dom.dom,
                 "project": dom.project,
                 "next_dom": dom.next_dom,
                 "previous_dom": dom.previous_dom,
                 "url": dom.url,
                 "time": dom.time}
    await db.table('dom').insert(data_dict)


def get_websites():
    db = DB()
    websites = []
    try:
        params = config_db()
        print('Connecting to the PostgreSQL database...')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.get_event_loop().run_until_complete(db.connect("dom", config=params, default=True,
                                                               max_inactive_connection_lifetime=100))

        websites = asyncio.get_event_loop().run_until_complete(websites_query(db))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        asyncio.get_event_loop().run_until_complete(db.stop())
        print('Database connection closed after getting websites.')
        return websites


async def websites_query(db):
    result_list = []
    result = await db.raw('select Distinct project from dom;')
    for row in result:
        result_list.append(row['project'].upper())
    return result_list


def get_history(project_name):
    db = DB()
    history = []
    try:
        params = config_db()
        print('Connecting to the PostgreSQL database...')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.get_event_loop().run_until_complete(db.connect("dom", config=params, default=True,
                                                               max_inactive_connection_lifetime=100))
        history = asyncio.get_event_loop().run_until_complete(entire_history_query(db,project_name))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        asyncio.get_event_loop().run_until_complete(db.stop())
        print('Database connection closed after getting websites.')
        return history


async def entire_history_query(db, project_name):
    result_list = []
    # result = await db.table('dom').select('*').where('project', project_name)
    result = await db.raw('select * from dom where upper(project) = ' + "project_name" + ';')
    for row in result:
        result_list.append((row['dom'], row['project']))
