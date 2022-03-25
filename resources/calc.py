import os
from sqlalchemy import schema

import werkzeug
from models.price_file import PriceFile
import datetime
from flask_restful import Resource, reqparse
from flask import request, current_app, json, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from db import db
import jsonschema
from jsonschema import validate

ALLOWED_EXTENSIONS = {'json'}

inputFileSchema = {
    "type": "object",
    "properties": {
        "begin_date": {"type": "string"},
        "end_date": {"type": "string"},
        "price_ts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "eff_date": {"type": "string"},
                    "price": {"type": "number"}
                },
                "required": ["eff_date", "price"]
            },
        }
    },
    "required": ["begin_date", "end_date", "price_ts"]
}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Calc(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True,
                        help="File is required")

    @jwt_required()
    def post(self):
        data = Calc.parser.parse_args()
        file = data['file']
        if allowed_file(file.filename):
            uploaded_filename = secure_filename(file.filename)
            new_filename = f'{uploaded_filename.split(".")[0]}_{datetime.datetime.now().strftime("%d_%m_%Y_%H:%M:%S")}.json'
            input_file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], new_filename)
            file.save(input_file_path)

            with open(input_file_path) as prices_file:
                data = json.load(prices_file)

            try:
                validate(instance=data, schema=inputFileSchema)
            except jsonschema.exceptions.ValidationError as err:
                os.remove(input_file_path)
                return {'message': f"{err.json_path} - {err.message}"}, 400

            begin_date = data['begin_date']
            end_date = data['end_date']
            prices = data['price_ts']

            filtered_prices = list(filter(
                lambda price: price["eff_date"] >= begin_date and price["eff_date"] <= end_date, prices))
            total = sum(price["price"] for price in filtered_prices)
            avg = total / len(filtered_prices)
            output_data = {"Sum": total, "Average": avg}
            output_path = os.path.join(
                current_app.config['OUTPUT_FOLDER'], new_filename)
            with open(output_path, 'w') as output:
                json.dump(output_data, output)

                try:
                    price_file = PriceFile(
                        original_uploaded_file_name=uploaded_filename,
                        uploaded_file_name=new_filename,
                        output_file_path=output_path,
                        output_file_name=new_filename,
                        begin_date=begin_date,
                        end_date=end_date,
                        sum=total,
                        average=avg,
                        created_at=datetime.datetime.now())
                    price_file.save_to_db()
                except BaseException as e:
                    return f'{e}'

            return {
                "id": price_file.id,
                "created_at": str(price_file.created_at),
                "original_uploaded_file_name": price_file.original_uploaded_file_name,
                "output_file_name": price_file.output_file_name,
                "begin_date": str(price_file.begin_date.strftime("%d-%m-%Y")),
                "end_date": str(price_file.end_date.strftime("%d-%m-%Y")),
                "sum": total,
                "average": avg
            }

        return "Only JSON file type is accepted", 500
