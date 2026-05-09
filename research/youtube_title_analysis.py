import os
from typing import List
from googleapiclient.discovery import build

# AlbaAnalyzer import placeholder (update with actual import if found)
# from kloud.alba import AlbaAnalyzer

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def fetch_videos(channel_id: str, max_results: int = 25):
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set in environment.")
    yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    req = yt.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date"
    )
    res = req.execute()
    return res["items"]


def analyze_titles_with_alba(videos: List[dict]):
    titles = [v["snippet"]["title"] for v in videos]
    # Placeholder for AlbaAnalyzer usage
    # analysis = AlbaAnalyzer.analyze_titles(titles)
    analysis = {"titles": titles, "analysis": "(mocked)"}
    return analysis


def main():
    channel_id = "UCuCd7kgikh6CM2hAh5eAIMA"
    videos = fetch_videos(channel_id)
    analysis = analyze_titles_with_alba(videos)
    print(analysis)


if __name__ == "__main__":
    main()


