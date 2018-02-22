# all the imports
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, g, redirect, url_for, jsonify, \
    render_template, flash, current_app, send_from_directory, abort
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import json
import re
import ET_Flask.EagarTsai as ET


ALLOWED_EXTENSIONS = set(['txt', 'csv'])

bp = Blueprint('ET_Flask', __name__)

# needed functions for database and file handling
def getSharedLib(app):
    files = os.listdir(app.root_path)
    lib = [x for x in files if re.search('.so$',x)][0]
    return os.path.join(app.root_path,lib)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def addInitMaterials():
    materials = pd.read_csv(current_app.config['INIT_MATERIALS'],header=0)
    for _, material in materials.iterrows():
        add_entry(material.tolist())

    return True


def add_entry(new_material):
    db = get_db()
    db.execute("insert into materials (name, k, cp, rho, T) values (?, ?, ?, ?, ?)",
               new_material)
    db.commit()
    return True


def queryMaterials(query_str, args=()):
    db = get_db()
    cur = db.execute(query_str, args)
    materials = cur.fetchall()
    return materials


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def checkFile(filename, mode):
    try:
        data = pd.read_table(filename,header=None,delimiter=',')
        assert data.shape[1] == 4
        if mode:
            assert data.shape[0] > 0
        else:
            assert data.shape[0] == 1
        
        assert not isinstance(data.iloc[0,0],str)
        return True
    except:
        return False

def calculateET(filename, material, mode):
    try:
        getET = ET.EagarTsai(mode, current_app.config['SHARED_LIB'])
        getET.compute(current_app.config['UPLOAD_FOLDER'],filename,material)
        return True
    except Exception as e:
        print(e)
        return False


# main page where user inputs query
@bp.route('/', methods=['GET','POST'])
def index():
    error = None
    if request.method == 'POST':
        # get the form
        whatToDo = request.form.get("main_menu", type=int)
    
        if whatToDo == 1:
            return redirect(url_for('ET_Flask.meltpool'))
        elif whatToDo == 2:
            return redirect(url_for('ET_Flask.temperatures'))
        else:
            error = 'Invalid option'
    
    return render_template("index.html", error=error)


@bp.route('/meltpool', methods=['GET','POST'])
def meltpool():
    error = None
    materials = queryMaterials('select id, name from materials order by name asc')
    
    if request.method == 'POST':
        #get the material
        materialID = request.form['material']
        if materialID == 'other':
            new_name = request.form.get("new_name", type=str)
            new_k = request.form.get("new_k", type=float)
            new_cp = request.form.get("new_cp", type=float)
            new_rho = request.form.get("new_rho", type=float)
            new_T = request.form.get("new_T", type=float)

            listMaterials = set(material['name'] for material in materials)
            if new_name not in listMaterials:
                add_entry([new_name, new_k, new_cp, new_rho, new_T])
                flash('New material was successfully added')
                materialID = len(listMaterials) + 1
            else:
                flash('Material already exists. Choose it from the drop-down list.')
                return redirect(request.url)
        
        simMaterial = queryMaterials('select name,k,cp,rho,T from materials where id = ?',
                                     [materialID])[0]
        
        if 'file_up' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file_up']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        #mode 1 for meltpool
        mode = 1
        if not checkFile(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), mode):
            flash('Please check file <em>' + filename + '</em> is in the correct format.')
            return redirect(request.url)
        
        flash('File <em>' + filename + '</em> was successfully read.')
        calculateSuccess = calculateET(filename, simMaterial, mode)
        if calculateSuccess:
            outputfile = filename.rsplit('.',1)[0] + '_out.csv'
            return render_template("success.html", filename=outputfile)
#            return redirect(url_for('ET_Flask.success', filename=outputfile))
        else:
            flash('There was a problem with file <em>' + filename + '</em>. Please check it.')
            return redirect(request.url)

    return render_template("meltpool.html", materials=materials, error=error)


@bp.route('/success')
def success():
    if not request.args:
        return redirect(url_for('ET_Flask.index'))

    if 'filename' not in request.args:
        return redirect(url_for('ET_Flask.index'))

    filename=request.args.get('filename', type=str)
    if filename not in os.listdir(current_app.config['UPLOAD_FOLDER']):
        return redirect(url_for('ET_Flask.index'))

    return render_template("success.html", filename=request.args.get('filename', type=str))

@bp.route('/downloads/<path:filename>')
def download(filename):
    return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], filename=filename)

@bp.route('/temperatures', methods=['GET','POST'])
def temperatures():
    error = None
    materials = queryMaterials('select id, name from materials order by name asc')
    
    if request.method == 'POST':
        #get the material
        materialID = request.form['material']
        if materialID == 'other':
            new_name = request.form.get("new_name", type=str)
            new_k = request.form.get("new_k", type=float)
            new_cp = request.form.get("new_cp", type=float)
            new_rho = request.form.get("new_rho", type=float)
            new_T = request.form.get("new_T", type=float)

            listMaterials = set(material['name'] for material in materials)
            if new_name not in listMaterials:
                add_entry([new_name, new_k, new_cp, new_rho, new_T])
                flash('New material was successfully added')
                materialID = len(listMaterials) + 1
            else:
                flash('Material already exists. Choose it from the drop-down list.')
                return redirect(request.url)
        
        simMaterial = queryMaterials('select name,k,cp,rho,T from materials where id = ?',
                                     [materialID])[0]
        
        if 'file_up' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file_up']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        #mode 0 for temperatures
        mode = 0
        if not checkFile(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), mode):
            flash('Please check file <em>' + filename + '</em> is in the correct format.')
            return redirect(request.url)
        
        flash('File <em>' + filename + '</em> was successfully read.')
        calculateSuccess = calculateET(filename, simMaterial, mode)
        if calculateSuccess:
            outputfile = filename.rsplit('.',1)[0] + '_out.json'
            return redirect(url_for('ET_Flask.success', filename=outputfile))
        else:
            flash('There was a problem with file <em>' + filename + '</em>. Please check it.')
            return redirect(request.url)

    return render_template("temperatures.html", materials=materials, error=error)


@bp.route('/materials')
def materials():
    error = None
    materials = queryMaterials('select * from materials order by name asc')
    return render_template("materials.html", error=error, materials=materials)


@bp.route('/api/meltpools', methods=['POST'])
def api_meltpool():
    if not request.json or not 'cases' in request.json or not 'material' in request.json:
        abort(400)
    
    inputCases = request.json
    filename = os.path.join(current_app.config['UPLOAD_FOLDER'], 'api_meltpools.csv')
    np.savetxt(filename, inputCases['cases'], delimiter=',')
    simMaterial = queryMaterials('select name,k,cp,rho,T from materials where id = ?',
                                 [inputCases['material']])
    if not simMaterial:
        return jsonify({"Error": "No material found"}), 400
    else:
        simMaterial = simMaterial[0]

    mode = 1
    calculateSuccess = calculateET('api_meltpools.csv', simMaterial, mode)
#    calculateSuccess = 1
    if calculateSuccess:
        return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], filename='api_meltpools_out.csv')
    else:
        return jsonify({"Error": "Simulation didn't finish"}), 400

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
