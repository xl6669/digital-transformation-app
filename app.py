import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------- 核心配置（适配云端部署） ----------------------
# 读取仓库中的Excel文件（直接用文件名，无需本地路径）
@st.cache_data  # 缓存数据提升加载速度
def load_data():
    try:
        # 关键修改：仅保留文件名，适配云端读取
        df = pd.read_excel("上市公司数字化合并总表.xlsx")
        # 处理空值和数据类型（可选，根据你的Excel结构调整）
        df = df.fillna(0)
        return df
    except FileNotFoundError:
        st.error("❌ 未找到Excel文件，请确认仓库中已上传「上市公司数字化合并总表.xlsx」")
        st.stop()

# ---------------------- 页面布局 ----------------------
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

# 显示数据预览（可选）
with st.expander("📋 数据预览", expanded=False):
    st.dataframe(df.head(10), use_container_width=True)

# ---------------------- 核心功能：查询指数 ----------------------
st.subheader("🔍 指数查询")

# 1. 选择查询维度（根据你的Excel列名调整，示例用「公司名称」「年份」「数字化指数」）
col1, col2 = st.columns(2)
with col1:
    # 获取Excel中的公司名称列表（去重）
    company_list = df["公司名称"].unique().tolist()
    selected_company = st.selectbox("选择公司", company_list)

with col2:
    # 获取Excel中的年份列表（去重）
    year_list = sorted(df["年份"].unique().tolist())
    selected_year = st.selectbox("选择年份", year_list)

# 2. 筛选数据
filtered_df = df[(df["公司名称"] == selected_company) & (df["年份"] == selected_year)]

# 3. 显示查询结果
if not filtered_df.empty:
    index_value = filtered_df["数字化指数"].iloc[0]
    st.success(f"✅ {selected_company} {selected_year}年 数字化转型指数：{index_value:.2f}")
    
    # 额外：显示该公司该年份的其他指标（根据你的Excel列名调整）
    with st.expander("📈 更多指标详情", expanded=True):
        st.dataframe(filtered_df.drop(["公司名称", "年份"], axis=1), use_container_width=True)
else:
    st.warning(f"⚠️ 未查询到 {selected_company} {selected_year}年 的数据")

# ---------------------- 可视化功能（可选） ----------------------
st.divider()
st.subheader("📊 数据可视化")

# 1. 单公司历年指数趋势
st.caption("👉 单公司历年数字化指数趋势")
company_trend_df = df[df["公司名称"] == selected_company]
if len(company_trend_df) > 1:
    fig1 = px.line(
        company_trend_df,
        x="年份",
        y="数字化指数",
        title=f"{selected_company} 历年数字化指数趋势",
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

# 2. 同年份各公司指数对比
st.caption("👉 同年份各公司数字化指数对比")
year_compare_df = df[df["年份"] == selected_year].sort_values("数字化指数", ascending=False)
fig2 = px.bar(
    year_compare_df.head(10),  # 只显示前10名
    x="公司名称",
    y="数字化指数",
    title=f"{selected_year}年 各公司数字化指数TOP10",
    color="数字化指数",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------------- 底部说明 ----------------------
st.divider()
st.caption("💡 数据来源：上市公司数字化转型调研数据 | 部署环境：Streamlit Cloud")
