from datetime import timedelta
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS

from db import db, migrate
from resources.calc import Calc
from resources.download_result import DownloadResult
from resources.uploaded_stocks import UploadedStocks
from resources.auth import Login
from resources.user import UserRegister

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
uri = os.environ.get(
    'DATABASE_URL', 'test.db')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=4)
app.config.from_pyfile('config.py')

UPLOAD_FOLDER = os.environ.get(
    'UPLOAD_FOLDER', 'private/input_price_files')
OUTPUT_FOLDER = os.environ.get(
    'OUTPUT_FOLDER', 'private/output_price_files')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

upload_dir = os.path.join(UPLOAD_FOLDER)
os.makedirs(upload_dir, exist_ok=True)
output_dir = os.path.join(OUTPUT_FOLDER)
os.makedirs(output_dir, exist_ok=True)

api = Api(app)

jwt = JWTManager(app)

api.add_resource(Calc, '/api/calc')
api.add_resource(UploadedStocks, '/api/uploaded_stocks')
api.add_resource(UserRegister, '/api/register')
api.add_resource(DownloadResult, '/api/download_result/<int:id>')
api.add_resource(Login, '/api/login')

db.init_app(app)
migrate.init_app(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":

    app.run(debug=True)
