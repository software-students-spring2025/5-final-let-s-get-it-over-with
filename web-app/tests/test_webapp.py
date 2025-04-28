import pytest
import json
from flask import session
from werkzeug.wrappers import Response
import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app
import auth

@ pytest.fixture
def client():
    # Configure the Flask test client
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client

# Tests for add_cache_control

def test_add_cache_control_no_session():
    """
    ADD DOCSTRING
    """
    with app.app.test_request_context('/'):
        response = Response('data')
        modified = app.add_cache_control(response)
        assert 'Cache-Control' not in modified.headers


def test_add_cache_control_with_session():
    """
    ADD DOCSTRING
    """
    with app.app.test_request_context('/'):
        session['username'] = 'user1'
        response = Response('data')
        modified = app.add_cache_control(response)
        assert modified.headers['Cache-Control'].startswith('no-store')
        assert modified.headers['Pragma'] == 'no-cache'
        assert modified.headers['Expires'] == '-1'

# Tests for home route

def test_home_redirects_when_not_logged_in(client):
    """
    ADD DOCSTRING
    """
    resp = client.get('/')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_home_with_valid_session(monkeypatch, client):
    """
    ADD DOCSTRING
    """
    # Mock user exists in database
    monkeypatch.setattr(auth.users_collection, 'find_one', lambda q: {'username': q['username']})
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'dashboard' in resp.data
    assert resp.headers['Cache-Control'].startswith('no-store')


def test_home_session_expired(monkeypatch, client):
    """
    ADD DOCSTRING
    """
    # Mock user does not exist in database
    monkeypatch.setattr(auth.users_collection, 'find_one', lambda q: None)
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']
    # Session should be cleared
    with client.session_transaction() as sess:
        assert 'username' not in sess

def test_chat_redirects_when_not_logged_in(client):
    """
    ADD DOCSTRING
    """
    resp = client.get('/chat')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_chat_with_valid_session(monkeypatch, client):
    """
    ADD DOCSTRING
    """
    # Mock user exists in database
    monkeypatch.setattr(auth.users_collection, 'find_one', lambda q: {'username': q['username']})
    monkeypatch.setattr(app, 'render_template', lambda template, **ctx: f"RENDERED[{template}]")
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    resp = client.get('/chat')
    assert resp.status_code == 200
    assert b'chat' in resp.data
    assert resp.headers['Cache-Control'].startswith('no-store')


def test_chat_session_expired(monkeypatch, client):
    """
    ADD DOCSTRING
    """
    # Mock user does not exist in database
    monkeypatch.setattr(auth.users_collection, 'find_one', lambda q: None)
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    resp = client.get('/chat', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']
    # Session should be cleared
    with client.session_transaction() as sess:
        assert 'username' not in sess


class DummyResponse:
    """
    ADD DOCSTRING
    """
    def __init__(self, json_data, status_code):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json


def test_proxy_success(monkeypatch, client):
    """
    ADD DOCSTRING
    """
    dummy = DummyResponse({'msg': 'ok'}, 200)
    monkeypatch.setattr(requests, 'post', lambda url, json: dummy)
    payload = {'text': 'hello'}
    resp = client.post(
        '/generate-comment', 
        data=json.dumps(payload), 
        content_type='application/json',
    )
    assert resp.status_code == 200
    assert resp.get_json() == {'msg': 'ok'}


def test_proxy_failure(monkeypatch, client):
    """
    ADD DOCSTRING
    """
    def bad_post(url, json):
        raise Exception('fail')
    monkeypatch.setattr(requests, 'post', bad_post)
    resp = client.post('/generate-comment', data=json.dumps({}), content_type='application/json')
    assert resp.status_code == 500
    assert resp.get_json() == {'error': 'ML service unreachable'}

