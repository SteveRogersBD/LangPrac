from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

def video_id_from_url(url: str) -> str:
    p = urlparse(url)

    # https://www.youtube.com/watch?v=VIDEO_ID
    if p.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        qs = parse_qs(p.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]

    # https://youtu.be/VIDEO_ID
    if p.hostname == "youtu.be":
        vid = p.path.strip("/").split("/")[0]
        if vid:
            return vid

    raise ValueError("couldn't extract video id from url")

def get_transcript(url: str):
    video_id = video_id_from_url(url)
    ytt = YouTubeTranscriptApi()
    fetched = ytt.fetch(video_id)  # NEW API :contentReference[oaicite:1]{index=1}
    return fetched.to_raw_data()   # list[{"text","start","duration"}, ...] :contentReference[oaicite:2]{index=2}

if __name__ == "__main__":
    link = "https://www.youtube.com/watch?v=g2aPWWwC-jo"
    transcript = get_transcript(link)
    print(transcript[:3])
