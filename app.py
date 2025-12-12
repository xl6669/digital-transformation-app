from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 你的文件路径
DATA_PATH = r"C:\Users\31649\Desktop\新建文件夹 (8)\上市公司数字化合并总表.xlsx"

st.set_page_config(
    page_title="数字化转型指数查询系统",
    page_icon="📊",
    layout="wide"
)

st.title("📊 上市公司数字化转型指数查询系统")
st.markdown("### 查询1999-2023年上市公司的数字化转型指数数据")

@st.cache_data
def load_data():
    try:
        # 读取Excel时直接指定列类型
        df = pd.read_excel(
            DATA_PATH,
            engine="openpyxl",
            dtype={
                "股票代码": str,       # 强制股票代码为文本
                "企业名称": str,
                "年份": int,          # 强制年份为整数
                "数字化转型指数": float # 强制指数为数值
            }
        )
        
        # 处理可能的空值/异常值
        df = df.dropna(subset=["股票代码", "企业名称", "年份", "数字化转型指数"])
        df["股票代码"] = df["股票代码"].str.strip()  # 去除股票代码前后空格
        df["年份"] = df["年份"].astype(int)         # 二次确认年份类型
        df["数字化转型指数"] = df["数字化转型指数"].astype(float) # 二次确认指数类型

        # 提取唯一值
        unique_stocks = sorted(df["股票代码"].unique())
        unique_companies = sorted(df["企业名称"].unique())
        unique_years = sorted(df["年份"].unique())
        
        # 股票→企业映射
        stock_to_company = df.drop_duplicates("股票代码").set_index("股票代码")["企业名称"].to_dict()
        
        return df, unique_stocks, unique_companies, unique_years, stock_to_company
    
    except Exception as e:
        # 精准捕获类型错误，强制转换后重试
        if "'<' not supported between instances of 'float' and 'str'" in str(e):
            df = pd.read_excel(DATA_PATH, engine="openpyxl")
            # 暴力转换所有列类型
            for col in df.columns:
                if col == "股票代码":
                    df[col] = df[col].astype(str)
                elif col == "年份":
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                else:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            # 再次提取数据
            df = df.dropna(subset=["股票代码", "企业名称", "年份", "数字化转型指数"])
            unique_stocks = sorted(df["股票代码"].unique())
            unique_companies = sorted(df["企业名称"].unique())
            unique_years = sorted(df["年份"].unique())
            stock_to_company = df.drop_duplicates("股票代码").set_index("股票代码")["企业名称"].to_dict()
            return df, unique_stocks, unique_companies, unique_years, stock_to_company
        else:
            st.error(f"加载失败：{str(e)}")
            return pd.DataFrame(), [], [], [], {}

# 加载数据
with st.spinner("正在加载数据..."):
    df, unique_stocks, unique_companies, unique_years, stock_to_company = load_data()

# 侧边栏
with st.sidebar:
    st.header("🔍 查询条件")
    search_type = st.radio("搜索方式:", ["股票代码", "企业名称"], index=0)
    
    selected_stock = None
    selected_company = None
    if search_type == "股票代码" and unique_stocks:
        selected_stock = st.selectbox("选择股票代码:", options=unique_stocks, format_func=lambda x: f"{x} - {stock_to_company.get(x, '未知')}", index=0)
        selected_company = stock_to_company.get(selected_stock, "")
    elif search_type == "企业名称" and unique_companies:
        selected_company = st.selectbox("选择企业名称:", options=unique_companies, index=None, placeholder="请选择")
        if selected_company:
            selected_stock = df[df["企业名称"] == selected_company]["股票代码"].iloc[0] if not df[df["企业名称"] == selected_company].empty else None
    
    selected_year = st.selectbox("选择年份:", options=unique_years, index=unique_years.index(2002) if 2002 in unique_years else 0) if unique_years else None
    search_button = st.button("📈 执行查询", use_container_width=True)

# 主页面
if df.empty:
    st.warning("暂无数据")
else:
    if search_button and selected_stock and selected_year:
        company_history = df[df["股票代码"] == selected_stock].sort_values("年份")
        filtered_data = company_history[company_history["年份"] == selected_year]
        
        st.title(f"{selected_company}历年数字化转型指数趋势")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=company_history["年份"], y=company_history["数字化转型指数"], mode="lines+markers", name="指数", line=dict(color="#1f77b4")))
        if not filtered_data.empty:
            fig.add_trace(go.Scatter(x=[selected_year], y=[filtered_data["数字化转型指数"].iloc[0]], mode="markers", marker=dict(size=14, color="#ff7f0e", symbol="star"), name=f"{selected_year}年"))
            fig.add_shape(type="line", x0=selected_year, y0=0, x1=selected_year, y1=company_history["数字化转型指数"].max()*1.2, line=dict(color="#ccc", dash="dash"))
        
        fig.update_layout(xaxis_title="年份", yaxis_title="指数", plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("详细数据")
        st.dataframe(pd.DataFrame({
            "股票代码": [selected_stock],
            "企业名称": [selected_company],
            "年份": [selected_year],
            "数字化转型指数": [filtered_data["数字化转型指数"].iloc[0] if not filtered_data.empty else 0]
        }), use_container_width=True)