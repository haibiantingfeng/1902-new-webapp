#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索性数据分析（EDA）Web App - 使用Streamlit

功能：
1. 支持上传CSV、XLSX、XLS格式的数据集
2. 自动生成数据概览、数据预览、统计摘要和可视化图表
3. 交互式分析界面

运行步骤：
1. 安装依赖：pip install -r requirements.txt
2. 运行应用：streamlit run eda_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="探索性数据分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("📊 探索性数据分析 (EDA) Web App")

# 侧边栏
st.sidebar.header("设置")

# 数据上传
st.sidebar.subheader("1. 上传数据")
uploaded_file = st.sidebar.file_uploader("选择文件", type=["csv", "xlsx", "xls"])

# 初始化变量
if uploaded_file is not None:
    # 读取数据
    @st.cache_data
    def load_data(file):
        """加载并预处理数据"""
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            return None
        
        # 自动检测列类型
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        
        return df
    
    # 加载数据
    df = load_data(uploaded_file)
    
    if df is not None:
        # 确定列类型
        def get_column_types(df):
            """获取列类型"""
            column_types = {}
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    column_types[col] = 'numeric'
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    column_types[col] = 'date'
                else:
                    column_types[col] = 'categorical'
            return column_types
        
        column_types = get_column_types(df)
        numeric_columns = [col for col, typ in column_types.items() if typ == 'numeric']
        categorical_columns = [col for col, typ in column_types.items() if typ == 'categorical']
        date_columns = [col for col, typ in column_types.items() if typ == 'date']
        
        # 显示数据信息
        st.sidebar.subheader("2. 数据信息")
        st.sidebar.write(f"数据行数: {len(df)}")
        st.sidebar.write(f"数据列数: {len(df.columns)}")
        st.sidebar.write(f"数值列: {len(numeric_columns)}")
        st.sidebar.write(f"类别列: {len(categorical_columns)}")
        st.sidebar.write(f"日期列: {len(date_columns)}")
        
        # 导航选项卡
        tab1, tab2, tab3, tab4 = st.tabs(["数据概览", "数据预览", "统计摘要", "可视化分析"])
        
        # 数据概览选项卡
        with tab1:
            st.subheader("📋 数据概览")
            
            # 统计卡片
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总行数", len(df))
            col2.metric("总列数", len(df.columns))
            col3.metric("数值列", len(numeric_columns))
            col4.metric("类别列", len(categorical_columns))
            
            # 列信息
            st.subheader("📊 列信息")
            columns_info = []
            for col in df.columns:
                columns_info.append({
                    '列名': col,
                    '类型': column_types[col],
                    '非空值': df[col].count(),
                    '缺失值': df[col].isnull().sum(),
                    '唯一值': df[col].nunique()
                })
            columns_df = pd.DataFrame(columns_info)
            st.dataframe(columns_df, use_container_width=True)
        
        # 数据预览选项卡
        with tab2:
            st.subheader("📅 数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            if len(df) > 10:
                st.write(f"显示前10行，共{len(df)}行数据")
        
        # 统计摘要选项卡
        with tab3:
            st.subheader("📊 统计摘要")
            if numeric_columns:
                st.dataframe(df[numeric_columns].describe(), use_container_width=True)
            else:
                st.info("没有数值列可供统计分析")
        
        # 可视化分析选项卡
        with tab4:
            st.subheader("📈 数据可视化")
            
            if numeric_columns:
                # 选择要分析的列
                selected_cols = st.multiselect("选择数值列进行分析", numeric_columns, default=numeric_columns[:2])
                
                # 直方图
                st.subheader("📊 直方图")
                for col in selected_cols:
                    fig = px.histogram(df, x=col, title=f"{col}的分布")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # 散点图
                if len(selected_cols) >= 2:
                    st.subheader("📈 散点图")
                    x_col = st.selectbox("选择X轴", selected_cols, index=0)
                    y_col = st.selectbox("选择Y轴", selected_cols, index=1)
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # 箱线图
                st.subheader("📦 箱线图")
                fig = px.box(df, y=selected_cols, title="数值列分布")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("没有数值列可供可视化分析")
                
            # 类别列分析
            if categorical_columns:
                st.subheader("📊 类别列分析")
                selected_cat_col = st.selectbox("选择类别列", categorical_columns)
                
                # 饼图
                fig = px.pie(df, names=selected_cat_col, title=f"{selected_cat_col}的分布")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # 柱状图
                fig = px.bar(df[selected_cat_col].value_counts().reset_index(), 
                           x='index', y=selected_cat_col, 
                           title=f"{selected_cat_col}的计数")
                fig.update_layout(height=400, xaxis_title=selected_cat_col, yaxis_title="计数")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("无法加载文件，请确保文件格式正确")
else:
    # 显示上传提示
    st.info("请在左侧边栏上传CSV、XLSX或XLS格式的数据集")
    
    # 显示示例数据格式
    st.subheader("📋 示例数据格式")
    example_data = {
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Value': [100, 102, 101],
        'Category': ['A', 'B', 'A'],
        'Amount': [1000, 1200, 900]
    }
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)

# 运行说明
st.sidebar.subheader("3. 运行说明")
st.sidebar.write("1. 安装依赖：pip install -r requirements.txt")
st.sidebar.write("2. 运行应用：streamlit run eda_app.py")
st.sidebar.write("3. 上传数据集文件")
st.sidebar.write("4. 在不同选项卡中查看数据分析结果")
st.sidebar.write("5. 选择不同的列进行可视化分析")

# 页脚
st.markdown("---")
st.markdown("© 2026 探索性数据分析Web App - 使用Streamlit构建")
