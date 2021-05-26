import datetime
from pathlib import Path, PosixPath
from unittest.mock import create_autospec

import pytest
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
from requests import Response

from gpy.gphotos import (
    GooglePhotosClient,
    UploadError,
    _save_access_token,
    upload_photo,
)


@pytest.mark.skip(reason="TODO: these test should be converted into a CLI command")
def test_dump_uploaded_pictures_from_1990_to_2005():
    client = GooglePhotosClient()
    client.start_session()

    # items_iterator = client.get_all_media_items()
    start = datetime.datetime(1990, 1, 1)
    end = datetime.datetime(2005, 1, 1)
    items_iterator = client.search_media_items(start=start, end=end)
    items = list(items_iterator)

    now = datetime.datetime.now()
    path = Path(f"uploaded_pictures_from_1990_to_2005-{now}.json")
    import json

    with path.open("w") as f:
        json.dump(items, f, indent=2)


# @pytest.mark.skip(reason="requires user interaction with the browser")
# def test_get_authorized_token_remembers_last_session():
#     auth_token = GOOGLE_OAUTH_CONFIG_DIR / AUTHORIZED_TOKEN_FILENAME

#     session_a = _get_authorized_session(auth_token_file=auth_token)
#     assert session_a is not None

#     session_b = _get_authorized_session(auth_token_file=auth_token)
#     assert session_b is not None

#     credentials_a = session_a.credentials.__dict__
#     credentials_a.pop("expiry")

#     credentials_b = session_b.credentials.__dict__
#     credentials_b.pop("expiry")

#     assert credentials_a == credentials_b


# @pytest.mark.skip(reason="requires user interaction with the browser")
# def test_authenticate_returns_credentials():
#     credentials_path = GOOGLE_OAUTH_CONFIG_DIR / CLIENT_SECRET_FILENAME
#     scopes = [
#         "https://www.googleapis.com/auth/photoslibrary",
#         "https://www.googleapis.com/auth/photoslibrary.sharing",
#     ]
#     credentials = _authenticate(credentials_path, scopes=scopes)
#     assert isinstance(credentials, Credentials)


# def test_authenticate_raises_if_credentials_file_does_not_exist():
#     credentials_path = Path("non/existing/path")
#     with pytest.raises(FileNotFoundError) as e:
#         _authenticate(credentials_path, scopes=[])

#     exc = e.value

#     assert exc.args == (
#         (
#             f"{credentials_path.absolute()} file does not exist\n\n"
#             "Please check the README to create one."
#         ),
#     )


def test_save_credentials(tmp_path: PosixPath) -> None:
    auth_token_file = tmp_path / "auth_token_file"

    credentials = Credentials(
        token="token",
        refresh_token="refresh_token",
        id_token=None,
        scopes=["scope_a", "scope_b"],
        token_uri="token_uri",
        client_id="client_id",
        client_secret="client_secret",
    )

    _save_access_token(credentials, auth_token_file)

    content = auth_token_file.read_text()

    assert content == (
        "{\n"
        '  "token": "token",\n'
        '  "refresh_token": "refresh_token",\n'
        '  "id_token": null,\n'
        '  "scopes": [\n'
        '    "scope_a",\n'
        '    "scope_b"\n'
        "  ],\n"
        '  "token_uri": "token_uri",\n'
        '  "client_id": "client_id",\n'
        '  "client_secret": "client_secret"\n'
        "}"
    )


def test_upload_photo__happy_path(tmp_path: PosixPath) -> None:
    mock_upload_response = create_autospec(Response)
    mock_upload_response.status_code = 200
    mock_upload_response.content = b"upload response body"

    mock_create_response = create_autospec(Response)
    mock_create_response.json.return_value = {
        "newMediaItemResults": [
            {"status": {"code": 0}},
        ]
    }

    mock_session = create_autospec(AuthorizedSession)
    mock_session.headers = {}
    mock_session.post.side_effect = [mock_upload_response, mock_create_response]

    path = tmp_path / "photo_to_upload.jpg"
    path.write_bytes(b"photo content")

    upload_photo(mock_session, path)


def test_raise_upload_photo__handled_server_error(tmp_path: PosixPath) -> None:
    mock_upload_response = create_autospec(Response)
    mock_upload_response.status_code = 200
    mock_upload_response.content = b"upload response body"

    mock_create_response = create_autospec(Response)
    mock_create_response.status_code = 200
    mock_create_response.json.return_value = {
        "newMediaItemResults": [
            {
                "status": {
                    "code": 1,
                    "message": "status message",
                }
            },
        ]
    }

    mock_session = create_autospec(AuthorizedSession)
    mock_session.headers = {}
    mock_session.post.side_effect = [mock_upload_response, mock_create_response]

    path = tmp_path / "photo_to_upload.jpg"
    path.write_bytes(b"photo content")

    with pytest.raises(UploadError) as e:
        upload_photo(mock_session, path)

    exc = e.value

    assert exc.args == (f"Could not add {path!r} to library -- status message",)


def test_raise_upload_photo__other_handled_server_error(tmp_path: PosixPath) -> None:
    mock_upload_response = create_autospec(Response)
    mock_upload_response.status_code = 200
    mock_upload_response.content = b"upload response body"

    mock_create_response = create_autospec(Response)
    mock_create_response.json.return_value = {"foo": "bar"}

    mock_session = create_autospec(AuthorizedSession)
    mock_session.headers = {}
    mock_session.post.side_effect = [mock_upload_response, mock_create_response]

    path = tmp_path / "photo_to_upload.jpg"
    path.write_bytes(b"photo content")

    with pytest.raises(UploadError) as e:
        upload_photo(mock_session, path)

    exc = e.value

    assert exc.args == (
        f"Could not add {path!r} to library. Server Response -- " "{'foo': 'bar'}",
    )


def test_raise_upload_photo__unhandled_server_error(tmp_path: PosixPath) -> None:
    mock_upload_response = create_autospec(Response)
    mock_upload_response.status_code = 500  # non 200
    mock_upload_response.content = b"upload response body"

    mock_session = create_autospec(AuthorizedSession)
    mock_session.headers = {}
    mock_session.post.side_effect = [mock_upload_response]

    path = tmp_path / "photo_to_upload.jpg"
    path.write_bytes(b"photo content")

    with pytest.raises(UploadError) as e:
        upload_photo(mock_session, path)

    exc = e.value

    assert exc.args == (
        f"Could not upload {path!r}. Server Response - {mock_upload_response}",
    )
