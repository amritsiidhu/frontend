import os
import subprocess
import sys

from bs4 import BeautifulSoup
from flask import current_app

import pytest
import mock
from mock import Mock

from app import create_app, get_env

# Don't import app.settings to avoid importing google.appengine.ext
sys.modules['app.settings'] = Mock()

AUTH_USERNAME = 'user'
AUTH_PASSWORD = 'pass'


@pytest.yield_fixture(scope='session')
def app():
    _app = create_app(**{
        'TESTING': True,
        'PREFERRED_URL_SCHEME': 'http',
        'ADMIN_CLIENT_ID': 'admin',
        'ADMIN_CLIENT_SECRET': 'secret',
        'API_BASE_URL': 'http://na_api_base',
        'SECRET_KEY': 'secret_key',
        'AUTH_USERNAME': AUTH_USERNAME,
        'AUTH_PASSWORD': AUTH_PASSWORD
    })

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def os_environ():
    """
    clear os.environ, and restore it after the test runs
    """
    # for use whenever you expect code to edit environment variables
    old_env = os.environ.copy()

    class EnvironDict(dict):
        def __setitem__(self, key, value):
            assert type(value) == str
            super(EnvironDict, self).__setitem__(key, value)

    os.environ = EnvironDict()
    yield
    os.environ = old_env


def request(url, method, data=None, headers=None):
    r = method(url, data=data, headers=headers)
    r.soup = BeautifulSoup(r.get_data(as_text=True), 'html.parser')
    return r


@pytest.fixture(scope='function')
def client(app):
    with app.test_request_context(), app.test_client() as client:
        yield client


@pytest.fixture
def logged_in(mocker):
    class Request(object):
        class Authorization(object):
            username = AUTH_USERNAME
            password = AUTH_PASSWORD
        authorization = Authorization
    mocker.patch("app.main.views.request", Request)


@pytest.fixture
def invalid_log_in(mocker):
    class Request(object):
        class Authorization(object):
            username = "invalid"
            password = "wrong"
        authorization = Authorization
    mocker.patch("app.main.views.request", Request)
