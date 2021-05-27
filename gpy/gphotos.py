import datetime
import json
import logging
from pathlib import Path
from typing import Any, Iterator, List, Optional

import pytz
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from gpy.config import DEFAULT_TZ
from gpy.filesystem import read_json, write_json
from gpy.types import JsonDict, MediaItem, MediaMetadata, structure, unstructure

logger = logging.getLogger(__name__)

GOOGLE_OAUTH_CONFIG_DIR = Path("~/.config/google-auth-oauthlib").expanduser()
CLIENT_SECRET_FILENAME = "client_id.json"  # this allows the user to create a token
AUTHORIZED_TOKEN_FILENAME = "authorized_token"  # this caches token


class UploadError(Exception):
    pass


class GooglePhotosClient:
    def __init__(self) -> None:
        self._auth_token_path = GOOGLE_OAUTH_CONFIG_DIR / AUTHORIZED_TOKEN_FILENAME
        self._base_url = "https://photoslibrary.googleapis.com"
        self._scopes = [
            "https://www.googleapis.com/auth/photoslibrary",
            "https://www.googleapis.com/auth/photoslibrary.sharing",
            "https://www.googleapis.com/auth/photoslibrary.readonly",
        ]

    def _load_cached_access_token(self) -> Optional[Credentials]:
        logger.info("Loading cached access token...")
        try:
            credentials = Credentials.from_authorized_user_file(
                filename=self._auth_token_path,
                scopes=self._scopes,
            )
            return credentials
        except OSError as err:
            logger.info(f"Error opening access token file - {err}")
        except ValueError:
            logger.info("Error loading access token - Incorrect format")

        return None

    def _get_new_credentials(self) -> Credentials:
        refresh_token_path = GOOGLE_OAUTH_CONFIG_DIR / CLIENT_SECRET_FILENAME
        logger.info("Loading refresh token...")
        if not refresh_token_path.exists():
            raise FileNotFoundError(
                (
                    f"{refresh_token_path.absolute()} file does not exist\n\n"
                    "Please check the README to create one."
                )
            )

        refresh_token_path_as_str = str(refresh_token_path.absolute())

        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=refresh_token_path_as_str,
            scopes=self._scopes,
        )

        logger.info("Starting OAuth flow to get access token...")
        credentials = flow.run_local_server(
            host="localhost",
            port=8080,
            authorization_prompt_message="",
            success_message="The auth flow is complete; you may close this window.",
            open_browser=True,
        )

        try:
            logger.info("Saving new credentials...")
            _save_access_token(credentials, self._auth_token_path)
        except OSError as err:
            logger.info(f"Could not save auth tokens - {err}")

        return credentials

    def start_session(self) -> None:
        credentials = self._load_cached_access_token()

        if not credentials:
            logger.info("No cached access token found")
            credentials = self._get_new_credentials()
        # TODO: the credentials.expiry time is always wrong... but no idea how
        # to check offline that the credentials are expired

        session = AuthorizedSession(credentials)

        self._session = session

    def _get(self, path: str, **kwargs: Any) -> JsonDict:
        if not self._session:
            self.start_session()

        url = f"{self._base_url}{path}"
        logger.info(f"GET {url}")
        response = self._session.get(url, **kwargs)

        response.raise_for_status()

        return response.json()

    def _post(self, path: str, **kwargs: Any) -> JsonDict:
        if not self._session:
            self.start_session()

        if "body" in kwargs:
            body = kwargs.pop("body")
            kwargs.update({"data": json.dumps(body)})
        url = f"{self._base_url}{path}"
        logger.info(f"POST {url}")
        response = self._session.post(url, **kwargs)

        response.raise_for_status()

        return response.json()

    def get_all_media_items(self) -> Iterator[MediaItem]:
        # https://developers.google.com/photos/library/reference/rest/v1/mediaItems/list#query-parameters  # noqa
        max_page_size = 100
        params = {"pageSize": max_page_size}
        data = self._get("/v1/mediaItems", params=params)
        if not data:
            return  # TODO: is this correct? or I should raise StopIteration? or return iter([])?

        media_items = map(parse_media_item, data["mediaItems"])
        yield from media_items
        pagination_token = data.get("nextPageToken")

        while pagination_token:
            params.update({"pageToken": data["nextPageToken"]})
            data = self._get("/v1/mediaItems", params=params)
            if not data:
                logger.warning("No data received in the response")
                return

            pagination_token = data.get("nextPageToken")

            media_items = map(parse_media_item, data["mediaItems"])
            yield from media_items

    def search_media_items(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> Iterator[MediaItem]:
        # https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search  # noqa
        max_page_size = 100
        start_date = {"year": start.year, "month": start.month, "day": start.day}
        end_date = {"year": end.year, "month": end.month, "day": end.day}

        body = {
            "pageSize": max_page_size,
            "filters": {
                "dateFilter": {
                    "ranges": [
                        {"startDate": start_date, "endDate": end_date},
                    ]
                }
            },
        }

        data = self._post("/v1/mediaItems:search", body=body)
        if not data:
            return  # TODO: is this correct? or I should raise StopIteration? or return iter([])?

        tz = DEFAULT_TZ
        media_items = (parse_media_item(item, tz) for item in data["mediaItems"])
        yield from media_items

        pagination_token = data.get("nextPageToken")

        while pagination_token:
            body = {**body, "pageToken": pagination_token}
            logger.info("Getting next page...")
            data = self._post("/v1/mediaItems:search", body=body)
            if not data:
                logger.warning("No data received in the response")
                return

            pagination_token = data.get("nextPageToken")

            media_items = (parse_media_item(item, tz) for item in data["mediaItems"])
            yield from media_items


def parse_media_item(raw: JsonDict, tz: pytz.timezone) -> MediaItem:
    raw_media_metadata = raw["mediaMetadata"]
    creation_time = datetime.datetime.strptime(
        raw_media_metadata["creationTime"], "%Y-%m-%dT%H:%M:%SZ"
    )

    media_metadata = MediaMetadata(
        creation_time=tz.localize(creation_time),
        width=int(raw_media_metadata["width"]),
        height=int(raw_media_metadata["height"]),
        photo=raw_media_metadata.get("photo"),
    )

    media_item = MediaItem(
        id=raw["id"],
        product_url=raw["productUrl"],
        base_url=raw["baseUrl"],
        mime_type=raw["mimeType"],
        media_metadata=media_metadata,
        filename=raw["filename"],
    )

    return media_item


# def when_did_access_token_expire(credential: Credentials) -> timedelta:
#     delta = datetime.datetime.now() - credential.expiry

#     timedelta_chunds = []

#     matches = re.search(r"(\d+):(\d{2}):(\d{2}).(\d+)", str(delta))
#     h = int(matches.group(1))
#     if h:
#         timedelta_chunds.append(f"{h}h")

#     m = int(matches.group(2))
#     if m:
#         timedelta_chunds.append(f"{m}m")

#     s = int(matches.group(3))
#     ms = matches.group(4)[:2]
#     if s:
#         timedelta_chunds.append(f"{s}.{ms}s")

#     delta_str = " ".join(timedelta_chunds)

#     logger.info(f"Access token expired {delta_str} ago")
#     return delta


# def _authenticate(credentials: Path, scopes: List[Scope]) -> Credentials:
#     if not credentials.exists():
#         raise FileNotFoundError(
#             (
#                 f"{credentials.absolute()} file does not exist\n\n"
#                 "Please check the README to create one."
#             )
#         )

#     credentials_path_as_str = str(credentials.absolute())
#     flow = InstalledAppFlow.from_client_secrets_file(
#         credentials_path_as_str, scopes=scopes
#     )

#     credentials = flow.run_local_server(
#         host="localhost",
#         port=8080,
#         authorization_prompt_message="",
#         success_message="The auth flow is complete; you may close this window.",
#         open_browser=True,
#     )

#     return credentials


def _save_access_token(credentials: Credentials, auth_file: Path) -> None:
    credencials_as_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "id_token": credentials.id_token,
        "scopes": credentials.scopes,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
    }

    write_json(auth_file, credencials_as_dict)
    logger.info(f"Credentials cached to {auth_file}")


