import datetime

from gpy.gphotos import MediaItem, MediaMetadata, parse_media_item


def test_parse_media_item():
    raw_media_item = {
        "id": "media item id",
        "productUrl": "https://photos.google.com/lr/photo/media item id",
        "baseUrl": "base_url URL",
        "mimeType": "image/jpeg",
        "mediaMetadata": {
            "creationTime": "2004-04-29T13:25:43Z",
            "width": "2048",
            "height": "1536",
            "photo": {
                "cameraMake": "BENQ ",
                "cameraModel": "BENQ DC2300",
                "focalLength": 5.6,
                "apertureFNumber": 3.5,
                "isoEquivalent": 100,
                "exposureTime": "0.011111111s",
            },
        },
        "filename": "Alex y Bocata.JPG",
    }

    media_item = parse_media_item(raw_media_item)

    assert media_item == MediaItem(
        id="media item id",
        product_url="https://photos.google.com/lr/photo/media item id",
        base_url="base_url URL",
        mime_type="image/jpeg",
        media_metadata=MediaMetadata(
            creation_time=datetime.datetime(2004, 4, 29, 13, 25, 43),
            width=2048,
            height=1536,
            photo={
                "cameraMake": "BENQ ",
                "cameraModel": "BENQ DC2300",
                "focalLength": 5.6,
                "apertureFNumber": 3.5,
                "isoEquivalent": 100,
                "exposureTime": "0.011111111s",
            },
        ),
        filename="Alex y Bocata.JPG",
    )
