import os
import requests
import feedparser
from google import genai

CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def main():
    # 1. Ledge.aiから記事を取得（ブラウザのフリをしてアクセス）
    rss_url = "https://ledge.ai/feed/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(rss_url, headers=headers, timeout=10)
    # 文字化けや特殊文字によるバグを防ぐため、明示的にUTF-8で読み込む
    response.encoding = 'utf-8'
    
    feed = feedparser.parse(response.text)
    articles = feed.entries[:2]
    
    if not articles:
        print("記事が取得できませんでした。")
        return

    # 2. メッセージの作成とGeminiでの要約
    client = genai.Client(api_key=GEMINI_API_KEY)
    message = "💡 【週刊】Ledge.ai 最新AIニュースまとめ★\n\n"
    
    for art in articles:
        # タイトルに含まれるかもしれない特殊文字のバグを防ぐため、文字列を綺麗にする
        clean_title = str(art.title).strip().replace('\n', '').replace('\r', '')
        
        prompt = f"以下の記事タイトルから、開発者向けに30文字程度の見出しと、100文字程度の概要を日本語で作成してください。\n\nタイトル: {clean_title}"
        
        try:
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            summary_text = res.text
        except Exception as e:
            # 万が一Geminiがエラーを吐いた場合は、要約なしでタイトルだけにする安全弁
            summary_text = f"（要約エラー: {clean_title}）"
        
        message += f"■ {summary_text}\n🔗 URL: {art.link}\n-----------------------\n"
    
    # 3. Zoho Cliqへ送信（確実にJSONとして送るための記述）
    headers_cliq = {"Content-Type": "application/json; charset=utf-8"}
    requests.post(CLIQ_WEBHOOK_URL, json={"text": message}, headers=headers_cliq)

if __name__ == "__main__":
    main()
