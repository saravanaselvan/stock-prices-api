from json import dumps
from datetime import datetime
from db import db
from flask_jwt_extended import get_jwt_identity


class PriceFile(db.Model):
    __tablename__ = 'price_files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')
    original_uploaded_file_name = db.Column(db.String(240))
    uploaded_file_name = db.Column(db.String(240))
    output_file_path = db.Column(db.String(240))
    output_file_name = db.Column(db.String(240))
    begin_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    sum = db.Column(db.Float(precision=2))
    average = db.Column(db.Float(precision=2))
    created_at = db.Column(db.DateTime)

    def __init__(self,
                 original_uploaded_file_name,
                 uploaded_file_name,
                 output_file_path,
                 output_file_name,
                 begin_date,
                 end_date,
                 sum,
                 average,
                 created_at):
        self.user_id = get_jwt_identity()
        self.original_uploaded_file_name = original_uploaded_file_name
        self.uploaded_file_name = uploaded_file_name
        self.output_file_path = output_file_path
        self.output_file_name = output_file_name
        self.created_at = created_at

        print(begin_date)

        self.begin_date = datetime.strptime(begin_date, '%d/%m/%Y').date()
        self.end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
        self.sum = sum
        self.average = average

    def __repr__(self):
        return '<PriceFile %r>' % self.id

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_uploaded_file_name': self.original_uploaded_file_name,
            'uploaded_file_name': self.uploaded_file_name,
            'output_file_path': self.output_file_path,
            'output_file_name': self.output_file_name,
            'begin_date': str(self.begin_date.strftime("%d-%m-%Y")),
            'end_date': str(self.end_date.strftime("%d-%m-%Y")),
            'sum': self.sum,
            'average': self.average,
            'created_at': str(self.created_at)
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
