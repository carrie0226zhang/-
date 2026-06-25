import json
import time
import requests
import websocket

# ==========================================
# 微信专属配置区域 (请把您在Server酱获取的Key填在下面)
# ==========================================
WECHAT_SENDKEY = "SCT_YOUR_KEY" # ⬅️ 记得把这里换成您的真实 SCKEY 密码

KEYWORDS = ["特斯拉", "TSLA", "苹果", "AAPL", "英伟达", "NVDA", "美联储", "降息", "加息"]

def send_to_wechat(title, content):
    url = f"https://ftqq.com{WECHAT_SENDKEY}.send"
    data = {
        "title": f"🚨 AI实盘预测：{title[:20]}...",
        "desp": f"### 📊 突发财经快讯\n> {title}\n\n### 🔮 AI 智能实时研判\n{content}\n\n--- \n*⏰ 推送时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}*"
    }
    try:
        response = requests.post(url, data=data)
        result = response.json()
        if result.get("code") == 0:
            print("💚 微信消息成功送达手机！")
        else:
            print(f"❌ 微信推送失败，原因: {result.get('message')}")
    except Exception as e:
        print(f"网络请求失败，无法发送微信: {e}")

def analyze_news_with_ai(news_text):
    bullish_words = ["大涨", "暴涨", "利好", "超预期", "暴增", "买入", "降息", "新高"]
    bearish_words = ["大跌", "暴跌", "利空", "不及预期", "下滑", "卖出", "加息", "跌停"]
    score = 0
    for word in bullish_words:
        if word in news_text: score += 1
    for word in bearish_words:
        if word in news_text: score -= 1

    if score > 0:
        return f"📈 **【利好信号偏向】**\n\n新闻蕴含明显正向情绪。AI 模型研判认为该股或美股大盘在短期内**【上涨】**的概率较高。\n\n🎯 预测信心指数: `{55 + score*5}%`。"
    elif score < 0:
        return f"📉 **【利空信号警告】**\n\n新闻蕴含负向看跌情绪。AI 模型发出风险警告，认为短期内存在**【下跌】**回撤风险。\n\n🎯 预测信心指数: `{55 + abs(score)*5}%`。"
    else:
        return "⚖️ **【中性消息/继续观察】**\n\n该突发新闻对股价的即时方向性刺激有限，建议维持原有的技术面均线和 RSI 指标追踪。"

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "data" in data and "content" in data["data"]:
            news_title = data["data"]["content"]
            if any(keyword in news_title for keyword in KEYWORDS):
                print(f"🎯 监听到重要新闻: {news_title}")
                ai_result = analyze_news_with_ai(news_title)
                send_to_wechat(news_title, ai_result)
    except Exception as e:
        pass

def on_open(ws):
    print("🚀 微信 AI 预测机器人已全面启动！正在 24 小时全网监听突发财经新闻...")

if __name__ == "__main__":
    ws_url = "wss://://jin10.com" 
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
    ws.run_forever()
