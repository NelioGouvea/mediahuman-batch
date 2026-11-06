import yt_dlp

UNAVAILABLE_TITLES = {"[Private video]", "[Deleted video]"}

YDL_OPTIONS = {
    "extract_flat": "in_playlist",
    "skip_download": True,
    "quiet": True,
    "no_warnings": True,
}


def parse_input(raw_text):
    tokens = (token for token in raw_text.split() if token.startswith("http"))
    return list(dict.fromkeys(tokens))


def extract_video_urls(url):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = info.get("entries")
    if entries is None:
        return [info["webpage_url"]]

    return [
        entry["url"]
        for entry in entries
        if entry and entry.get("url") and entry.get("title") not in UNAVAILABLE_TITLES
    ]
