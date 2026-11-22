"""Tests unitaires du bloc presse.

Le flux RSS est une source externe non contractuelle : ces tests vérifient
qu'aucune panne (timeout, XML invalide, flux vide) ne peut faire échouer la
route. Ils sont hors ligne : ``httpx.get`` et le cache sont remplacés.
"""

import httpx
import pytest

from app.services import football_service

VALID_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>RMC Sport</title>
    <item>
      <title>Le PSG &lt;b&gt;s'impose&lt;/b&gt; face a Lyon</title>
      <link>https://example.test/article-1</link>
      <pubDate>Sun, 22 Nov 2026 19:21:11 GMT</pubDate>
    </item>
    <item>
      <title>Sans lien valide</title>
      <link>javascript:alert(1)</link>
      <pubDate>Sun, 22 Nov 2026 18:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Titre sans date</title>
      <link>https://example.test/article-2</link>
    </item>
  </channel>
</rss>
"""


class FakeResponse:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "boom", request=httpx.Request("GET", "https://example.test"), response=self
            )


@pytest.fixture(autouse=True)
def clear_press_cache():
    football_service._PRESS_CACHE = None
    yield
    football_service._PRESS_CACHE = None


def test_press_parses_title_link_and_date(monkeypatch):
    monkeypatch.setattr(
        football_service.httpx, "get", lambda *args, **kwargs: FakeResponse(VALID_FEED)
    )

    payload = football_service.get_press(limit=5)

    assert payload["available"] is True
    assert payload["source"]["name"] == "RMC Sport"
    assert len(payload["items"]) == 2, "le lien non HTTP doit être écarté"
    first = payload["items"][0]
    assert first["title"] == "Le PSG s'impose face a Lyon", "les balises HTML sont retirées"
    assert first["link"] == "https://example.test/article-1"
    assert first["publishedAt"] == "2026-11-22T19:21:11Z"


def test_press_is_never_blocking_on_timeout(monkeypatch):
    def boom(*args, **kwargs):
        raise httpx.ConnectTimeout("timeout")

    monkeypatch.setattr(football_service.httpx, "get", boom)

    payload = football_service.get_press(limit=5)

    assert payload["available"] is False
    assert payload["items"] == []
    assert payload["source"]["url"]


def test_press_is_never_blocking_on_invalid_xml(monkeypatch):
    monkeypatch.setattr(
        football_service.httpx, "get", lambda *args, **kwargs: FakeResponse(b"<rss><channel>")
    )

    payload = football_service.get_press(limit=5)

    assert payload["available"] is False
    assert payload["items"] == []


def test_press_is_never_blocking_on_http_error(monkeypatch):
    monkeypatch.setattr(
        football_service.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse(b"nope", status_code=503),
    )

    payload = football_service.get_press(limit=5)

    assert payload["available"] is False
    assert payload["items"] == []


def test_press_titles_are_truncated(monkeypatch):
    long_title = "A" * 300
    feed = (
        b"<rss><channel><item><title>"
        + long_title.encode()
        + b"</title><link>https://example.test/long</link></item></channel></rss>"
    )
    monkeypatch.setattr(
        football_service.httpx, "get", lambda *args, **kwargs: FakeResponse(feed)
    )

    payload = football_service.get_press(limit=5)

    assert payload["available"] is True
    assert len(payload["items"][0]["title"]) == football_service.PRESS_MAX_TITLE


def test_press_respects_the_limit(monkeypatch):
    monkeypatch.setattr(
        football_service.httpx, "get", lambda *args, **kwargs: FakeResponse(VALID_FEED)
    )

    payload = football_service.get_press(limit=1)

    assert len(payload["items"]) == 1
