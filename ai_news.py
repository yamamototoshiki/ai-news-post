import os
import requests
import feedparser
from google import genai

CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def main():
    # ─── 確実に取得できる「Zenn（AIトピック）」にソースを変更 ───
    rss_url = "https://zenn.dev/topics/ai/feed"
    
    response = requests.get(rss_url, timeout=10)
    response.encoding = 'utf-8'
    feed = feedparser.parse(response.text)
    articles = feed.entries[:2]
    
    if not articles:
        print("Zennから記事が取得できませんでした。")
        return

    # 2. メッセージの作成とGeminiでの要約
    client = genai.Client(api_key=GEMINI_API_KEY)
    message = "🛠️ 【週刊】Zenn 最新AI技術開発記事まとめ★\n\n"
    
    for art in articles:
        clean_title = str(art.title).strip().replace('\n', '').replace('\r', '')
        prompt = f"以下の技術ブログのタイトルから、開発者向けに30文字程度の見出しと、どのような実装やTipsに関する記事なのかが分かる100文字程度の概要を日本語で作成してください。\n\nタイトル: {clean_title}"
        
        try:
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            summary_text = res.text
        except Exception as e:
            summary_text = f"（要約エラー: {clean_title}）"
        
        message += f"■ {summary_text}\n🔗 URL: {art.link}\n-----------------------\n"
    
    # 3. Zoho Cliqへ送信
    headers_cliq = {"Content-Type": "application/json; charset=utf-8"}
    requests.post(CLIQ_WEBHOOK_URL, json={"text": message}, headers=headers_cliq)

if __name__ == "__main__":
    main()
