import pytest

from math_api import app as math_app


@pytest.fixture
def app():
    yield math_app

@pytest.fixture
def client(app):
    return app.test_client()