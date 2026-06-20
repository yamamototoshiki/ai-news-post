import os
import requests
import feedparser
from google import genai

CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_ai_news():
    rss_url = "https://rss.itmedia.co.jp/rss/core/aiplus.xml"
    feed = feedparser.parse(rss_url)
    
    # ログ出力：何件の記事が取得できたかを確認
    print(f"[DEBUG] RSSから取得した記事数: {len(feed.entries)} 件")
    
    return feed.entries[:2]

def generate_summary(title, link):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = (
        f"以下のITmediaのAI技術記事の見出しから、開発者向けに30文字程度の見出しと、"
        f"どのような技術やトレンドに関する記事なのかが分かる100文字程度の概要を日本語で作成してください。\n\n"
        f"タイトル: {title}"
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

def send_to_cliq(text):
    payload = {"text": text}
    # ログ出力：今から送信を試みるURL（セキュリティのため一部伏せ字）
    print(f"[DEBUG] Cliqへ送信を試みます。URLの長さ: {len(CLIQ_WEBHOOK_URL) if CLIQ_WEBHOOK_URL else 0}")
    
    response = requests.post(CLIQ_WEBHOOK_URL, json=payload)
    
    # ログ出力：Cliqのサーバーから返ってきた返事（200なら成功、400や404ならURL間違い）
    print(f"[DEBUG] Cliqからのレスポンスコード: {response.status_code}")
    print(f"[DEBUG] Cliqからの返答内容: {response.text}")

def main():
    # ログ出力：環境変数がちゃんと読み込めているか確認
    print(f"[DEBUG] CLIQ_WEBHOOK_URLが設定されているか: {bool(CLIQ_WEBHOOK_URL)}")
    print(f"[DEBUG] GEMINI_API_KEYが設定されているか: {bool(GEMINI_API_KEY)}")

    articles = get_ai_news()
    if not articles: 
        print("[DEBUG] 記事が0件だったため、ここで処理を終了しました。")
        return
        
    message = "📰 【週刊】ITmedia AI+ 技術ニュースまとめ★\n\n"
    for art in articles:
        print(f"[DEBUG] 記事の要約を開始: {art.title[:15]}...")
        summary = generate_summary(art.title, art.link)
        message += f"■ {summary}\n🔗 URL: {art.link}\n-----------------------\n"
    
    send_to_cliq(message)
    print("[DEBUG] すべての処理が完了しました。")

if __name__ == "__main__":
    main()
