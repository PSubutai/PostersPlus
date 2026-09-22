"""Key-less configurator search: Cinemeta stands in for TMDB's search, the
TMDB id is resolved on selection, and a verbatim {tmdb_id} placeholder is
read as absent so an IMDb id alone renders."""
import asyncio
import unittest
from unittest import mock

import main
import cinemeta


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload
    def json(self):
        return self._payload


class CinemetaSearchTests(unittest.TestCase):
    def test_rows_are_tmdb_shaped_and_interleaved(self):
        async def fake_get(url, **_):
            if "/catalog/movie/" in url:
                return _Resp(200, {"metas": [
                    {"id": "tt1", "imdb_id": "tt1", "type": "movie", "name": "A", "releaseInfo": "2019", "poster": "https://x/a.jpg"},
                    {"id": "tt3", "type": "movie", "name": "C", "releaseInfo": "2001–"},
                    {"id": "notimdb", "type": "movie", "name": "junk"},
                ]})
            return _Resp(200, {"metas": [
                {"id": "tt2", "imdb_id": "tt2", "type": "series", "name": "B", "releaseInfo": "2022"},
            ]})
        client = mock.Mock(); client.get = fake_get
        rows = asyncio.run(cinemeta.search(client, "q"))
        self.assertEqual([r["imdb_id"] for r in rows], ["tt1", "tt2", "tt3"])
        self.assertEqual(rows[0]["media_type"], "movie")
        self.assertEqual(rows[0]["title"], "A")
        self.assertEqual(rows[0]["release_date"], "2019-01-01")
        self.assertEqual(rows[0]["poster_url"], "https://x/a.jpg")
        self.assertIsNone(rows[0]["id"])
        self.assertEqual(rows[1]["media_type"], "tv")
        self.assertEqual(rows[1]["name"], "B")
        self.assertEqual(rows[1]["first_air_date"], "2022-01-01")
        self.assertEqual(rows[2]["release_date"], "2001-01-01")

    def test_a_failed_catalogue_is_just_empty(self):
        async def fake_get(url, **_):
            if "/catalog/movie/" in url:
                raise RuntimeError("boom")
            return _Resp(503, {})
        client = mock.Mock(); client.get = fake_get
        self.assertEqual(asyncio.run(cinemeta.search(client, "q")), [])
        self.assertEqual(asyncio.run(cinemeta.search(client, "  ")), [])


class PlaceholderTests(unittest.TestCase):
    def test_tmdb_id_placeholder_reads_as_absent(self):
        for literal in ("{tmdb_id}", "{tmdb_id?}", " {tmdb_id} "):
            self.assertEqual(main._normalise_optional_id(literal, "tmdb_id"), "")
        self.assertEqual(main._normalise_optional_id("496243", "tmdb_id"), "496243")
        self.assertEqual(main._normalise_optional_id("{imdb_id}", "tmdb_id"), "{imdb_id}")
        src = open("main.py", encoding="utf-8").read()
        self.assertEqual(src.count('_normalise_optional_id(tmdb_id, "tmdb_id")'), 2)


class ConfiguratorKeylessTests(unittest.TestCase):
    def test_search_and_preview_no_longer_require_a_key(self):
        html = open("configurator.html", encoding="utf-8").read()
        self.assertNotIn("Enter your TMDB API key above to search", html)
        self.assertIn("async function fetchTmdbId(", html)
        self.assertIn("if (tmdbId) params.set('tmdb_id', tmdbId);", html)
        self.assertIn("if (resolvedTmdbId || resolvedImdbId) loadPreview();", html)
        self.assertIn("if (!data.tmdbId && !data.imdbId) return;", html)


if __name__ == "__main__":
    unittest.main()
