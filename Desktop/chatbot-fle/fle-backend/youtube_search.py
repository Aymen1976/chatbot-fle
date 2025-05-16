# ✅ youtube_search.py
from youtubesearchpython import VideosSearch

def search_youtube(query):
    try:
        search = VideosSearch(query, limit=3)
        results = search.result().get("result", [])

        video_links = []
        for video in results:
            title = video.get("title", "Vidéo sans titre")
            link = video.get("link", "")
            video_links.append(f"- [{title}]({link})")

        return video_links
    except Exception as e:
        print("❌ Erreur recherche YouTube :", e)
        return []
