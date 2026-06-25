import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# 1. 网页头部设计
st.set_page_config(page_title="AI预测系统", page_icon="🔮", layout="wide")
st.title("🔮 我的专属 AI 智能实盘预测系统")
st.markdown("---")

# 2. 侧边栏交互组件
st.sidebar.header("🛠️ 策略参数设置")
ticker = st.sidebar.text_input("请输入美股代码 (如 TSLA, AAPL, NVDA, SPY):", "SPY")
start_date = st.sidebar.date_input("选择历史数据起点:", pd.to_datetime("2021-01-01"))
st.sidebar.markdown("---")

# 3. 核心点击运行逻辑
if st.sidebar.button("🚀 开始 AI 分析并预测明天"):
    with st.spinner('正在从全球行情服务器抓取数据并训练 AI 模型...'):
        try:
            # 下载数据
            data = yf.download(ticker, start=start_date)
            if data.empty:
                st.error("❌ 未抓取到数据，请检查股票代码是否输入正确（需使用美股标准代码，如 AAPL）。")
            else:
                if isinstance(data.columns, pd.MultiIndex): 
                    data.columns = data.columns.get_level_values(0)

                # 计算指标
                data['MA5'] = data['Close'].rolling(window=5).mean()
                data['MA20'] = data['Close'].rolling(window=20).mean()
                data['Return'] = data['Close'].pct_change()

                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-9)
                data['RSI'] = 100 - (100 / (1 + rs))

                data['Target'] = np.where(data['Close'].shift(-1) > data['Close'], 1, 0)
                data = data.dropna()

                # 训练模型
                features = ['Close', 'MA5', 'MA20', 'Return', 'RSI']
                X = data[features]
                y = data['Target']
                split = int(len(data) * 0.8)

                model = RandomForestClassifier(n_estimators=100, random_state=42)
                model.fit(X.iloc[:split], y.iloc[:split])

                # 回测计算
                data['AI_Signal'] = 0
                data.iloc[split:, data.columns.get_loc('AI_Signal')] = model.predict(X.iloc[split:])
                data['Strategy_Return'] = data['AI_Signal'].shift(1) * data['Return']
                data['Strategy_Return'] = data['Strategy_Return'].fillna(0)

                data['Market_Wealth'] = (1 + data['Return'].iloc[split:]).cumprod()
                data['AI_Wealth'] = (1 + data['Strategy_Return'].iloc[split:]).cumprod()

                # 最新预测
                latest_data = X.iloc[[-1]]
                tomorrow_prediction = model.predict(latest_data)
                tomorrow_probability = model.predict_proba(latest_data)

                # 前端布局展示：分成左右两栏 (已修复新版 Streamlit 的兼容性错误)
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📢 最新实盘预测结果")
                    if tomorrow_prediction == 1:
                        st.success(f"📈 明天预测方向：【上涨】\n\n🎯 🔮 AI 信心指数: {tomorrow_probability[0][1]:.2%}")
                    else:
                        st.error(f"📉 明天预测方向：【下跌】\n\n🎯 🔮 AI 信心指数: {tomorrow_probability[0][0]:.2%}")

                    st.markdown("---")
                    st.subheader("📊 财富放大倍数对比")
                    st.metric("AI 策略最终财富", f"{data['AI_Wealth'].iloc[-1]:.2f} 倍")
                    st.metric("纯买入持有最终财富", f"{data['Market_Wealth'].iloc[-1]:.2f} 倍")

                with col2:
                    st.subheader("📉 资产增值收益对比曲线")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(data['Market_Wealth'].values, label='Buy & Hold (Market)', color='gray', linestyle='--')
                    ax.plot(data['AI_Wealth'].values, label='AI Trading Strategy', color='green', linewidth=2)
                    ax.set_xlabel("Trading Days")
                    ax.set_ylabel("Wealth Multiplier")
                    ax.legend()
                    ax.grid(True)
                    st.pyplot(fig)
        except Exception as e:
            st.error(f"运行出错啦: {e}")
