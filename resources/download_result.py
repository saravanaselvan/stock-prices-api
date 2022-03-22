from flask import send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.price_file import PriceFile


class DownloadResult(Resource):

    @jwt_required()
    def get(self, id):
        price_file = PriceFile.query.filter_by(
            id=id, user_id=get_jwt_identity()).first()
        file_path = price_file.output_file_path
        return send_file(file_path, as_attachment=True)
