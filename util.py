
from flask import jsonify, make_response
import certifi
from pymongo import MongoClient
import json
from inspect import getframeinfo, stack
import logging
import os

LOG_LEVEL = "DEBUG"
LOGFILE_NAME = "data_mining.log"

MSG =  "message"


def get_database(databaseName = "PractiseDb"):
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb+srv://subhankar:subhankar2028@cluster0.vwov3tz.mongodb.net/"+databaseName
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
   # Create the database for our example (we will use the same database throughout the tutorial
   return client[databaseName]

def dataresponse(function_name, data):
    logger(function_name+"() : ", data, level="debug")
    return make_response(jsonify(data), 200)


def errorresponse(function_name, err, message=None):
    logger(function_name+"() : ", err, level="error")
    data = {
        MSG : "Server error." if message==None else message,
        'err' : str(err)
    }
    return make_response(jsonify(data), 400)

def getenteredInfo(request):
    if request.method == "POST":
        return request.get_json()
    else:
        return None




logging.basicConfig(format='%(asctime)s-%(levelname)-6s:%(message)s', datefmt='%H:%M:%S', level=LOG_LEVEL, 
                    handlers=[logging.FileHandler(LOGFILE_NAME), logging.StreamHandler()])

# Logging method
def logger(tag = "", value = "", level = "info"):
    # add calling functions filename+line number
    caller = getframeinfo(stack()[1][0])
    only_filename = os.path.basename(caller.filename)
    caller_str = "%-18s:%-3d|" % (only_filename, caller.lineno)
    tag = "|"+caller_str+tag

    if level == "debug":
        logging.debug("= %s = %s", tag, value)
        
    elif level == "info":
        logging.debug(" INFO = %s = %s", tag, value)
        #logging.info("= %s", tag+"["+str(value)+"]")
        
    elif level == "warning":
        logging.debug("= %s = %s", tag, value)
        
    elif level == "error":
        if isinstance(value, Exception):
            # logging.exception("\n\t!!!!!!! = %s = %s", tag, value, exc_info=1)
            # print(traceback.print_exc(limit=1, file=sys.stdout))
            logging.exception('\n\t!!!!!!! = {} = {}'.format(tag, value))
        else:
            # logging.error("\n\t!!!!!!! = %s = %s", tag, value)
            # print(traceback.print_exc(limit=1, file=sys.stdout))
            logging.exception('\n\t!!!!!!! = {} = {}'.format(tag, value))

    else:
        print("!!!UNKNOWN LOGGING LEVEL!!!"+level)

