from flask import Flask, redirect, render_template, request, send_file
#app = Flask(__name__)

import json, os, settings

from app import app

# Contours
import scriptz.contourz
from scriptz.contourz import returnContourz

# data_to_json
from collections import namedtuple, Iterable, OrderedDict
import numpy as np


@app.route('/error')
def error():
    return render_template("error.html")


@app.route('/pitch')
def pitch():
    return render_template("pitchfinder.html")


@app.route('/upload', methods=['GET', 'POST'])
def file():

    # Get geometric contours
    global contourList
    contourList = contourz()
   
    # Ajax call for contours
    if request.method == 'GET':
#
# TO-DO - resize user supplied images
#
        processContours = request.args.get('processContours')
        
        if processContours:
            # Return all contours
            return data_to_json(contourList)

    # Audio file posted
    if request.method == 'POST':
        
        file = request.files['file']
        
        uploaded_file = request.files['file']
        #print uploaded_file

        if file:
            
            fileName = file.filename #'vizualizr.file'
            
            #try:
            #    os.remove(os.path.join(settings.UPLOAD_FOLDER, fileName))
            #except:
            #    pass

            file.save(os.path.join(settings.UPLOAD_FOLDER, fileName))

            return render_template("pitchfinder.html") 
            #,contourList=contourList[0][1] #map(json.dumps,contourList) #json.dumps([1,2,3])
           
    return render_template("fileopen.html")


@app.route('/vizualizrfile')
def filereturn():
    #return file()

    return send_file('uploads/The_Impossebulls_-_05_-_AmeriKan_Idle_Instrumental.mp3', cache_timeout=1) #blind_willie.mp3
    
    #The_Impossebulls_-_05_-_AmeriKan_Idle_Instrumental.mp3
    #piano-slow-songs-romeo-and-juliet-love-theme-kissing-you-instrumental1.mp3
    #self.request.params[<form element name with file>].filename

@app.route('/contourz')
def contourz():
    # call returnContourz() in scriptz.contourz
    return returnContourz()

@app.route('/')
def home():
    return render_template("pitchfinder.html")

#if __name__ == '__main__':
#    app.run(port=8080, debug=True)




#
# http://robotfantastic.org/serializing-python-data-to-json-some-edge-cases.html
#

def isnamedtuple(obj):
    """Heuristic check if an object is a namedtuple."""
    return isinstance(obj, tuple) \
           and hasattr(obj, "_fields") \
           and hasattr(obj, "_asdict") \
           and callable(obj._asdict)

def serialize(data):
    if data is None or isinstance(data, (bool, int, long, float, basestring)):
        return data
    if isinstance(data, list):
        return [serialize(val) for val in data]
    if isinstance(data, OrderedDict):
        return {"py/collections.OrderedDict":
                [[serialize(k), serialize(v)] for k, v in data.iteritems()]}
    if isnamedtuple(data):
        return {"py/collections.namedtuple": {
            "type":   type(data).__name__,
            "fields": list(data._fields),
            "values": [serialize(getattr(data, f)) for f in data._fields]}}
    if isinstance(data, dict):
        if all(isinstance(k, basestring) for k in data):
            return {k: serialize(v) for k, v in data.iteritems()}
        return {"py/dict": [[serialize(k), serialize(v)] for k, v in data.iteritems()]}
    if isinstance(data, tuple):
        return {"py/tuple": [serialize(val) for val in data]}
    if isinstance(data, set):
        return {"py/set": [serialize(val) for val in data]}
    if isinstance(data, np.ndarray):
        return {"py/numpy.ndarray": {
            "values": data.tolist(),
            "dtype":  str(data.dtype)}}
    raise TypeError("Type %s not data-serializable" % type(data))

def restore(dct):
    if "py/dict" in dct:
        return dict(dct["py/dict"])
    if "py/tuple" in dct:
        return tuple(dct["py/tuple"])
    if "py/set" in dct:
        return set(dct["py/set"])
    if "py/collections.namedtuple" in dct:
        data = dct["py/collections.namedtuple"]
        return namedtuple(data["type"], data["fields"])(*data["values"])
    if "py/numpy.ndarray" in dct:
        data = dct["py/numpy.ndarray"]
        return np.array(data["values"], dtype=data["dtype"])
    if "py/collections.OrderedDict" in dct:
        return OrderedDict(dct["py/collections.OrderedDict"])
    return dct

def data_to_json(data):
    return json.dumps(serialize(data))

def json_to_data(s):
    return json.loads(s, object_hook=restore)