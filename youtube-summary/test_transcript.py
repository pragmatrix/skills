"""Pins the rules transcript.py relies on. Run: python3 -m unittest test_transcript (in this folder)."""
import unittest

import transcript


def tracks(*codes):
    return [{"languageCode": code} for code in codes]


class VideoIdTest(unittest.TestCase):
    def test_url_forms(self):
        for url in (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ&t=10s",
            "https://youtu.be/dQw4w9WgXcQ?si=abc",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/live/dQw4w9WgXcQ",
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            "dQw4w9WgXcQ",
        ):
            self.assertEqual(transcript.video_id(url), "dQw4w9WgXcQ", url)

    def test_rejects_other_urls(self):
        with self.assertRaises(transcript.TranscriptError):
            transcript.video_id("https://example.com/watch?v=dQw4w9WgXcQ")


class PickTrackTest(unittest.TestCase):
    def pick(self, *codes):
        return transcript.pick_track(tracks(*codes), "en")["languageCode"]

    def test_exact_language_beats_regional_variant(self):
        self.assertEqual(self.pick("de", "en-US", "en"), "en")

    def test_regional_variant_beats_other_languages(self):
        self.assertEqual(self.pick("de", "en-GB"), "en-GB")

    def test_falls_back_to_first_track(self):
        self.assertEqual(self.pick("de", "fr"), "de")

    def test_no_tracks(self):
        self.assertIsNone(transcript.pick_track([], "en"))


class CaptionTextTest(unittest.TestCase):
    def test_double_escaped_entities_and_both_formats(self):
        classic = '<transcript><text start="0" dur="1">it&amp;#39;s</text><text start="1" dur="1"> ok </text></transcript>'
        format3 = '<timedtext><body><p t="0" d="1"><s>it&amp;#39;s</s></p><p t="1" d="1">ok</p></body></timedtext>'
        self.assertEqual(transcript.caption_text(classic), "it's ok")
        self.assertEqual(transcript.caption_text(format3), "it's ok")
