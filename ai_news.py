import os
import requests
import feedparser
from google import genai

# 安全に認証情報を取得
CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def main():
    # 1. Ledge.aiから記事を取得（ブラウザのフリをしてアクセス）
    rss_url = "https://ledge.ai/feed/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(rss_url, headers=headers, timeout=10)
    feed = feedparser.parse(response.text)
    articles = feed.entries[:2] # 上位2件
    
    if not articles:
        return

    # 2. メッセージの作成とGeminiでの要約
    client = genai.Client(api_key=GEMINI_API_KEY)
    message = "💡 【週刊】Ledge.ai 最新AIニュースまとめ★\n\n"
    
    for art in articles:
        prompt = f"以下の記事タイトルから、30文字程度の見出しと、100文字程度の概要を日本語で作成してください。\n\nタイトル: {art.title}"
        res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        
        message += f"■ {res.text}\n🔗 URL: {art.link}\n-----------------------\n"
    
    # 3. Zoho Cliqへ送信
    requests.post(CLIQ_WEBHOOK_URL, json={"text": message})

if __name__ == "__main__":
    main()
