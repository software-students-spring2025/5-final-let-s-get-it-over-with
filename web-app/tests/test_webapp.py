"""
Tests for app.py
"""

import json as js
import sys
import os
import pytest
from flask import session
from werkzeug.wrappers import Response
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import app
import auth

# pylint: enable=wrong-import-position


@pytest.fixture(name="client")
def fixture_client():
    """Configure the Flask test client"""
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


def test_add_cache_control_no_session():
    """Test for add_cache_control without a session"""
    with app.app.test_request_context("/"):
        response = Response("data")
        modified = app.add_cache_control(response)
        assert "Cache-Control" not in modified.headers


def test_add_cache_control_with_session():
    """Test for add_cache_control with a session"""
    with app.app.test_request_context("/"):
        session["username"] = "user1"
        response = Response("data")
        modified = app.add_cache_control(response)
        assert modified.headers["Cache-Control"].startswith("no-store")
        assert modified.headers["Pragma"] == "no-cache"
        assert modified.headers["Expires"] == "-1"


def test_home_redirects_when_not_logged_in(client):
    """tests home route"""
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_home_with_valid_session(monkeypatch, client):
    """tests home route when logged in"""
    monkeypatch.setattr(
        auth.users_collection, "find_one", lambda q: {"username": q["username"]}
    )
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"dashboard" in resp.data
    assert resp.headers["Cache-Control"].startswith("no-store")


def test_home_session_expired(monkeypatch, client):
    """tests home route when session expires"""
    # Mock user does not exist in database
    monkeypatch.setattr(auth.users_collection, "find_one", lambda q: None)
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
    # Session should be cleared
    with client.session_transaction() as sess:
        assert "username" not in sess


def test_chat_redirects_when_not_logged_in(client):
    """tests redirection from chat when not logged in"""
    resp = client.get("/chat")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_chat_with_valid_session(monkeypatch, client):
    """tests chat when user is valid and logged in"""
    monkeypatch.setattr(
        auth.users_collection, "find_one", lambda q: {"username": q["username"]}
    )
    monkeypatch.setattr(
        app, "render_template", lambda template, **ctx: f"RENDERED[{template}]"
    )
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    resp = client.get("/chat")
    assert resp.status_code == 200
    assert b"chat" in resp.data
    assert resp.headers["Cache-Control"].startswith("no-store")


def test_chat_session_expired(monkeypatch, client):
    """tests chat route when session is expired"""
    monkeypatch.setattr(auth.users_collection, "find_one", lambda q: None)
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    resp = client.get("/chat", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
    # Session should be cleared
    with client.session_transaction() as sess:
        assert "username" not in sess


class DummyResponse:
    """creates dummy response to circumvent real connection"""

    def __init__(self, json_data, status_code):
        """initializes dummy response"""
        self._json = json_data
        self.status_code = status_code

    def json(self):
        """returns json"""
        return self._json

    def get_status_code(self):
        """returns json"""
        return self.status_code


def test_proxy_success(monkeypatch, client):
    """tests successful connection to ml-client"""
    dummy = DummyResponse({"msg": "ok"}, 200)
    monkeypatch.setattr(requests, "post", lambda url, json: dummy)
    payload = {"text": "hello"}
    resp = client.post(
        "/generate-comment", data=js.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 200
    assert resp.get_json() == {"msg": "ok"}


def test_proxy_failure(monkeypatch, client):
    """tests unsuccessful connection to ml-client"""

    def bad_post(url, json):
        raise RuntimeError("Recieved failing status code from url")

    monkeypatch.setattr(requests, "post", bad_post)
    resp = client.post(
        "/generate-comment", data=js.dumps({}), content_type="application/json"
    )
    assert resp.status_code == 500
    assert resp.get_json() == {"error": "ML service unreachable"}
