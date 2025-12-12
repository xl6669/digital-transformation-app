import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------- 适配你的Excel列名：股票代码/企业名称/年份/数字化转型指数 ----------------------
@st.cache_data
def load_data():
    try:
        # 读取仓库中的Excel文件（无需本地路径）
        df = pd.read_excel("上市公司数字化合并总表.xlsx")
        # 处理空值（避免报错）
        df = df.fillna(0)
        return df
    except FileNotFoundError:
        st.error("❌ 未找到Excel文件，请确认仓库中已上传「上市公司数字化合并总表.xlsx」")
        st.stop()

# ---------------------- 页面配置 ----------------------
st.set_page_config(
    page_title="上市公司数字化转型指数查询",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("📊 上市公司数字化转型指数查询系统")
st.divider()

# ---------------------- 加载数据 ----------------------
df = load_data()

# 数据预览
with st.expander("📋 数据预览（前10条）", expanded=False):
    st.dataframe(df.head(10), use_container_width=True)

# ---------------------- 核心查询功能（适配你的列名） ----------------------
st.subheader("🔍 指数查询")

col1, col2, col3 = st.columns(3)
with col1:
    # 股票代码选择
    stock_code_list = df["股票代码"].astype(str).unique().tolist()
    selected_code = st.selectbox("选择股票代码", stock_code_list)

with col2:
    # 企业名称选择（根据股票代码联动）
    company_list = df[df["股票代码"] == int(selected_code)]["企业名称"].unique().tolist()
    selected_company = st.selectbox("选择企业名称", company_list)

with col3:
    # 年份选择
    year_list = sorted(df["年份"].unique().tolist())
    selected_year = st.selectbox("选择年份", year_list)

# 筛选数据
filtered_df = df[
    (df["股票代码"] == int(selected_code)) &
    (df["企业名称"] == selected_company) &
    (df["年份"] == selected_year)
]

# 显示查询结果
st.divider()
if not filtered_df.empty:
    index_value = filtered_df["数字化转型指数"].iloc[0]
    st.success(f"✅ {selected_company}（{selected_code}）{selected_year}年 数字化转型指数：{index_value:.2f}")
    
    # 显示该企业该年份的所有指标
    with st.expander("📈 完整指标详情", expanded=True):
        st.dataframe(
            filtered_df.drop(["股票代码", "企业名称", "年份"], axis=1),
            use_container_width=True
        )
else:
    st.warning(f"⚠️ 未查询到 {selected_company}（{selected_code}）{selected_year}年 的数据")

# ---------------------- 数据可视化（适配你的列名） ----------------------
st.divider()
st.subheader("📊 数据可视化分析")

# 1. 单企业历年指数趋势
st.caption("👉 单企业历年数字化转型指数趋势")
company_trend_df = df[
    (df["股票代码"] == int(selected_code)) &
    (df["企业名称"] == selected_company)
].sort_values("年份")

if len(company_trend_df) > 1:
    fig_trend = px.line(
        company_trend_df,
        x="年份",
        y="数字化转型指数",
        title=f"{selected_company}（{selected_code}）历年数字化转型指数趋势",
        markers=True,
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("ℹ️ 该企业仅有1年数据，无法生成趋势图")

# 2. 同年份各企业指数对比（TOP10）
st.caption("👉 同年份各企业数字化转型指数TOP10")
year_top_df = df[df["年份"] == selected_year].sort_values("数字化转型指数", ascending=False).head(10)

fig_top = px.bar(
    year_top_df,
    x="企业名称",
    y="数字化转型指数",
    title=f"{selected_year}年 企业数字化转型指数TOP10",
    color="数字化转型指数",
    color_continuous_scale="Viridis",
    text="数字化转型指数"
)
fig_top.update_traces(texttemplate="%{text:.2f}", textposition="outside")
st.plotly_chart(fig_top, use_container_width=True)

# ---------------------- 底部说明 ----------------------
st.divider()
st.caption("💡 数据来源：上市公司数字化转型调研数据 | 支持指标：数字化转型指数、人工智能词频数等")
