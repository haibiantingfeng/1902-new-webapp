#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融数据分析Web App - 使用Streamlit

功能：
1. 支持上传CSV格式的金融数据集
2. 自动生成4个核心图表：
   - 股价与EMA叠加折线图
   - MACD（DIF/DEA/红绿柱）走势图
   - 按月份/星期拆分的日历相关性涨跌幅图
   - 股价与成交量联动图
3. 带交互功能：可选择时间范围、放大图表、悬停显示具体数值

运行步骤：
1. 安装依赖：pip install -r requirements.txt
2. 运行应用：streamlit run app.py
3. 在浏览器中打开应用，上传CSV文件
4. 选择时间范围查看不同时期的数据
5. 点击图表放大，悬停查看详细数据
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="金融数据分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("📊 金融数据分析Web App")

# 侧边栏
st.sidebar.header("设置")

# 数据上传
st.sidebar.subheader("1. 上传数据")
uploaded_file = st.sidebar.file_uploader("选择CSV文件", type="csv")

# 初始化变量
if uploaded_file is not None:
    # 读取数据
    def calculate_ema(prices, period=20):
        """计算指数移动平均线"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
        """计算MACD指标"""
        fast_ema = calculate_ema(prices, fast_period)
        slow_ema = calculate_ema(prices, slow_period)
        dif = fast_ema - slow_ema
        dea = calculate_ema(dif, signal_period)
        macd = 2 * (dif - dea)
        return dif, dea, macd
    
    @st.cache_data
    def load_data(file):
        """加载并预处理数据"""
        df = pd.read_csv(file)
        
        # 确保Date列是日期类型
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 排序数据
        df = df.sort_values('Date')
        
        # 计算技术指标
        if 'EMA' not in df.columns:
            df['EMA'] = calculate_ema(df['Close'])
        
        if 'DIF' not in df.columns or 'DEA' not in df.columns or 'MACD' not in df.columns:
            df['DIF'], df['DEA'], df['MACD'] = calculate_macd(df['Close'])
        
        # 添加月份和星期信息
        df['Month'] = df['Date'].dt.month
        df['Month_Name'] = df['Date'].dt.strftime('%B')
        df['Weekday'] = df['Date'].dt.weekday
        df['Weekday_Name'] = df['Date'].dt.strftime('%A')
        
        # 计算日涨跌幅
        df['Daily_Return'] = df['Close'].pct_change() * 100
        
        return df
    
    # 加载数据
    df = load_data(uploaded_file)
    
    # 检查是否包含多个股票
    if 'Symbol' in df.columns:
        available_symbols = df['Symbol'].unique().tolist()
        st.sidebar.subheader("2. 股票选择")
        selected_symbol = st.sidebar.selectbox("选择股票", available_symbols)
        
        # 过滤选中的股票数据
        df = df[df['Symbol'] == selected_symbol]
    
    # 显示数据信息
    st.sidebar.subheader("3. 数据信息")
    st.sidebar.write(f"数据行数: {len(df)}")
    st.sidebar.write(f"时间范围: {df['Date'].min().date()} 至 {df['Date'].max().date()}")
    
    # 时间范围选择
    st.sidebar.subheader("4. 时间范围")
    start_date = st.sidebar.date_input(
        "开始日期",
        min_value=df['Date'].min().date(),
        max_value=df['Date'].max().date(),
        value=df['Date'].min().date()
    )
    
    end_date = st.sidebar.date_input(
        "结束日期",
        min_value=df['Date'].min().date(),
        max_value=df['Date'].max().date(),
        value=df['Date'].max().date()
    )
    
    # 过滤数据
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    
    # 显示原始数据预览
    st.subheader("📅 数据预览")
    st.dataframe(filtered_df.head(), use_container_width=True)
    
    # 图表1：股价与EMA叠加折线图
    st.subheader("📈 股价与EMA叠加折线图")
    fig1 = go.Figure()
    
    # 添加股价线
    fig1.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['Close'],
        name='股价',
        line=dict(color='blue', width=2),
        hovertemplate='日期: %{x}<br>股价: %{y:.2f}'
    ))
    
    # 添加EMA线
    fig1.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['EMA'],
        name='EMA',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='日期: %{x}<br>EMA: %{y:.2f}'
    ))
    
    # 更新布局
    fig1.update_layout(
        title='股价与指数移动平均线(EMA)走势',
        xaxis_title='日期',
        yaxis_title='价格',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # 图表2：MACD走势图
    st.subheader("📊 MACD走势图")
    fig2 = go.Figure()
    
    # 添加DIF线
    fig2.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['DIF'],
        name='DIF',
        line=dict(color='blue', width=2),
        hovertemplate='日期: %{x}<br>DIF: %{y:.4f}'
    ))
    
    # 添加DEA线
    fig2.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['DEA'],
        name='DEA',
        line=dict(color='red', width=2),
        hovertemplate='日期: %{x}<br>DEA: %{y:.4f}'
    ))
    
    # 添加MACD柱状图
    fig2.add_trace(go.Bar(
        x=filtered_df['Date'],
        y=filtered_df['MACD'],
        name='MACD柱状图',
        marker=dict(
            color=['green' if val >= 0 else 'red' for val in filtered_df['MACD']]
        ),
        hovertemplate='日期: %{x}<br>MACD: %{y:.4f}'
    ))
    
    # 更新布局
    fig2.update_layout(
        title='MACD指标走势图',
        xaxis_title='日期',
        yaxis_title='值',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 图表3：按月份/星期拆分的日历相关性涨跌幅图
    st.subheader("📅 日历相关性涨跌幅图")
    
    # 计算每月平均涨跌幅
    monthly_return = filtered_df.groupby('Month_Name')['Daily_Return'].mean().reset_index()
    monthly_return['Month'] = pd.to_datetime(monthly_return['Month_Name'], format='%B').dt.month
    monthly_return = monthly_return.sort_values('Month')
    
    # 计算每周平均涨跌幅
    weekday_return = filtered_df.groupby('Weekday_Name')['Daily_Return'].mean().reset_index()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_return['Weekday_Order'] = weekday_return['Weekday_Name'].apply(lambda x: weekday_order.index(x))
    weekday_return = weekday_return.sort_values('Weekday_Order')
    
    # 创建子图
    fig3 = go.Figure()
    
    # 添加月份涨跌幅
    fig3.add_trace(go.Bar(
        x=monthly_return['Month_Name'],
        y=monthly_return['Daily_Return'],
        name='月度平均涨跌幅',
        marker=dict(
            color=['green' if val >= 0 else 'red' for val in monthly_return['Daily_Return']]
        ),
        hovertemplate='月份: %{x}<br>平均涨跌幅: %{y:.2f}%'
    ))
    
    # 更新布局
    fig3.update_layout(
        title='月度平均涨跌幅',
        xaxis_title='月份',
        yaxis_title='平均涨跌幅 (%)',
        hovermode='closest',
        height=400
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # 周度涨跌幅图
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=weekday_return['Weekday_Name'],
        y=weekday_return['Daily_Return'],
        name='周度平均涨跌幅',
        marker=dict(
            color=['green' if val >= 0 else 'red' for val in weekday_return['Daily_Return']]
        ),
        hovertemplate='星期: %{x}<br>平均涨跌幅: %{y:.2f}%'
    ))
    
    fig4.update_layout(
        title='周度平均涨跌幅',
        xaxis_title='星期',
        yaxis_title='平均涨跌幅 (%)',
        hovermode='closest',
        height=400
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # 图表4：股价与成交量联动图
    st.subheader("📊 股价与成交量联动图")
    
    # 创建子图
    fig5 = go.Figure()
    
    # 添加股价线（主Y轴）
    fig5.add_trace(go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['Close'],
        name='股价',
        line=dict(color='blue', width=2),
        yaxis='y',
        hovertemplate='日期: %{x}<br>股价: %{y:.2f}'
    ))
    
    # 添加成交量柱状图（次Y轴）
    fig5.add_trace(go.Bar(
        x=filtered_df['Date'],
        y=filtered_df['Volume'],
        name='成交量',
        marker=dict(color='gray', opacity=0.5),
        yaxis='y2',
        hovertemplate='日期: %{x}<br>成交量: %{y:.0f}'
    ))
    
    # 更新布局
    fig5.update_layout(
        title='股价与成交量联动图',
        xaxis_title='日期',
        yaxis_title='股价',
        yaxis2=dict(
            title='成交量',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    st.plotly_chart(fig5, use_container_width=True)
    
    # 数据统计信息
    st.subheader("📊 统计信息")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("平均股价", f"{filtered_df['Close'].mean():.2f}")
    col2.metric("平均成交量", f"{filtered_df['Volume'].mean():.0f}")
    col3.metric("平均日涨跌幅", f"{filtered_df['Daily_Return'].mean():.2f}%")
    col4.metric("最大日涨跌幅", f"{filtered_df['Daily_Return'].max():.2f}%")
    
else:
    # 显示上传提示
    st.info("请在左侧边栏上传CSV格式的金融数据集")
    
    # 显示示例数据格式
    st.subheader("📋 示例数据格式")
    example_data = {
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Close': [100, 102, 101],
        'EMA': [99.5, 100.5, 101.0],
        'DIF': [0.5, 0.8, 0.6],
        'DEA': [0.4, 0.5, 0.6],
        'MACD': [0.1, 0.3, 0.0],
        'Volume': [1000000, 1200000, 900000]
    }
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)

# 运行说明
st.sidebar.subheader("5. 运行说明")
st.sidebar.write("1. 安装依赖：pip install -r requirements.txt")
st.sidebar.write("2. 运行应用：streamlit run app.py")
st.sidebar.write("3. 上传CSV文件")
st.sidebar.write("4. 如果CSV包含多个股票，选择要分析的股票")
st.sidebar.write("5. 选择时间范围")
st.sidebar.write("6. 查看生成的图表")
st.sidebar.write("\n⚠️ 注意：如果CSV文件缺少技术指标（EMA、DIF、DEA、MACD），应用会自动计算这些指标。")

# 页脚
st.markdown("---")
st.markdown("© 2026 金融数据分析Web App - 使用Streamlit构建")
