import os
import urllib.parse
import requests
import feedparser
from google import genai

CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_ai_news():
    # 検索キーワード（開発・エンジニアリング視点）
    query = (
        "(LLMアプリ OR RAG OR ファインチューニング OR LangChain OR LlamaIndex OR 「AI 開発」 OR 「AI 実装」) "
        "+(アーキテクチャ OR ライブラリ OR API OR プログラミング OR OSS) "
        "-ビジネス -投資 -株価 -導入事例 -DX -初心者"
    )
    
    # 日本語やスペースをURLで安全に送れる形式に自動変換
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    
    feed = feedparser.parse(rss_url)
    return feed.entries[:2]  # 上位2件に絞り込み

def generate_summary(title, link):
    # 最新のクライアント初期化
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = (
        f"以下の技術記事の見出しから、開発者向けに30文字程度の見出しと、"
        f"どのような技術や実装に関する記事なのかが分かる100文字程度の概要を日本語で作成してください。\n\n"
        f"タイトル: {title}"
    )
    
    # 【対策】最新SDKがサポートする「gemini-2.5-flash」を正しく指定
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
        print("開発視点の記事が見つかりませんでした。")
        return
        
    message = "🛠️ 【週刊】生成AI・LLM開発技術ニュースまとめ★\n\n"
    for art in articles:
        summary = generate_summary(art.title, art.link)
        message += f"■ {summary}\n🔗 URL: {art.link}\n-----------------------\n"
    
    send_to_cliq(message)

if __name__ == "__main__":
    main()
