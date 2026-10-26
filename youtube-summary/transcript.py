#!/usr/bin/env python3
"""Download a YouTube video's transcript as plain text, without timestamps.

  transcript.py <youtube-url-or-video-id>

The transcript goes to $TMPDIR/youtube-<video-id>.txt, and the script prints that path.
The file starts with a header (title, channel, duration, URL), then a blank line, then
the transcript text wrapped at 100 columns.

The method is ported from the YTranscript Obsidian plugin
(https://github.com/lstrzepek/obsidian-yt-transcript, src/youtube/fetch.ts, MIT).
It asks YouTube's InnerTube player API for the caption tracks while posing as the iOS
app, because the caption URLs returned to that client work without proof-of-origin tokens.
"""
import html
import json
import os
import re
import sys
import tempfile
import textwrap
import urllib.request

# YouTube's public InnerTube API key, as used by YTranscript.
PLAYER_URL = "https://www.youtube.com/youtubei/v1/player?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
IOS_CLIENT = {"clientName": "IOS", "clientVersion": "20.10.38", "hl": "en", "gl": "US"}
IOS_USER_AGENT = "com.google.ios.youtube/20.10.38 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X)"
LANG = "en"

VIDEO_ID_PATTERNS = (
    re.compile(
        r"(?:(?:youtube|youtube-nocookie)\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|v/|live/)|youtu\.be/)"
        r"([a-zA-Z0-9_-]{11})"
    ),
    re.compile(r"^([a-zA-Z0-9_-]{11})$"),
)
# Caption XML comes in two formats. The classic one has <text start dur>, format 3 has <p t d>.
TEXT_TAG = re.compile(r"<text\s+start=\"[^\"]+\"\s+dur=\"[^\"]+\"[^>]*>(.*?)</text>", re.S)
P_TAG = re.compile(r"<p\s+t=\"\d+\"\s+d=\"\d+\"[^>]*>(.*?)</p>", re.S)
INNER_TAG = re.compile(r"<[^>]+>")


class TranscriptError(Exception):
    pass


def video_id(url):
    for pattern in VIDEO_ID_PATTERNS:
        match = pattern.search(url)
        if match:
            return match.group(1)
    raise TranscriptError(f"not a YouTube URL or video ID: {url}")


def pick_track(tracks, lang):
    """Prefer the exact language, then a regional variant of it, then its base language, then any track."""
    for matches in (
        lambda code: code == lang,
        lambda code: code.startswith(lang + "-"),
        lambda code: lang.startswith(code + "-"),
    ):
        for track in tracks:
            if matches(track["languageCode"]):
                return track
    return tracks[0] if tracks else None


def caption_text(xml):
    """Return the caption segments of a caption XML document as one string.

    Segment text is entity-encoded twice (an apostrophe arrives as &amp;#39;), so it is unescaped twice.
    """
    segments = TEXT_TAG.findall(xml) or P_TAG.findall(xml)
    texts = (html.unescape(html.unescape(INNER_TAG.sub("", s))).replace("\n", " ").strip() for s in segments)
    return " ".join(t for t in texts if t)


def request(url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def player_data(vid):
    body = {"context": {"client": IOS_CLIENT}, "videoId": vid}
    headers = {"Content-Type": "application/json", "User-Agent": IOS_USER_AGENT}
    data = json.loads(request(PLAYER_URL, body, headers))
    status = data.get("playabilityStatus", {})
    if status.get("status") in ("ERROR", "LOGIN_REQUIRED", "UNPLAYABLE"):
        raise TranscriptError(f"video not playable ({status['status']}): {status.get('reason', '')}")
    return data


def header(vid, details, track):
    seconds = int(details.get("lengthSeconds") or 0)
    duration = f"{seconds // 3600}:{seconds // 60 % 60:02}:{seconds % 60:02}"
    return "\n".join([
        f"Title: {details.get('title', 'Unknown')}",
        f"Channel: {details.get('author', 'Unknown')}",
        f"Duration: {duration}",
        f"Language: {track['languageCode']}",
        f"URL: https://www.youtube.com/watch?v={vid}",
    ])


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    try:
        vid = video_id(argv[0])
        data = player_data(vid)
        tracks = data.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
        track = pick_track(tracks, LANG)
        if track is None:
            raise TranscriptError("this video has no captions")
        text = caption_text(request(track["baseUrl"], headers={"Accept-Language": "en-US,en;q=0.9"}))
        if not text:
            raise TranscriptError(f"the {track['languageCode']} caption track is empty")
    except (TranscriptError, OSError, ValueError) as err:
        print(f"transcript.py: {err}", file=sys.stderr)
        return 1
    path = os.path.join(tempfile.gettempdir(), f"youtube-{vid}.txt")
    with open(path, "w", encoding="utf-8") as out:
        out.write(header(vid, data.get("videoDetails", {}), track) + "\n\n")
        out.write(textwrap.fill(text, width=100) + "\n")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
