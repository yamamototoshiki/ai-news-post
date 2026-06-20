import os
import requests
import feedparser
from google import genai

CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_ai_news():
    # ─── ニュース取得先を「Ledge.ai」の公式フィードに変更 ───
    rss_url = "https://ledge.ai/feed/"
    
    # クラウドからのアクセスブロックを回避する対策
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.text)
    except Exception as e:
        print(f"[DEBUG] RSS取得時に通信エラーが発生しました: {e}")
        return []
    
    print(f"[DEBUG] Ledge.aiのRSSから取得した記事数: {len(feed.entries)} 件")
    return feed.entries[:2]  # 最新記事の上位2件に絞り込み

def generate_summary(title, link):
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Ledge.aiの記事であることを意識したプロンプト
    prompt = (
        f"以下のLedge.aiのAI関連記事の見出しから、開発者向けに30文字程度の見出しと、"
        f"どのような技術トレンドや実装に関する記事なのかが分かる100文字程度の概要を日本語で作成してください。\n\n"
        f"タイトル: {title}"
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    return response.text

def send_to_cliq(text):
    payload = {"text": text}
    print(f"[DEBUG] Cliqへ送信を試みます。URLの長さ: {len(CLIQ_WEBHOOK_URL) if CLIQ_WEBHOOK_URL else 0}")
    
    response = requests.post(CLIQ_WEBHOOK_URL, json=payload)
    
    print(f"[DEBUG] Cliqからのレスポンスコード: {response.status_code}")
    print(f"[DEBUG] Cliqからの返答内容: {response.text}")

def main():
    print(f"[DEBUG] CLIQ_WEBHOOK_URLが設定されているか: {bool(CLIQ_WEBHOOK_URL)}")
    print(f"[DEBUG] GEMINI_API_KEYが設定されているか: {bool(GEMINI_API_KEY)}")

    articles = get_ai_news()
    if not articles: 
        print("[DEBUG] 記事が0件だったため、ここで処理を終了しました。")
        return
        
    message = "💡 【週刊】Ledge.ai 最新AIニュースまとめ★\n\n"
    for art in articles:
        print(f"[DEBUG] 記事の要約を開始: {art.title[:15]}...")
        summary = generate_summary(art.title, art.link)
        message += f"■ {summary}\n🔗 URL: {art.link}\n-----------------------\n"
    
    send_to_cliq(message)
    print("[DEBUG] すべての処理が完了しました。")

if __name__ == "__main__":
    main()
