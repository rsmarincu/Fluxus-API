import pytest

from pandas_api import app as pandas_app


@pytest.fixture
def app():
    yield pandas_app

@pytest.fixture
def client(app):
    return app.test_client()