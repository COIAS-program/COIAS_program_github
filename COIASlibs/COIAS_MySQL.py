#!/usr/bin/env python3
# -*- coding: UTF-8 -*
# Timestamp: 2023/01/27 20:30 sugiura
#####################################################################
# MySQLのCOIASデータベースにconnectする関数とcloseする関数を記したスクリプト
#####################################################################

import pymysql
import sys

sys.path.append("/home/COIASusers/web-coias-back-app/")
from API import config

### function: connect to the database COIAS ###############
def connect_to_COIAS_database():
    ## connect
    connection = pymysql.connect(
        host=config.DB_HOST,
        port=int(config.DB_PORT),
        user=config.DB_USER_NAME,
        database=config.DB_DATABASE_NAME,
        charset="utf8",
        password=config.DB_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor,
    )
    cursor = connection.cursor()

    return (connection, cursor)


###########################################################

### function: close the connection to the database COIAS ##
def close_COIAS_database(connection, cursor):
    cursor.close()
    connection.close()


###########################################################
