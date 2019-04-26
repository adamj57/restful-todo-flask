import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
    client = app.test_client()
    yield client


def test_register(client):
    rv = client.post("/register", data=dict(username="test", password="test"))

    assert b"User test was created" in rv.data
