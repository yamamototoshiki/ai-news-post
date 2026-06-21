import os
import requests
import feedparser
from google import genai

CLIQ_WEBHOOK_URL = os.environ.get("CLIQ_WEBHOOK_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def main():
    # 1. Zenn（AIトピック）から記事を取得
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
        
        # ─── プロンプトの修正：余計な説明文言を出力させないように「出力例」を指定 ───
        prompt = (
            f"以下の技術ブログのタイトルから、【30文字程度の見出し】と【100文字程度の概要】を日本語で作成してください。\n"
            f"注意：出力は、余計なラベル（「見出し：」「概要：」など）や記号（■、*、#）を含めず、必ず以下の形式のみで出力してください。\n\n"
            f"--- 出力形式 ---\n"
            f"作成した見出しをここに記述\n"
            f"作成した概要文をここに記述\n"
            f"----------------\n\n"
            f"タイトル: {clean_title}"
        )
        
        try:
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            # 行ごとに分割して「見出し」と「概要」を切り出す
            lines = [line.strip() for line in res.text.strip().split('\n') if line.strip()]
            
            if len(lines) >= 2:
                gemini_title = lines[0]
                gemini_summary = lines[1]
            else:
                gemini_title = clean_title
                gemini_summary = res.text
                
        except Exception as e:
            gemini_title = f"（要約エラー）{clean_title}"
            gemini_summary = "データの取得に失敗しました。"
        
        # ─── Cliqの装飾修正：見出しを大きくし、下線風の区切り線を入れ、不要な記号を削除 ───
        # 「###」で文字サイズを大きくし、直後にハイフン3つ「---」を入れることで下線（区切り線）を表現します
        message += f"### *{gemini_title}*\n---\n{gemini_summary}\n🔗 URL: {art.link}\n\n\n"
    
    # 3. Zoho Cliqへ送信
    headers_cliq = {"Content-Type": "application/json; charset=utf-8"}
    requests.post(CLIQ_WEBHOOK_URL, json={"text": message}, headers=headers_cliq)

if __name__ == "__main__":
    main()
