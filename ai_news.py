import os
import requests
import feedparser
from google import genai

CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_ai_news():
    # ─── ニュース取得先を「ITmedia AI+」の公式フィードに変更 ───
    rss_url = "https://rss.itmedia.co.jp/rss/core/aiplus.xml"
    
    feed = feedparser.parse(rss_url)
    return feed.entries[:2]  # 最新記事の上位2件に絞り込み

def generate_summary(title, link):
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # ITmediaの記事であることを明示したプロンプト
    prompt = (
        f"以下のITmediaのAI技術記事の見出しから、開発者向けに30文字程度の見出しと、"
        f"どのような技術やトレンドに関する記事なのかが分かる100文字程度の概要を日本語で作成してください。\n\n"
        f"タイトル: {title}"
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    return response.text

def send_to_cliq(text):
    payload = {"text": text}
    requests.post(CLIQ_WEBHOOK_URL, json=payload)

def main():
    articles = get_ai_news()
    if not articles: 
        print("ITmediaから記事を取得できませんでした。")
        return
        
    message = "📰 【週刊】ITmedia AI+ 技術ニュースまとめ★\n\n"
    for art in articles:
        summary = generate_summary(art.title, art.link)
        message += f"■ {summary}\n🔗 URL: {art.link}\n-----------------------\n"
    
    send_to_cliq(message)

if __name__ == "__main__":
    main()
