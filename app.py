from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
import inspect



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    import secrets
    app.config['SECRET_KEY'] = secrets.FLASK_SECRET
    app.config['JWT_SECRET_KEY'] = secrets.JWT_SECRET
except:
    app.config['SECRET_KEY'] = "1234"  # not secure!
    app.config['JWT_SECRET_KEY'] = "5678"  # not secure!


app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

jwt = JWTManager(app)
db = SQLAlchemy(app)
api = Api(app)

from src import models, resources

for name, obj in inspect.getmembers(resources):
    if inspect.isclass(obj):
        if issubclass(obj, Resource) and obj != Resource:
            api.add_resource(obj, obj.path)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=1234)
