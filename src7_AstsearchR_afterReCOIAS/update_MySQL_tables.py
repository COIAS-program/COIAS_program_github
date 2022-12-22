#!/usr/bin/env python3
# -*- coding: UTF-8 -*
#Timestamp: 2022/12/22 12:00 sugiura
###########################################################################################
# webCOIASにて今回の測定結果に基づいてMySQLのデータベースを更新する.
# 2022/12/22現在はとりあえず仮のスクリプトを置いておく.
###########################################################################################
import traceback
import print_detailed_log
import readparam

class InvalidIDError(Exception):
    pass

try:
    print("TEMPORALLY MESSAGE: THIS IS UPDATE_MYSQL_TABLE.PY!!!!")
    
    params = readparam.readparam()
    measurer_id = params["id"]
    if measurer_id < 0:
        raise InvalidIDError
    
    
except FileNotFoundError:
    print("Some previous files are not found in update_MySQL_tables.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 74

except InvalidIDError:
    print(f"Invalid ID: id={measurer_id}. In webCOIAS, please specify valid id as follows: AstsearchR_afterReCOIAS id=yourUserID.")
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 75

except Exception:
    print("Some errors occur in update_MySQL_tables.py!",flush=True)
    print(traceback.format_exc(),flush=True)
    error = 1
    errorReason = 75

else:
    error = 0
    errorReason = 74

finally:
    errorFile = open("error.txt","a")
    errorFile.write("{0:d} {1:d} 714 \n".format(error,errorReason))
    errorFile.close()

    if error==1:
        print_detailed_log.print_detailed_log(dict(globals()))
