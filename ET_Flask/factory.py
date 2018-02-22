
import os
from flask import Flask, g
from werkzeug.utils import find_modules, import_string
from ET_Flask.blueprints.ET_Flask import init_db, addInitMaterials, getSharedLib


def create_app(config=None):
    app = Flask('ET_Flask')
    app.config.update(dict(
                           DATABASE=os.path.join(app.root_path, 'ET_Materials.db'),
                           INIT_MATERIALS=os.path.join(app.root_path, 'init_materials.csv'),
                           DEBUG=True,
                           SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
                           UPLOAD_FOLDER=os.path.join(app.root_path, 'tmp'),
                           MAX_CONTENT_LENGTH=10 * 1024,
                           SHARED_LIB=getSharedLib(app)
                           ))
    app.config.update(config or {})
    app.config.from_envvar('ET_FLASK_SETTINGS', silent=True)
    
    register_blueprints(app)
    register_cli(app)
    register_teardowns(app)

    return app


def register_blueprints(app):
    """Register all blueprint modules."""
    for name in find_modules('ET_Flask.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None


def register_cli(app):
    @app.cli.command('initdb')
    def initdb_command():
        """Creates the database tables."""
        init_db()
        addInitMaterials()
        print('Initialized the database.')


def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        """Closes the database again at the end of the request."""
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()
