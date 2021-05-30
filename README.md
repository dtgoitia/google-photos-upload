## Usage

Update GSheet to reflect current state: `make refresh`
Reconcile: `make refresh`
  - apply changes to manually updated GSheet, aka: upload files marked to be uploaded

Find out what's already uploaded in GPhotos:
```shell
python -m gpy fetch_uploaded_media_info
```

Workflow:

  1. Copy files locally
  1. Convert videos to mp4 (`make convert_avi_files_to_mp4`)
  1. Add google metadata to pictures (`make add_metadata_to_pictures`) --> photos ready to be uploaded
  1. Estimate videos datetime (`make estimate_hardcoded_metadata_for_videos`)
  1. Add google metadata to videos (`make add_hardcoded_metadata_to_videos`) --> videos ready
    - this `touch`es videos with the UTC timestamp to later upload manually
  1. Upload media by pushing them to Android device (`make push_files_to_phone`)

## Quick start

Scan dates:

```shell
gpy scan date path/to/file/or/dir
```

<!--
Scan GPS coordinates:

```shell
gpy scan gps path/to/file/or/dir
```
-->

Edit file metadata

```shell
gpy meta file path/to/file/or/dir
```

## Install

Repository developed using Python 3.9.

```shell
make install
```

Assumption: `exiftool` is already installed.

## Obtaining a Google Photos API credentials

Enable _Google Photos API_ credentials:

1. Go to the [Google API Console][1] and select your project.
2. From the left menu, select _APIs & Services_ > _Library_.
3. Search for "Photos API" and click it.
4. Hit _Enable_.

Get credentials:

1. From the menu, select _APIs & Services_ > _Credentials_.
2. On the _Credentials_ page, click _Create Credentials_ > _OAuth client ID_.
3. Select _Desktop app_.

If this workflow is out of date, follow the [official steps][2].

Create a `client_id.json` file and replace the credentials bellow:

```json
{
  "installed": {
    "client_id":"YOUR_CLIENT_ID",
    "client_secret":"YOUR_CLIENT_SECRET",
    "auth_uri":"https://accounts.google.com/o/oauth2/auth",
    "token_uri":"https://www.googleapis.com/oauth2/v3/token",
    "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
  }
}
```

[1]: https://console.developers.google.com/apis/library "GCP Console"
[2]: https://developers.google.com/photos/library/guides/get-started "Google Photos APIs - Get started with REST"
