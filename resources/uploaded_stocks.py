from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.price_file import PriceFile


class UploadedStocks(Resource):

    @jwt_required()
    def get(self):
        prices = PriceFile.query.order_by(PriceFile.created_at.desc()).filter_by(
            user_id=get_jwt_identity()).all()
        return {'prices': [price.json() for price in prices]}
