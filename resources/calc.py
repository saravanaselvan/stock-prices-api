import os
from models.price_file import PriceFile
import datetime
from flask_restful import Resource
from flask import request, current_app, json
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from db import db


class Calc(Resource):

    @jwt_required()
    def post(self):
        print(get_jwt_identity())
        file = request.files['file']
        uploaded_filename = secure_filename(file.filename)
        new_filename = f'{uploaded_filename.split(".")[0]}_{datetime.datetime.now().strftime("%d_%m_%Y_%H:%M:%S")}.json'
        input_file_path = os.path.join(
            current_app.static_folder, "input_price_files", new_filename)
        file.save(input_file_path)

        with open(input_file_path) as prices_file:
            data = json.load(prices_file)

        begin_date = data['begin_date']
        end_date = data['end_date']
        prices = data['price_ts']

        def prices_filter(price):
            if(price["eff_date"] >= begin_date and price["eff_date"] <= end_date):
                return True
            else:
                return False

        filtered_prices = list(filter(prices_filter, prices))
        total = sum(price["price"] for price in filtered_prices)
        avg = total / len(filtered_prices)
        output_data = {"Sum": total, "Average": avg}
        output_path = os.path.join(
            current_app.static_folder, "output_price_files", new_filename)
        with open(output_path, 'w') as output:
            json.dump(output_data, output)

            try:
                priceFile = PriceFile(
                    original_uploaded_file_name=uploaded_filename,
                    uploaded_file_name=new_filename,
                    output_file_path=output_path,
                    output_file_name=new_filename,
                    begin_date=begin_date,
                    end_date=end_date,
                    sum=total,
                    average=avg,
                    created_at=datetime.datetime.now())
                db.session.add(priceFile)
                db.session.commit()
                db.session.refresh(priceFile)
            except BaseException as e:
                return f'{e}'

        return {
            "id": priceFile.id,
            "created_at": str(priceFile.created_at),
            "original_uploaded_file_name": priceFile.original_uploaded_file_name,
            "output_file_name": priceFile.output_file_name,
            "begin_date": str(priceFile.begin_date.strftime("%d-%m-%Y")),
            "end_date": str(priceFile.end_date.strftime("%d-%m-%Y")),
            "sum": total,
            "average": avg
        }
