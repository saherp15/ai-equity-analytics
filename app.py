import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="AI Equity Analytics Platform",
    page_icon="📈",
    layout="wide"
)

# ==========================
# FILE UPLOAD
# ==========================

uploaded_file = st.file_uploader(
    "Upload Market Data CSV",
    type=["csv"]
)

if uploaded_file is not None:

    # Load Data
    df = pd.read_csv(uploaded_file)

    # Convert Date Column
    df["Date"] = pd.to_datetime(df["Date"])

    # Sidebar Navigation
    page = st.sidebar.radio(
        "Overview",
        [
            "Market Overview",
            "Stock Explorer",
            "Top Movers",
            "Top Volume Stocks",
            "Advanced Analytics",
            "Portfolio Simulator",
            "AI Assistant"
        ]
    )

    # ==========================
    # MARKET OVERVIEW
    # ==========================

    if page == "Market Overview":

        st.title("📊 Market Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Stocks",
                df["Ticker"].nunique()
            )

        with col2:
            st.metric(
                "Latest Trading Date",
                df["Date"].max().strftime("%d-%b-%Y")
            )

        with col3:
            st.metric(
                "Avg Daily Return %",
                round(df["Daily_Return_Pct"].mean(), 2)
            )

        with col4:
            st.metric(
                "Avg Volatility",
                round(df["Volatility_20D"].mean(), 2)
            )

        st.divider()

        # Volatility Chart
        st.subheader("📈 Top 10 Most Volatile Stocks")

        volatility_df = (
            df.groupby("Ticker")["Volatility_20D"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .sort_values(ascending=True)
            .reset_index()
        )

        fig = px.bar(
            volatility_df,
            x="Volatility_20D",
            y="Ticker",
            orientation="h",
            text="Volatility_20D",
            title="Top 10 Most Volatile Stocks"
        )

        fig.update_traces(
            texttemplate="%{x:.2f}",
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="volatility_chart"
        )

        st.divider()

        # Volume Chart
        st.subheader("📦 Top 10 Highest Average Volume Stocks")

        volume_df = (
            df.groupby("Ticker")["Volume"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        volume_df["Volume_M"] = (
            volume_df["Volume"] / 1_000_000
        )

        fig2 = px.bar(
            volume_df,
            x="Ticker",
            y="Volume_M",
            text="Volume_M",
            title="Highest Average Volume Stocks"
        )

        fig2.update_traces(
            texttemplate="%{y:.1f}M",
            textposition="outside"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            key="volume_overview_chart"
        )

    # ==========================
    # STOCK EXPLORER
    # ==========================

    elif page == "Stock Explorer":

        st.title("📈 Stock Explorer")

        selected_stock = st.selectbox(
            "Select Stock",
            sorted(df["Ticker"].unique())
        )

        stock_df = (
            df[df["Ticker"] == selected_stock]
            .sort_values("Date")
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Latest Price",
                f"₹{stock_df['Close'].iloc[-1]:.2f}"
            )

        with col2:
            st.metric(
                "Average Volume",
                f"{stock_df['Volume'].mean():,.0f}"
            )

        with col3:
            st.metric(
                "Average Return %",
                f"{stock_df['Daily_Return_Pct'].mean():.2f}%"
            )

        st.divider()

        st.subheader("📈 Closing Price Trend")

        fig = px.line(
            stock_df,
            x="Date",
            y="Close",
            markers=True,
            title=f"{selected_stock} Closing Price"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="stock_price_chart"
        )

        st.divider()

        st.subheader("📦 Volume Trend")

        fig2 = px.bar(
            stock_df,
            x="Date",
            y="Volume",
            title=f"{selected_stock} Trading Volume"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            key="stock_volume_chart"
        )

    # ==========================
    # TOP MOVERS
    # ==========================

    elif page == "Top Movers":

        st.title("🏆 Top Movers")

        movers = (
            df.groupby("Ticker")["Daily_Return_Pct"]
            .mean()
            .reset_index()
        )

        # FIX 1: gainers sorted descending, losers sorted ascending
        gainers = (
            movers.sort_values(
                "Daily_Return_Pct",
                ascending=False
            )
            .head(10)
        )

        losers = (
            movers.sort_values(
                "Daily_Return_Pct",
                ascending=True  # ✅ Fixed: was ascending=False (same as gainers)
            )
            .head(10)
        )

        # FIX 2: removed * 100 (Daily_Return_Pct is already a percentage)
        gainers = gainers.copy()
        losers = losers.copy()

        gainers["Daily_Return_Pct"] = gainers["Daily_Return_Pct"].round(2)
        losers["Daily_Return_Pct"] = losers["Daily_Return_Pct"].round(2)

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🚀 Top Gainers")

            fig = px.bar(
                gainers,
                x="Daily_Return_Pct",
                y="Ticker",
                orientation="h",
                text="Daily_Return_Pct"
            )
            fig.update_traces(
                texttemplate="%{x:.2f}%",
                textposition="outside",
                  cliponaxis=False
            )
            fig.update_layout(
                xaxis_range=[0, gainers["Daily_Return_Pct"].max() * 1.3]
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key="gainers_chart"
            )

        with col2:

            st.subheader("📉 Top Losers")

            fig2 = px.bar(
                losers,
                x="Daily_Return_Pct",
                y="Ticker",
                orientation="h",
                text="Daily_Return_Pct"
            )
            fig2.update_traces(
                texttemplate="%{x:.2f}%",
                textposition="outside",
              
            )
            fig2.update_layout(
                xaxis_range=[
                    losers["Daily_Return_Pct"].min() * 1.3,
                    0
                ]
            )
            fig2.update_yaxes(autorange="reversed")

            st.plotly_chart(
                fig2,
                use_container_width=True,
                key="losers_chart"
            )

    # ==========================
    # Top Volume Stocks
    # ==========================

    elif page == "Top Volume Stocks":

        st.title("Top Volume Stocks")

        top_volume = (
            df.groupby("Ticker")["Volume"]
            .mean()
            .sort_values(ascending=True)
            .head(15)
            .reset_index()
        )

        top_volume["Volume_M"] = (
            top_volume["Volume"] / 1_000_000
        )

        fig = px.bar(
            top_volume,
            x="Volume_M",
            y="Ticker",
            orientation="h",
            text="Volume_M",
            title="Top Volume Stocks"
        )
        fig.update_traces(
            texttemplate="%{x:.1f}M",
            textposition="outside"
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="top_volume_chart"
        )

    # ==========================
    # Advanced Analytics
    # ==========================

    elif page == "Advanced Analytics":

        st.title("Advanced Analytics")
        st.subheader("⚖️ Risk vs Return Analysis")

        # Calculate risk (standard deviation of daily returns) and return (mean daily return)
        risk_return = (
            df.groupby("Ticker")["Daily_Return_Pct"]
            .agg(["std", "mean"])
            .reset_index()
        )
        risk_return.columns = ["Ticker", "Risk", "Return"]

        # Create scatter plot
        fig = px.scatter(
            risk_return,
            x="Risk",
            y="Return",
            color="Ticker",
            title="Risk vs Return"
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="risk_return_chart"
        )
        st.divider()
        

        st.subheader("🔥 Correlation Heatmap")

        # Create price matrix
        price_data = df.pivot_table(
            index="Date",
            columns="Ticker",
            values="Close"
        )

        # Correlation matrix
        corr_matrix = price_data.corr()

        # Heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=False,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Stock Correlation Matrix"
        )

        fig.update_layout(
            height=800,
            xaxis_title="Stocks",
            yaxis_title="Stocks"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    elif page == "Portfolio Simulator":

        st.title("💼 Portfolio Simulator")

        investment = st.number_input(
            "Investment Amount (₹)",
            min_value=1000,
            value=100000
        )

        selected_stocks = st.multiselect(
            "Select Stocks",
            sorted(df["Ticker"].unique()),
            default=sorted(df["Ticker"].unique())[:3]
        )

        if len(selected_stocks) > 0:

            portfolio_df = (
                df[df["Ticker"].isin(selected_stocks)]
                .groupby("Ticker")
                .agg({
                    "Close": "last",
                    "Daily_Return_Pct": "mean"
                })
                .reset_index()
            )

            portfolio_df["Weight"] = (
                100 / len(selected_stocks)
            )

            portfolio_df["Investment"] = (
                investment / len(selected_stocks)
            )

            portfolio_df["Expected Return"] = (
                portfolio_df["Investment"]
                * portfolio_df["Daily_Return_Pct"]
                / 100
            )

            st.subheader("Portfolio Allocation")

            st.dataframe(portfolio_df)

            total_return = portfolio_df[
                "Expected Return"
            ].sum()

            st.metric(
                "Expected Daily Portfolio Return",
                f"₹{total_return:,.0f}"
            )

            fig = px.pie(
                portfolio_df,
                names="Ticker",
                values="Investment",
                title="Portfolio Allocation"
            )

            st.plotly_chart(
                fig,
                
                use_container_width=True
            )
    elif page == "AI Assistant":
        
        st.title("🤖 AI Market Assistant")
        st.info("""
            Try asking:

            • Which stock has the highest volatility?
            • Which stock has the highest average return?
            • Compare HINDALCO and TATASTEEL.
            • Summarize the uploaded dataset.
            • Which stocks appear risky?
            • Which stocks have high volume and low volatility?
            """)

        st.info(
            "Ask questions about stocks, markets, investing, finance etc"
        )
        # Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        prompt = st.chat_input(
            "Ask me anything..."
        )

        if prompt:

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            try:

                history = []

                for msg in st.session_state.messages[:-1]:

                    role = (
                        "model"
                        if msg["role"] == "assistant"
                        else "user"
                    )

                    history.append(
                        {
                            "role": role,
                            "parts": [msg["content"]]
                        }
                    )

                chat = model.start_chat(
                    history=history
                )
                data_context = f"""
                You are an AI Equity Analytics Assistant.

                You are analyzing the user's uploaded stock market dataset.

                Dataset Columns:
                {', '.join(df.columns)}

                Total Stocks:
                {df['Ticker'].nunique()}

                Date Range:
                {df['Date'].min()} to {df['Date'].max()}

                IMPORTANT RULES:

                1. Use the uploaded dataset whenever possible.
                2. Answer questions about stocks, returns, volatility, volume, trends and comparisons using the dataset.
                3. If the answer is not available in the dataset, clearly say so.
                4. Do not invent values.
                5. If the user asks a general finance question, answer normally.
                6. Be concise and analytical.
                """
                # Replace the sample_data block with this:
                stats = df.groupby("Ticker").agg(
                    avg_return=("Daily_Return_Pct", "mean"),
                    avg_volatility=("Volatility_20D", "mean"),
                    avg_volume=("Volume", "mean"),
                    avg_price_range=("Price_Range", "mean"),
                    latest_close=("Close", "last"),
                    latest_ma20=("MA20", "last"),
                    latest_ma50=("MA50", "last"),
                ).round(4)

                sample_data = stats.to_string()
                full_prompt = f"""
                {data_context}

                Aggregated Stats Per Stock (use these for all calculations):

                {sample_data}

                User Question:
                {prompt}
                """
                response = chat.send_message(full_prompt)

                assistant_reply = response.text

                with st.chat_message("assistant"):
                    st.markdown(
                        assistant_reply
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_reply
                    }
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )
else:
    st.info("Please upload a CSV file to begin.")

st.divider()

st.caption(
    "Built with Streamlit • Plotly • Python • AI Equity Analytics Platform"
)
