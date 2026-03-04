#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主Web App - 使用Streamlit

功能：
1. 金融数据分析
2. 探索性数据分析（EDA）

运行步骤：
1. 安装依赖：pip install -r requirements.txt
2. 运行应用：streamlit run main.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("📊 数据分析平台")

# 侧边栏导航
st.sidebar.header("导航")
app_mode = st.sidebar.selectbox(
    "选择应用模式",
    ["金融数据分析", "探索性数据分析"]
)

# 加载相应的应用
if app_mode == "金融数据分析":
    # 导入金融分析模块
    import app
elif app_mode == "探索性数据分析":
    # 导入EDA模块
    import eda_app
