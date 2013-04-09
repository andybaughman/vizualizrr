from flask import render_template
from flask import redirect
from flask import request
from flask import send_file
import settings

from app import app

import scriptz.contourz
from scriptz.contourz import main

import os


@app.route('/error')
def error():
    return render_template("error.html")

@app.route('/pitch')
def pitch():
    return render_template("pitchfinder.html")

@app.route('/upload', methods=['GET', 'POST'])
def file():
              # evalute the javascript expression

    if request.method == 'POST':
        file = request.files['file']
        if file:
            #filename = file.filename
            #fileName, fileExtension = os.path.splitext(filename)
            fileName = 'vizualizr.file'
            try:
                os.remove(os.path.join(settings.UPLOAD_FOLDER, fileName))
            except:
                pass
            
            contourList = contourz()

            file.save(os.path.join(settings.UPLOAD_FOLDER, fileName))
            return render_template("pitchfinder.html",contourList=contourList)
           
    return render_template("fileopen.html")

@app.route('/vizualizrfile')
def filereturn():
    return send_file('uploads/vizualizr.file',cache_timeout=1)

@app.route('/contourz')
def contourz():
    # call main() in scriptz.contourz
    return main()