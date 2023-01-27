#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2023/01/27 20:30 sugiura
#####################################################################
# MySQLのCOIASデータベースにconnectする関数とcloseする関数を記したスクリプト
#####################################################################

import pymysql
from os.path import expanduser

### function: connect to the database COIAS ###############
def connect_to_COIAS_database():
    ## get password
    pwFileName = expanduser("~") + "/.pw/pwCOIASdb.txt"
    f = open(pwFileName, "r")
    pw = f.readline().rstrip("\n")
    f.close()

    ## connect
    connection = pymysql.connect(host="localhost",
                                 user="dataHandler",
                                 database="COIAS",
                                 charset="utf8",
                                 password=pw,
                                 cursorclass=pymysql.cursors.DictCursor
                                 )
    cursor = connection.cursor()

    return (connection, cursor)
###########################################################

### function: close the connection to the database COIAS ##
def close_COIAS_database(connection, cursor):
    cursor.close()
    connection.close()
###########################################################
