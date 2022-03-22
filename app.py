import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from db import db
from resources.calc import Calc
from resources.download_result import DownloadResult
from resources.uploaded_stocks import UploadedStocks
from resources.auth import Login
from resources.user import UserRegister

app = Flask(__name__)
uri = os.environ.get(
    'DATABASE_URL', 'test.db')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sdlakjfoiuwerfsdlk;jsdflk;sdjf;ld'
api = Api(app)

jwt = JWTManager(app)

api.add_resource(Calc, '/api/calc')
api.add_resource(UploadedStocks, '/api/uploaded_stocks')
api.add_resource(UserRegister, '/api/register')
api.add_resource(DownloadResult, '/api/download_result/<int:id>')
api.add_resource(Login, '/api/login')

if __name__ == "__main__":
    db.init_app(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    app.run(debug=True)
