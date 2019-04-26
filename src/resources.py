from flask_restful import Resource, abort, reqparse
from src.models import UserModel, RevokedTokenModel
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

todos = {
    "todo1": {
        "status": False,
        "content": "Do something"
    },
    "todo2": {
        "status": True,
        "content": "Do something else"
    }
}

todo_parser = reqparse.RequestParser()
todo_parser.add_argument("status", type=bool)
todo_parser.add_argument("content")

user_parser = reqparse.RequestParser()
user_parser.add_argument("username")
user_parser.add_argument("password")


class Todo(Resource):

    path = "/todos"

    @jwt_required
    def get(self):
        return todos

    @jwt_required
    def post(self):
        args = todo_parser.parse_args()
        todo_id = int(max(todos.keys()).lstrip("todo")) + 1
        todo_id = "todo%i" % todo_id
        todos[todo_id] = {"status": args["status"],
                          "content": args["content"]}
        return todos[todo_id], 201


def abort_if_doesnt_exist(resource_id, resource_container):
    if resource_id not in resource_container:
        abort(404, message="Resource {} does not exist!".format(resource_id))


class TodoSingle(Resource):

    path = "/todos/<string:todo_id>"

    @jwt_required
    def get(self, todo_id):
        abort_if_doesnt_exist(todo_id, todos)
        return todos[todo_id]

    @jwt_required
    def put(self, todo_id):
        args = todo_parser.parse_args()
        task = {"status": args["status"],
                "content": args["content"]}
        todos[todo_id] = task
        return task, 201

    @jwt_required
    def delete(self, todo_id):
        abort_if_doesnt_exist(todo_id, todos)
        del todos[todo_id]
        return "", 204


class UserRegistration(Resource):

    path = "/register"

    def post(self):
        data = user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):

    path = "/login"
    def post(self):
        data = user_parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class AllUsers(Resource):

    path = "/users"

    @jwt_required
    def get(self):
        return UserModel.return_all()

    @jwt_required
    def delete(self):
        return UserModel.delete_all()


class TokenRefresh(Resource):

    path = "/refresh"

    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}


class UserLogoutAccess(Resource):

    path = "/logout/access"

    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):

    path = "/logout/refresh"

    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
