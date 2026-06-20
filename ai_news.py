import os
import requests
import feedparser
from google import genai

# GitHub Secretsから安全に値を読み込む設定に変更
CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_ai_news():
#    rss_url = "https://news.google.com/rss/search?q=生成AI+when:7d&hl=ja&gl=JP&ceid=JP:ja"
   「生成AI」「LLM」「機械学習」などの技術系ワードかつ「開発、論文、オープンソース」等を含む、ただし「株価、投資」は除外
    rss_url = "https://news.google.com/rss/search?q=(生成AI+OR+LLM+OR+機械学習+OR+オープンソース)+(開発+OR+論文+OR+モデル)+-株価+-投資&hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(rss_url)
    return feed.entries[:2]

#def get_ai_news():
#    # ITmedia AI+のフィードを直接読み込む
#    rss_url = "https://rss.itmedia.co.jp/rss/core/aiplus.xml"
#    feed = feedparser.parse(rss_url)
#    return feed.entries[:2]  # 上位2件に絞り込み

def generate_summary(title, link):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"以下のニュース記事の見出しから、30文字程度の見出しと、100文字程度の概要を日本語で作成してください。\n\nタイトル: {title}"
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text

def send_to_cliq(text):
    payload = {"text": text}
    requests.post(CLIQ_WEBHOOK_URL, json=payload)

def main():
    articles = get_ai_news()
    if not articles: return
    message = "★【週刊】生成AIニュースまとめ★\n\n"
    for art in articles:
        summary = generate_summary(art.title, art.link)
        message += f"■ {summary}\n🔗 URL: {art.link}\n-----------------------\n"
    send_to_cliq(message)

if __name__ == "__main__":
    main()
