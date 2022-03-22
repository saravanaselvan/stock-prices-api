from flask_restful import Resource, reqparse

from models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, required=True,
                        help="Email required")
    parser.add_argument('password', type=str, required=True,
                        help="Password required")

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_email(data['email']):
            return {"message": "Email already exists."}, 400

        user = UserModel(**data)

        user.save_to_db()

        return {"message": "User created successfully."}, 201


class UserList(Resource):

    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}
