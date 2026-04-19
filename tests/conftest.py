import threading
import pytest
from werkzeug.serving import make_server

from web.app import app as flask_app

_CHROMIUM_PATH = '/opt/pw-browsers/chromium-1208/chrome-linux64/chrome'
_LIVE_PORT = 5099

flask_app.config['SECRET_KEY'] = 'test-secret-key'


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c
    flask_app.config['TESTING'] = False


@pytest.fixture(scope='session')
def live_server_url():
    srv = make_server('127.0.0.1', _LIVE_PORT, flask_app)
    t = threading.Thread(target=srv.serve_forever)
    t.daemon = True
    t.start()
    yield f'http://127.0.0.1:{_LIVE_PORT}'
    srv.shutdown()


@pytest.fixture(scope='session')
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        'executable_path': _CHROMIUM_PATH,
        'args': ['--no-sandbox', '--disable-dev-shm-usage'],
    }