def read_media_items(path: Path) -> List[MediaItem]:
    data = read_json(path)
    media_items = structure(data, List[MediaItem])
    return media_items


def write_media_items(path: Path, media_items: List[MediaItem]) -> None:
    content = unstructure(media_items)

    logger.info(f"Writing media items to {path}")
    write_json(path=path, content=content)


# def _get_authorized_session(
#     auth_token_file: Optional[Path] = None,
# ) -> AuthorizedSession:
#     scopes: List[Scope] = [
#         "https://www.googleapis.com/auth/photoslibrary",
#         "https://www.googleapis.com/auth/photoslibrary.sharing",
#         "https://www.googleapis.com/auth/photoslibrary.readonly",
#     ]

#     credentials: Optional[Credentials] = None

#     # load cached credential files
#     if auth_token_file:
#         try:
#             credentials = Credentials.from_authorized_user_file(auth_token_file, scopes)
#         except OSError as err:
#             logger.info(f"Error opening auth token file - {err}")
#         except ValueError:
#             logger.info("Error loading auth tokens - Incorrect format")

#     # no cached credential found
#     if not credentials:
#         credentials_path = GOOGLE_OAUTH_CONFIG_DIR / CLIENT_SECRET_FILENAME
#         credentials = _authenticate(credentials_path, scopes)

#     # start session
#     session = AuthorizedSession(credentials)

#     if auth_token_file:
#         try:
#             _save_credentials(credentials, auth_token_file)
#         except OSError as err:
#             logger.info(f"Could not save auth tokens - {err}")

#     return session


def upload_media(session: AuthorizedSession, path: Path) -> None:
    data = path.read_bytes()

    session.headers["Content-type"] = "application/octet-stream"
    session.headers["X-Goog-Upload-Protocol"] = "raw"
    session.headers["X-Goog-Upload-File-Name"] = path.name

    logger.info(f"Uploading photo -- {path!r}")

    response = session.post("https://photoslibrary.googleapis.com/v1/uploads", data)

    if not (response.status_code == 200 and response.content):
        raise UploadError(f"Could not upload {path!r}. Server Response - {response}")

    create_body = json.dumps(
        {
            "albumId": None,
            "newMediaItems": [
                {
                    "description": "",
                    "simpleMediaItem": {"uploadToken": response.content.decode()},
                }
            ],
        },
        indent=4,
    )

    url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
    resp = session.post(url, create_body).json()

    logger.info(f"Server response: {resp}")

    if "newMediaItemResults" not in resp:
        err_msg = f"Could not add {path!r} to library. Server Response -- {resp}"
        raise UploadError(err_msg)

    status = resp["newMediaItemResults"][0]["status"]
    code = status.get("code")

    if code and code > 0:
        err_msg = f"Could not add {path!r} to library -- {status['message']}"
        raise UploadError(err_msg)

    logger.info(f"Added {path!r} to library and album")


def upload_photos(session: AuthorizedSession, photo_paths: List[Path]) -> None:
    pass
