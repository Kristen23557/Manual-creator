import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import uuid
import time
import shutil
import hashlib
from typing import Dict, List, Optional, Any

# ============================================
# 页面配置
# ============================================
st.set_page_config(
    page_title="网页手册创建器",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': 'https://github.com',
        'About': '# 网页手册创建器 v2.0\n一个强大的网页手册制作工具'
    }
)

# ============================================
# GitHub 深色主题CSS - 所有文字改为浅蓝色
# ============================================
def load_css():
    st.markdown("""
    <style>
    /* GitHub 深色主题变量 - 使用醒目浅蓝色 */
    :root {
        --gh-bg: #0d1117;
        --gh-surface: #161b22;
        --gh-muted: #8ed1ff;  /* 改为浅蓝色 */
        --gh-text: #7cc5ff;   /* 主要文字改为浅蓝色 */
        --gh-border: #30363d;
        --gh-primary: #58a6ff;
        --gh-success: #3fb950;
        --gh-danger: #ff7b72;
        --gh-warning: #f0883e;
        --gh-accent: #bc8cff;
        --gh-header: #010409;
        --gh-light-blue: #7cc5ff;  /* 新增浅蓝色 */
        --gh-bright-blue: #8ed1ff; /* 新增亮蓝色 */
    }
    
    /* 全局样式 */
    .stApp {
        background-color: var(--gh-bg) !important;
        color: var(--gh-light-blue) !important;  /* 改为浅蓝色 */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    }
    
    /* 主容器 */
    .main-container {
        max-width: 1600px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* GitHub 风格的头部 */
    .app-header {
        text-align: center;
        padding: 40px 0;
        background: var(--gh-header);
        border-bottom: 1px solid var(--gh-border);
        margin-bottom: 40px;
        border-radius: 0;
    }
    
    .app-title {
        font-size: 2.8rem;
        font-weight: 600;
        color: #8ed1ff !important;  /* 改为亮蓝色 */
        margin-bottom: 16px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
        font-weight: 400;
    }
    
    /* GitHub 风格的卡片 */
    .feature-card {
        background: var(--gh-surface);
        border: 1px solid var(--gh-border);
        border-radius: 6px;
        padding: 24px;
        transition: all 0.2s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        background: #1c2128;
        border-color: var(--gh-primary);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 20px;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        display: inline-block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #8ed1ff !important;  /* 改为亮蓝色 */
        margin-bottom: 12px;
        line-height: 1.3;
    }
    
    .feature-desc {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        line-height: 1.6;
        font-size: 1rem;
        margin-bottom: 16px;
    }
    
    .feature-badge {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(56, 139, 253, 0.1);
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        border-radius: 2em;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 8px;
        border: 1px solid rgba(56, 139, 253, 0.3);
    }
    
    /* GitHub 风格的按钮 */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid var(--gh-border);
        padding: 8px 16px;
        font-size: 0.95rem;
        font-weight: 500;
        transition: all 0.2s ease;
        background: #21262d;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        position: relative;
        overflow: hidden;
        letter-spacing: 0.3px;
    }
    
    .stButton > button:hover {
        background: #30363d;
        border-color: #8b949e;
        transform: translateY(-1px);
        color: #8ed1ff !important;  /* 悬停时改为亮蓝色 */
    }
    
    .stButton > button:active {
        background: #282e33;
    }
    
    .stButton > button[type="primary"] {
        background: var(--gh-primary);
        color: #ffffff !important;
        border-color: var(--gh-primary);
    }
    
    .stButton > button[type="primary"]:hover {
        background: #388bfd;
        border-color: #388bfd;
        color: #ffffff !important;
    }
    
    .stButton > button[type="secondary"] {
        background: #30363d;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 侧边栏 - GitHub 深色风格 */
    section[data-testid="stSidebar"] {
        background: var(--gh-header) !important;
        border-right: 1px solid var(--gh-border) !important;
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 20px;
        background: transparent !important;
    }
    
    /* 侧边栏标题 */
    .sidebar-header {
        text-align: left;
        padding: 0 20px 20px;
        border-bottom: 1px solid var(--gh-border);
        margin-bottom: 20px;
    }
    
    .sidebar-title {
        color: #8ed1ff !important;  /* 改为亮蓝色 */
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 8px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    
    .sidebar-subtitle {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        font-size: 0.9rem;
        margin-top: 2px;
    }
    
    /* 目录树 - GitHub 风格 */
    .directory-tree {
        padding: 0 16px;
    }
    
    .tree-item {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        font-size: 0.95rem;
        background: transparent;
        position: relative;
        font-weight: 400;
    }
    
    .tree-item:hover {
        background: #1c2128;
        color: #8ed1ff !important;  /* 悬停时改为亮蓝色 */
    }
    
    .tree-item.active {
        background: rgba(56, 139, 253, 0.1);
        color: #8ed1ff !important;  /* 改为亮蓝色 */
        font-weight: 500;
        border: 1px solid rgba(56, 139, 253, 0.3);
    }
    
    .tree-item-icon {
        font-size: 1rem;
        width: 20px;
        text-align: center;
        opacity: 0.8;
    }
    
    /* 编辑器容器 - GitHub 风格 */
    .editor-container {
        background: var(--gh-surface);
        border: 1px solid var(--gh-border);
        border-radius: 6px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    /* 内容元素 */
    .content-element {
        background: var(--gh-surface);
        border: 1px solid var(--gh-border);
        border-radius: 6px;
        padding: 20px;
        margin: 16px 0;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .content-element:hover {
        background: #1c2128;
        border-color: var(--gh-border);
    }
    
    /* 预览区域 */
    .preview-container {
        background: var(--gh-surface);
        border: 1px solid var(--gh-border);
        border-radius: 6px;
        padding: 20px;
        margin-top: 20px;
        max-height: 600px;
        overflow-y: auto;
        position: relative;
    }
    
    .preview-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .preview-container::-webkit-scrollbar-track {
        background: var(--gh-bg);
    }
    
    .preview-container::-webkit-scrollbar-thumb {
        background: #484f58;
        border-radius: 4px;
    }
    
    .preview-container::-webkit-scrollbar-thumb:hover {
        background: #5a626d;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--gh-surface);
        padding: 8px;
        border-radius: 6px;
        border: 1px solid var(--gh-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        background: transparent;
        font-size: 0.95rem;
        font-weight: 500;
        border: 1px solid transparent;
        transition: all 0.2s ease;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #1c2128;
        color: #8ed1ff !important;  /* 悬停时改为亮蓝色 */
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(56, 139, 253, 0.1) !important;
        color: #8ed1ff !important;  /* 改为亮蓝色 */
        border-color: rgba(56, 139, 253, 0.3) !important;
    }
    
    /* 表单样式 */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div {
        border-radius: 6px !important;
        border: 1px solid var(--gh-border) !important;
        padding: 8px 12px !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        background: var(--gh-surface) !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus,
    .stSelectbox > div > div:focus-within {
        border-color: var(--gh-primary) !important;
        box-shadow: 0 0 0 2px rgba(56, 139, 253, 0.2) !important;
        outline: none;
        color: #8ed1ff !important;  /* 聚焦时改为亮蓝色 */
    }
    
    /* 颜色选择器 */
    .stColorPicker > div > div {
        border-radius: 6px !important;
        border: 1px solid var(--gh-border) !important;
        overflow: hidden;
        transition: all 0.2s ease !important;
    }
    
    /* 状态提示 */
    .stAlert {
        border-radius: 6px;
        padding: 16px;
        border: 1px solid;
        background: var(--gh-surface);
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stAlert [data-testid="stMarkdownContainer"] {
        font-size: 0.95rem;
        font-weight: 400;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 分隔线 */
    hr {
        margin: 24px 0;
        border: none;
        height: 1px;
        background: var(--gh-border);
    }
    
    /* 响应式设计 */
    @media (max-width: 1024px) {
        .app-title {
            font-size: 2.2rem;
        }
        
        .app-subtitle {
            font-size: 1.1rem;
        }
        
        .editor-container {
            padding: 20px;
        }
        
        .feature-card {
            padding: 20px;
        }
    }
    
    @media (max-width: 768px) {
        .app-title {
            font-size: 1.8rem;
        }
        
        .app-subtitle {
            font-size: 1rem;
            padding: 0 16px;
        }
        
        .editor-container {
            padding: 16px;
        }
        
        .feature-card {
            padding: 16px;
        }
        
        .feature-title {
            font-size: 1.2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 12px;
            font-size: 0.9rem;
        }
    }
    
    /* 加载动画 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid rgba(56, 139, 253, 0.3);
        border-radius: 50%;
        border-top-color: #7cc5ff !important;  /* 改为浅蓝色 */
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 进度条 */
    .progress-bar {
        height: 4px;
        background: var(--gh-border);
        border-radius: 2px;
        overflow: hidden;
        margin: 16px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #7cc5ff, #8ed1ff);  /* 改为浅蓝色渐变 */
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    
    /* 计数器 */
    .counter {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: #7cc5ff !important;  /* 改为浅蓝色 */
        color: #0d1117 !important;
        border-radius: 50%;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 8px;
    }
    
    /* 徽章 */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(124, 197, 255, 0.1);  /* 浅蓝色半透明 */
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        border-radius: 2em;
        font-size: 0.85rem;
        font-weight: 500;
        margin-left: 8px;
        border: 1px solid rgba(124, 197, 255, 0.3);
    }
    
    /* 折叠面板 */
    .stExpander {
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px !important;
        margin: 12px 0 !important;
        background: var(--gh-surface) !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stExpander > div:first-child {
        background: var(--gh-surface) !important;
        border-radius: 6px !important;
        padding: 16px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #8ed1ff !important;  /* 改为亮蓝色 */
    }
    
    /* 成功/警告/错误状态 */
    .status-success {
        background: rgba(63, 185, 80, 0.1);
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid rgba(63, 185, 80, 0.2);
    }
    
    .status-warning {
        background: rgba(240, 136, 62, 0.1);
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid rgba(240, 136, 62, 0.2);
    }
    
    .status-error {
        background: rgba(255, 123, 114, 0.1);
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid rgba(255, 123, 114, 0.2);
    }
    
    /* 图标按钮 */
    .icon-btn {
        background: #21262d !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .icon-btn:hover {
        background: #30363d !important;
        border-color: #7cc5ff !important;  /* 改为浅蓝色 */
        color: #8ed1ff !important;  /* 改为亮蓝色 */
    }
    
    /* 代码块样式 */
    pre, code {
        font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace !important;
        background: var(--gh-header) !important;
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px !important;
        padding: 12px !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 表格样式 */
    table {
        background: var(--gh-surface) !important;
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px !important;
    }
    
    th {
        background: var(--gh-header) !important;
        color: #8ed1ff !important;  /* 改为亮蓝色 */
        font-weight: 600 !important;
    }
    
    td {
        border-color: var(--gh-border) !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 选择文本样式 */
    ::selection {
        background: rgba(124, 197, 255, 0.3) !important;  /* 浅蓝色半透明 */
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    ::-moz-selection {
        background: rgba(124, 197, 255, 0.3) !important;  /* 浅蓝色半透明 */
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 链接样式 */
    a {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        text-decoration: none !important;
    }
    
    a:hover {
        color: #8ed1ff !important;  /* 悬停时改为亮蓝色 */
        text-decoration: underline !important;
    }
    
    /* GitHub 风格的标题 */
    h1, h2, h3, h4, h5, h6 {
        color: #8ed1ff !important;  /* 改为亮蓝色 */
        font-weight: 600 !important;
        margin-top: 24px !important;
        margin-bottom: 16px !important;
    }
    
    h1 {
        font-size: 2rem !important;
        border-bottom: 1px solid var(--gh-border) !important;
        padding-bottom: 0.3em !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        border-bottom: 1px solid var(--gh-border) !important;
        padding-bottom: 0.3em !important;
    }
    
    /* 块引用 */
    blockquote {
        border-left: 3px solid #7cc5ff !important;  /* 改为浅蓝色 */
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        background: var(--gh-surface) !important;
        padding: 8px 16px !important;
        margin: 16px 0 !important;
        border-radius: 0 6px 6px 0 !important;
    }
    
    /* 列表样式 */
    ul, ol {
        padding-left: 32px !important;
    }
    
    li {
        margin: 8px 0 !important;
        line-height: 1.6 !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    li::marker {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 图片样式 */
    img {
        max-width: 100% !important;
        border-radius: 6px !important;
        border: 1px solid var(--gh-border) !important;
    }
    
    /* 禁用所有过度动画 */
    * {
        transition-duration: 0.2s !important;
        animation-duration: 0.2s !important;
    }
    
    /* 工具提示 */
    [data-tooltip] {
        position: relative;
        cursor: help;
        border-bottom: 1px dotted #7cc5ff;  /* 改为浅蓝色 */
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 自定义滚动条 */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gh-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: #484f58;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a626d;
    }
    
    /* 覆盖所有文本颜色 */
    p, span, div, label {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 数字输入框 */
    input[type="number"] {
        background: var(--gh-surface) !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        border: 1px solid var(--gh-border) !important;
    }
    
    /* 复选框 */
    .stCheckbox > label {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 滑块 */
    .stSlider > div {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 下拉菜单 */
    .stSelectbox select {
        background: var(--gh-surface) !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 多选框 */
    .stMultiSelect > div > div {
        background: var(--gh-surface) !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 文件上传器 */
    .stFileUploader > div {
        background: var(--gh-surface) !important;
        border: 1px solid var(--gh-border) !important;
    }
    
    /* 数据框 */
    .stDataFrame {
        background: var(--gh-surface) !important;
        border: 1px solid var(--gh-border) !important;
    }
    
    /* 指标 */
    .stMetric {
        background: var(--gh-surface) !important;
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px !important;
        padding: 16px !important;
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stMetric > div > div {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 图表 */
    .stPlotlyChart {
        background: var(--gh-surface) !important;
        border: 1px solid var(--gh-border) !important;
        border-radius: 6px !important;
    }
    
    /* 文本区域 */
    textarea {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 占位符文字 */
    ::placeholder {
        color: rgba(124, 197, 255, 0.6) !important;  /* 浅蓝色半透明 */
    }
    
    /* 输入框标签 */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label,
    .stCheckbox > label span {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 提示文本 */
    .stInfo, .stWarning, .stError, .stSuccess {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 展开器内容 */
    .stExpander > div:last-child {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 单选按钮 */
    .stRadio > label {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 多选框组 */
    .stCheckboxGroup > label {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 滑块标签 */
    .stSlider > label {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 文件上传器标签 */
    .stFileUploader > label {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 数据框标题 */
    .stDataFrame > div > div:first-child {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 容器的圆角改为直角，保持 GitHub 风格 */
    .main-container,
    .feature-card,
    .editor-container,
    .content-element,
    .tree-item,
    .stExpander,
    .preview-container {
        border-radius: 0 !important;
    }
    
    /* GitHub 的轻微圆角保留 */
    .stButton > button,
    .stTabs [data-baseweb="tab"],
    .stAlert,
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div {
        border-radius: 6px !important;
    }
    
    /* 所有 markdown 文本 */
    .stMarkdown {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6 {
        color: #8ed1ff !important;  /* 改为亮蓝色 */
    }
    
    .stMarkdown p {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stMarkdown ul,
    .stMarkdown ol {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stMarkdown li {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stMarkdown a {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stMarkdown a:hover {
        color: #8ed1ff !important;  /* 悬停时改为亮蓝色 */
    }
    
    .stMarkdown code {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    .stMarkdown blockquote {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
        border-left-color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 覆盖所有可能的文本类 */
    .text,
    .label,
    .caption,
    .title,
    .heading,
    .subtitle,
    .description,
    .content,
    .paragraph,
    .note {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* Streamlit 特定的类 */
    .css-1v0mbdj,
    .css-1offfwp,
    .css-1d391kg,
    .css-12oz5g7,
    .css-1aumxhk,
    .css-1v3fvcr,
    .css-1q8dd3e,
    .css-1lcbmhc,
    .css-1p1nwyz,
    .css-1xarl3l,
    .css-1y4p8pa,
    .css-16idsys,
    .css-1wrcr25,
    .css-1vbkxwb,
    .css-1hynsf2,
    .css-1l269bu,
    .css-1vbd788,
    .css-1n76uvr {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    
    /* 确保所有文本可见 */
    *:not(button):not(input):not(textarea):not(select):not(option) {
        color: #7cc5ff !important;  /* 改为浅蓝色 */
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# 会话状态管理
# ============================================
class SessionStateManager:
    @staticmethod
    def initialize():
        """初始化所有会话状态"""
        defaults = {
            'current_project': None,
            'project_structure': None,
            'current_page': None,
            'edit_mode': False,
            'edit_element_id': None,
            'active_tab': "home",
            'edit_page_title': False,
            'edit_page_id': None,
            'show_page_settings': False,
            'last_save_time': None,
            'auto_save': True,
            'project_loaded': False,
            'preview_mode': False,
            'selected_theme': 'dark',
            'sidebar_collapsed': False,
            'notification': None,
            'project_version': 1,
            'content_history': [],
            'current_history_index': -1,
            'is_saving': False,
            'last_backup_time': None,
            'export_in_progress': False,
            'current_operation': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def add_notification(message, type="info", duration=3):
        """添加通知"""
        st.session_state.notification = {
            "message": message,
            "type": type,
            "time": time.time(),
            "duration": duration
        }
    
    @staticmethod
    def show_notifications():
        """显示通知"""
        if st.session_state.notification:
            notification = st.session_state.notification
            current_time = time.time()
            
            if current_time - notification["time"] < notification["duration"]:
                if notification["type"] == "success":
                    st.success(notification["message"])
                elif notification["type"] == "error":
                    st.error(notification["message"])
                elif notification["type"] == "warning":
                    st.warning(notification["message"])
                else:
                    st.info(notification["message"])
            else:
                st.session_state.notification = None
    
    @staticmethod
    def start_operation(operation_name):
        """开始操作"""
        st.session_state.current_operation = operation_name
        st.session_state.is_saving = True
    
    @staticmethod
    def end_operation():
        """结束操作"""
        st.session_state.current_operation = None
        st.session_state.is_saving = False

# 项目操作类（已提取至 manual_creator.project_manager）
from manual_creator.project_manager import ProjectManager

# ============================================
# HTML生成器类 - 更新文字为浅蓝色
# ============================================
class HTMLGenerator:
    @staticmethod
    def generate_html(structure):
        """生成完整的HTML文件"""
        html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="author" content="{author}">
    <meta name="generator" content="网页手册创建器 v2.0">
    <meta name="theme-color" content="#0d1117">
    <title>{title}</title>
    
    <!-- 字体和图标 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap">
    
    <!-- GitHub Markdown CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown-dark.min.css">
    
    <!-- 主要样式 -->
    <style>
        {css}
    </style>
    
    <!-- 额外样式 -->
    {additional_css}
</head>
<body class="markdown-body">
    <!-- 侧边栏切换按钮 -->
    <button class="sidebar-toggle" id="sidebarToggle" aria-label="切换侧边栏" title="切换侧边栏 (Ctrl+B)">
        <i class="fas fa-bars"></i>
    </button>
    
    <!-- 加载遮罩 -->
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-spinner-large"></div>
        <p>加载中...</p>
    </div>
    
    <div class="container">
        <!-- 侧边栏导航 -->
        <nav class="sidebar" id="sidebar" aria-label="主导航">
            <div class="sidebar-header">
                <button class="close-sidebar" id="closeSidebar" aria-label="关闭侧边栏">
                    <i class="fas fa-times"></i>
                </button>
                <h1 class="sidebar-title">{title}</h1>
                {description_html}
                <div class="sidebar-meta">
                    <span class="meta-item"><i class="fas fa-calendar"></i> {date}</span>
                    <span class="meta-item"><i class="fas fa-user"></i> {author}</span>
                    {word_count_html}
                </div>
            </div>
            
            <div class="directory-tree" role="tree">
                <div class="tree-item cover-item" data-page="cover" role="treeitem" aria-selected="true">
                    <i class="fas fa-home"></i>
                    <span>🏠 {cover_title}</span>
                </div>
                {pages_html}
            </div>
            
            <div class="sidebar-footer">
                <div class="theme-switcher">
                    <button class="theme-btn light-btn" data-theme="light" aria-label="切换到浅色主题">
                        <i class="fas fa-sun"></i> 浅色
                    </button>
                    <button class="theme-btn dark-btn" data-theme="dark" aria-label="切换到深色主题">
                        <i class="fas fa-moon"></i> 深色
                    </button>
                </div>
                <p class="copyright">© {year} {title} · 由网页手册创建器生成</p>
            </div>
        </nav>
        
        <!-- 主内容区 -->
        <main class="content" id="content">
            <!-- 阅读进度条 -->
            <div class="reading-progress" id="readingProgress">
                <div class="progress-bar"></div>
            </div>
            
            <!-- 页面容器 -->
            <div class="page active" id="cover-page" role="region" aria-label="封面页">
                {cover_content}
            </div>
            {pages_content}
        </main>
    </div>
    
    <!-- 返回顶部按钮 -->
    <button id="backToTop" class="back-to-top" aria-label="返回顶部" title="返回顶部">
        <i class="fas fa-chevron-up"></i>
    </button>
    
    <!-- 快速导航菜单 -->
    <div class="quick-nav" id="quickNav">
        <button class="nav-btn" data-action="prev" aria-label="上一页" title="上一页 (←)">
            <i class="fas fa-chevron-left"></i>
        </button>
        <button class="nav-btn" data-action="next" aria-label="下一页" title="下一页 (→)">
            <i class="fas fa-chevron-right"></i>
        </button>
        <button class="nav-btn" data-action="toc" aria-label="打开目录" title="打开目录 (T)">
            <i class="fas fa-list"></i>
        </button>
        <button class="nav-btn" data-action="search" aria-label="搜索" title="搜索 (/)">
            <i class="fas fa-search"></i>
        </button>
    </div>
    
    <!-- 搜索模态框 -->
    <div class="search-modal" id="searchModal">
        <div class="search-container">
            <input type="text" class="search-input" id="searchInput" placeholder="搜索内容..." aria-label="搜索输入">
            <button class="search-close" id="searchClose" aria-label="关闭搜索">
                <i class="fas fa-times"></i>
            </button>
            <div class="search-results" id="searchResults"></div>
        </div>
    </div>

    <!-- 主要JavaScript -->
    <script>
        {javascript}
    </script>
    
    <!-- 额外JavaScript -->
    {additional_js}
</body>
</html>"""
        
        # 获取数据
        title = structure.get("title", "网页手册")
        description = structure.get("description", "一个精美的手册网页")
        author = "网页手册创建器用户"
        cover_title = structure["cover_page"].get("title", "封面")
        year = datetime.now().year
        date = datetime.now().strftime("%Y年%m月%d日")
        
        # 计算字数
        word_count = HTMLGenerator.calculate_word_count(structure)
        word_count_html = f'<span class="meta-item"><i class="fas fa-file-word"></i> {word_count:,} 字</span>' if word_count > 0 else ''
        
        # 生成各部分内容
        css = HTMLGenerator.generate_css(structure["config"])
        additional_css = HTMLGenerator.generate_additional_css()
        description_html = f'<p class="sidebar-description">{description}</p>' if description else ''
        pages_html = HTMLGenerator.generate_pages_html(structure["pages"])
        pages_content = HTMLGenerator.generate_pages_content(structure["pages"])
        cover_content = HTMLGenerator.generate_page_content(structure["cover_page"])
        javascript = HTMLGenerator.generate_javascript(structure["config"])
        additional_js = HTMLGenerator.generate_additional_js()
        
        # 格式化HTML
        html = html_template.format(
            title=title,
            description=description,
            description_html=description_html,
            author=author,
            cover_title=cover_title,
            year=year,
            date=date,
            word_count_html=word_count_html,
            css=css,
            additional_css=additional_css,
            pages_html=pages_html,
            pages_content=pages_content,
            cover_content=cover_content,
            javascript=javascript,
            additional_js=additional_js
        )
        
        return html
    
    @staticmethod
    def calculate_word_count(structure):
        """计算总字数"""
        word_count = 0

        def chars_count(s: str) -> int:
            if not s:
                return 0
            return len(s.replace('\n', '').replace(' ', ''))

        if "content" in structure.get("cover_page", {}):
            for element in structure["cover_page"]["content"]:
                if element.get("type") in ["heading", "paragraph", "note"]:
                    text = element.get("text", "")
                    word_count += chars_count(text)

        for page in structure.get("pages", []):
            if "content" in page:
                for element in page["content"]:
                    if element.get("type") in ["heading", "paragraph", "note"]:
                        text = element.get("text", "")
                        word_count += chars_count(text)

        return word_count
    
    @staticmethod
    def generate_css(config):
        """生成GitHub风格的CSS样式 - 文字改为浅蓝色"""
        theme = config.get("theme", "dark")
        primary_color = config.get("primary_color", "#58a6ff")
        secondary_color = config.get("secondary_color", "#bc8cff")
        
        # GitHub 深色主题颜色 - 文字使用浅蓝色
        bg_color = "#0d1117"
        text_color = "#7cc5ff"  # 改为浅蓝色
        sidebar_bg = "#161b22"
        card_bg = "#161b22"
        border_color = "#30363d"
        code_bg = "#1c2128"
        
        return f"""
        :root {{
            --primary-color: {primary_color};
            --secondary-color: {secondary_color};
            --accent-color: #bc8cff;
            --success-color: #3fb950;
            --warning-color: #f0883e;
            --danger-color: #ff7b72;
            --info-color: #58a6ff;
            
            --bg-color: {bg_color};
            --text-color: {text_color};
            --sidebar-bg: {sidebar_bg};
            --card-bg: {card_bg};
            --border-color: {border_color};
            --code-bg: {code_bg};
            
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.5);
            --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.6);
            --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.7);
            
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            
            --spacing-xs: 8px;
            --spacing-sm: 12px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
            font-size: 16px;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            overflow-x: hidden;
            min-height: 100vh;
        }}
        
        /* GitHub 风格的容器布局 */
        .container {{
            display: flex;
            min-height: 100vh;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* GitHub 风格的侧边栏 */
        .sidebar {{
            width: 280px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            overflow-y: auto;
            z-index: 1000;
            transition: transform 0.2s ease;
        }}
        
        .sidebar.hidden {{
            transform: translateX(-100%);
        }}
        
        /* 侧边栏头部 */
        .sidebar-header {{
            padding: 24px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .close-sidebar {{
            position: absolute;
            top: 16px;
            right: 16px;
            background: transparent;
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            width: 32px;
            height: 32px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            opacity: 0.7;
        }}
        
        .close-sidebar:hover {{
            background: var(--card-bg);
            color: #8ed1ff;
            opacity: 1;
        }}
        
        .sidebar-title {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #8ed1ff;
            margin-bottom: 8px;
        }}
        
        .sidebar-description {{
            font-size: 0.95rem;
            color: var(--text-color);
            opacity: 0.8;
            line-height: 1.5;
            margin-bottom: 16px;
        }}
        
        .sidebar-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 12px;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
            color: var(--text-color);
            opacity: 0.7;
        }}
        
        /* 目录树 */
        .directory-tree {{
            padding: 16px;
        }}
        
        .tree-item {{
            padding: 10px 12px;
            margin: 4px 0;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-color);
            font-size: 0.95rem;
            border: 1px solid transparent;
        }}
        
        .tree-item:hover {{
            background: #1c2128;
            color: #8ed1ff;
        }}
        
        .tree-item.active {{
            background: rgba(56, 139, 253, 0.1);
            color: #8ed1ff;
            font-weight: 500;
            border-color: rgba(56, 139, 253, 0.3);
        }}
        
        /* 侧边栏页脚 */
        .sidebar-footer {{
            padding: 20px;
            margin-top: 20px;
            border-top: 1px solid var(--border-color);
        }}
        
        .theme-switcher {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }}
        
        .theme-btn {{
            flex: 1;
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            background: var(--card-bg);
            color: var(--text-color);
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.9rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}
        
        .theme-btn:hover {{
            background: #1c2128;
            border-color: #8ed1ff;
            color: #8ed1ff;
        }}
        
        .theme-btn.active {{
            background: #58a6ff;
            color: white;
            border-color: #58a6ff;
        }}
        
        .copyright {{
            font-size: 0.85rem;
            color: var(--text-color);
            opacity: 0.6;
            text-align: center;
        }}
        
        /* 侧边栏切换按钮 */
        .sidebar-toggle {{
            position: fixed;
            top: 16px;
            left: 16px;
            background: #58a6ff;
            color: white;
            border: none;
            border-radius: var(--radius-sm);
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            z-index: 999;
            box-shadow: var(--shadow-md);
            transition: all 0.2s ease;
            opacity: 0;
        }}
        
        .sidebar.hidden ~ .sidebar-toggle {{
            opacity: 1;
        }}
        
        .sidebar-toggle:hover {{
            background: #388bfd;
            transform: scale(1.05);
        }}
        
        /* 内容区域 */
        .content {{
            flex: 1;
            margin-left: 280px;
            padding: 32px;
            min-height: 100vh;
            background: var(--bg-color);
            transition: all 0.2s ease;
        }}
        
        .sidebar.hidden ~ .content {{
            margin-left: 0;
        }}
        
        /* GitHub Markdown 风格 */
        .markdown-body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            font-size: 16px;
            line-height: 1.6;
            word-wrap: break-word;
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }}
        
        .markdown-body h1,
        .markdown-body h2,
        .markdown-body h3,
        .markdown-body h4,
        .markdown-body h5,
        .markdown-body h6 {{
            font-weight: 600 !important;
            color: #8ed1ff !important;
            margin-top: 24px !important;
            margin-bottom: 16px !important;
            padding-bottom: 0.3em !important;
            border-bottom: 1px solid var(--border-color) !important;
        }}
        
        .markdown-body h1 {{
            font-size: 2em !important;
        }}
        
        .markdown-body h2 {{
            font-size: 1.5em !important;
        }}
        
        .markdown-body p {{
            margin-bottom: 16px !important;
            line-height: 1.6 !important;
            color: var(--text-color) !important;
        }}
        
        .markdown-body code {{
            font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace !important;
            background-color: var(--code-bg) !important;
            border-radius: 6px !important;
            padding: 0.2em 0.4em !important;
            font-size: 85% !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
        }}
        
        .markdown-body pre {{
            background-color: var(--code-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
            padding: 16px !important;
            overflow: auto;
            line-height: 1.45;
            color: var(--text-color) !important;
        }}
        
        .markdown-body blockquote {{
            border-left: 0.25em solid #7cc5ff !important;
            color: var(--text-color) !important;
            padding: 0 1em !important;
            margin: 16px 0 !important;
        }}
        
        .markdown-body ul, .markdown-body ol {{
            padding-left: 2em !important;
        }}
        
        .markdown-body li {{
            margin: 8px 0 !important;
            color: var(--text-color) !important;
        }}
        
        .markdown-body table {{
            border-spacing: 0;
            border-collapse: collapse;
            display: block;
            width: max-content;
            max-width: 100%;
            overflow: auto;
            margin: 16px 0 !important;
        }}
        
        .markdown-body th {{
            font-weight: 600 !important;
            background-color: var(--card-bg) !important;
            color: #8ed1ff !important;
        }}
        
        .markdown-body th,
        .markdown-body td {{
            padding: 6px 13px !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
        }}
        
        .markdown-body tr {{
            background-color: var(--bg-color) !important;
            border-top: 1px solid var(--border-color) !important;
        }}
        
        .markdown-body tr:nth-child(2n) {{
            background-color: var(--card-bg) !important;
        }}
        
        .markdown-body hr {{
            border: none !important;
            height: 1px !important;
            background-color: var(--border-color) !important;
            margin: 24px 0 !important;
        }}
        
        .markdown-body a {{
            color: #7cc5ff !important;
            text-decoration: none !important;
        }}
        
        .markdown-body a:hover {{
            color: #8ed1ff !important;
            text-decoration: underline !important;
        }}
        
        /* 页面样式 */
        .page {{
            max-width: 800px;
            margin: 0 auto;
            display: none;
        }}
        
        .page.active {{
            display: block;
        }}
        
        .page-title {{
            font-size: 2em;
            font-weight: 600;
            color: #8ed1ff;
            margin-bottom: 24px;
            padding-bottom: 0.3em;
            border-bottom: 1px solid var(--border-color);
        }}
        
        /* 内容元素 */
        .element {{
            margin: 24px 0;
        }}
        
        .heading {{
            color: #8ed1ff;
            margin: 16px 0;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.3em;
        }}
        
        .heading-1 {{ 
            font-size: 2em;
            margin-top: 32px;
        }}
        
        .heading-2 {{ 
            font-size: 1.5em;
            margin-top: 24px;
        }}
        
        .heading-3 {{ 
            font-size: 1.25em;
            margin-top: 20px;
        }}
        
        .heading-4 {{ 
            font-size: 1em;
            margin-top: 16px;
        }}
        
        .paragraph {{
            line-height: 1.6;
            font-size: 1rem;
            color: var(--text-color);
            padding: 16px;
            border-radius: var(--radius-sm);
            margin: 16px 0;
            background: var(--card-bg);
            border-left: 3px solid #58a6ff;
        }}
        
        .note {{
            background: var(--card-bg);
            border-left: 3px solid #58a6ff;
            padding: 16px;
            border-radius: var(--radius-sm);
            margin: 16px 0;
            font-style: italic;
            color: var(--text-color);
        }}
        
        .note-content {{
            color: var(--text-color);
            font-size: 1rem;
            line-height: 1.6;
        }}
        
        .note-author {{
            text-align: right;
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.9rem;
            margin-top: 12px;
            font-style: italic;
        }}
        
        .button {{
            display: inline-block;
            padding: 8px 16px;
            background: #58a6ff;
            color: white;
            text-decoration: none;
            border-radius: var(--radius-sm);
            font-weight: 500;
            font-size: 1rem;
            transition: all 0.2s ease;
            border: 1px solid #58a6ff;
            cursor: pointer;
            margin: 12px 0;
        }}
        
        .button:hover {{
            background: #388bfd;
            text-decoration: none;
            transform: translateY(-1px);
        }}
        
        .video-container {{
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: var(--radius-sm);
            background: var(--card-bg);
            margin: 20px 0;
            border: 1px solid var(--border-color);
        }}
        
        .video-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
            border-radius: var(--radius-sm);
        }}
        
        /* 返回顶部按钮 */
        .back-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background: #58a6ff;
            color: white;
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            z-index: 1000;
            transition: all 0.2s ease;
        }}
        
        .back-to-top.show {{
            display: flex;
        }}
        
        .back-to-top:hover {{
            background: #388bfd;
            transform: translateY(-2px);
        }}
        
        /* 快速导航 */
        .quick-nav {{
            position: fixed;
            bottom: 20px;
            right: 70px;
            display: flex;
            gap: 8px;
            z-index: 998;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        
        .quick-nav.visible {{
            opacity: 1;
        }}
        
        .nav-btn {{
            width: 40px;
            height: 40px;
            border-radius: var(--radius-sm);
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            color: var(--text-color);
            transition: all 0.2s ease;
        }}
        
        .nav-btn:hover {{
            background: #1c2128;
            border-color: #8ed1ff;
            color: #8ed1ff;
        }}
        
        /* 搜索模态框 */
        .search-modal {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            z-index: 2000;
            display: none;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        
        .search-modal.active {{
            display: flex;
            opacity: 1;
        }}
        
        .search-container {{
            width: 90%;
            max-width: 600px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 20px;
        }}
        
        .search-input {{
            width: 100%;
            padding: 12px;
            font-size: 1rem;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            background: var(--bg-color);
            color: var(--text-color);
            margin-bottom: 16px;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: #58a6ff;
        }}
        
        .search-close {{
            position: absolute;
            top: 16px;
            right: 16px;
            background: transparent;
            border: none;
            color: var(--text-color);
            font-size: 1.2rem;
            cursor: pointer;
        }}
        
        .search-results {{
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .search-result-item {{
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            transition: all 0.2s ease;
            color: var(--text-color);
        }}
        
        .search-result-item:hover {{
            background: #1c2128;
            color: #8ed1ff;
        }}
        
        .search-result-title {{
            font-weight: 500;
            color: var(--text-color);
            margin-bottom: 4px;
        }}
        
        .search-result-content {{
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.9rem;
        }}
        
        /* 加载遮罩 */
        .loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--bg-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 3000;
        }}
        
        .loading-spinner-large {{
            width: 50px;
            height: 50px;
            border: 3px solid var(--border-color);
            border-top: 3px solid #7cc5ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
        }}
        
        .loading-overlay p {{
            font-size: 1rem;
            color: var(--text-color);
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .sidebar {{
                width: 100%;
                max-width: 300px;
            }}
            
            .content {{
                margin-left: 0;
                padding: 20px;
            }}
            
            .page {{
                padding-bottom: 20px;
            }}
            
            .page-title {{
                font-size: 1.5em;
            }}
        }}
        
        @media (max-width: 480px) {{
            .content {{
                padding: 16px;
            }}
            
            .page-title {{
                font-size: 1.3em;
            }}
            
            .heading-1 {{ font-size: 1.5em; }}
            .heading-2 {{ font-size: 1.3em; }}
            .heading-3 {{ font-size: 1.1em; }}
            .heading-4 {{ font-size: 1em; }}
        }}
        
        /* 打印样式 */
        @media print {{
            .sidebar,
            .sidebar-toggle,
            .quick-nav,
            .back-to-top {{
                display: none !important;
            }}
            
            .content {{
                margin-left: 0 !important;
                padding: 0 !important;
            }}
        }}
        """
    
    @staticmethod
    def generate_additional_css():
        """生成额外的CSS - 文字改为浅蓝色"""
        return """<style>
        /* 自定义滚动条 */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-color);
        }
        
        ::-webkit-scrollbar-thumb {
            background: #484f58;
            border-radius: 4px;
            border: 2px solid var(--bg-color);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #5a626d;
        }
        
        /* 选择文本样式 */
        ::selection {
            background: rgba(124, 197, 255, 0.3);
            color: #7cc5ff;
        }
        
        ::-moz-selection {
            background: rgba(124, 197, 255, 0.3);
            color: #7cc5ff;
        }
        
        /* 焦点样式 */
        :focus {
            outline: 2px solid rgba(124, 197, 255, 0.5);
            outline-offset: 1px;
        }
        
        :focus:not(:focus-visible) {
            outline: none;
        }
        
        /* 图片样式 */
        img {
            max-width: 100%;
            height: auto;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
        }
        
        /* 工具提示 */
        [data-tooltip] {
            position: relative;
            cursor: help;
            color: #7cc5ff;
        }
        
        [data-tooltip]:hover::before {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--card-bg);
            color: #7cc5ff;
            padding: 6px 10px;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            white-space: nowrap;
            border: 1px solid var(--border-color);
            z-index: 1000;
            margin-bottom: 5px;
        }
        
        /* 空状态文本 */
        .empty-state {
            color: #7cc5ff;
            opacity: 0.7;
        }
        
        /* 图片标题 */
        .image-caption {
            color: #7cc5ff;
            opacity: 0.7;
        }
        </style>"""
    
    @staticmethod
    def generate_pages_html(pages):
        """生成页面导航HTML"""
        if not pages:
            return ""
        
        pages_html = ""
        for page in pages:
            icon = "fas fa-book" if page.get("type") == "chapter" else "fas fa-file-alt"
            title = page.get('title', '未命名页面')
            pages_html += f"""
                <div class="tree-item" data-page="{page['id']}" role="treeitem">
                    <i class="{icon}"></i>
                    <span>{title}</span>
                </div>
            """
        return pages_html
    
    @staticmethod
    def generate_pages_content(pages):
        """生成页面内容HTML"""
        if not pages:
            return ""
        
        pages_content = ""
        for page in pages:
            page_content = HTMLGenerator.generate_page_content(page)
            title = page.get('title', '未命名页面')
            pages_content += f"""
                <div class="page" id="{page['id']}-page" role="region" aria-label="{title}">
                    <h1 class="page-title">{title}</h1>
                    {page_content}
                </div>
            """
        return pages_content
    
    @staticmethod
    def generate_page_content(page):
        """生成单个页面内容HTML"""
        if "content" not in page or not page["content"]:
            return '''
            <div class="empty-content">
                <div class="empty-state">
                    <i class="fas fa-file-alt fa-2x" style="color: #7cc5ff; opacity: 0.3; margin-bottom: 1rem;"></i>
                    <p style="color: #7cc5ff; opacity: 0.5; font-style: italic;">暂无内容</p>
                </div>
            </div>
            '''
        
        content_html = ""
        for element in page["content"]:
            element_html = HTMLGenerator.generate_element_html(element)
            content_html += f'<div class="element markdown-body">{element_html}</div>'
        
        return content_html
    
    @staticmethod
    def generate_element_html(element):
        """生成单个元素HTML - 文字改为浅蓝色"""
        element_type = element["type"]
        
        if element_type == "heading":
            level = element.get("level", 2)
            text = element.get("text", "")
            color = element.get("color", "#8ed1ff")  # 改为亮蓝色
            align = element.get("align", "left")
            
            return f'<h{level} class="heading heading-{level}" style="color: {color}; text-align: {align}; border-bottom: 1px solid #30363d;">{text}</h{level}>'
        
        elif element_type == "paragraph":
            text = element.get("text", "")
            color = element.get("color", "#7cc5ff")  # 改为浅蓝色
            background = element.get("background", "transparent")
            align = element.get("align", "left")
            
            text_with_breaks = text.replace('\n', '<br>')
            return f'''
            <div class="paragraph" style="color: {color}; background: {background}; text-align: {align}; border-left: 3px solid #58a6ff;">
                {text_with_breaks}
            </div>
            '''
        
        elif element_type == "note":
            text = element.get("text", "")
            author = element.get("author", "")
            color = element.get("color", "#7cc5ff")  # 改为浅蓝色
            background = element.get("background", "rgba(56, 139, 253, 0.1)")
            
            author_html = f'<div class="note-author">{author}</div>' if author else ''
            
            return f'''
            <div class="note" style="background: {background}; border-left: 3px solid #58a6ff;">
                <div class="note-content" style="color: {color};">
                    "{text}"
                    {author_html}
                </div>
            </div>
            '''
        
        elif element_type == "button":
            text = element.get("text", "点击这里")
            url = element.get("url", "#")
            color = element.get("color", "#ffffff")
            background = element.get("background", "#238636")
            
            return f'''
            <a href="{url}" target="_blank" class="button" style="background: {background}; color: {color}; border: 1px solid {background};">
                {text}
            </a>
            '''
        
        elif element_type == "video":
            video_id = element.get("video_id", "")
            if video_id:
                return f'''
                <div class="video-container">
                    <iframe src="https://player.bilibili.com/player.html?bvid={video_id}&page=1"
                            scrolling="no" border="0" frameborder="no" framespacing="0"
                            allowfullscreen="true"
                            title="B站视频播放器">
                    </iframe>
                </div>
                '''
            else:
                return '<p style="color: #7cc5ff; opacity: 0.5; font-style: italic;">[视频ID未设置]</p>'  # 改为浅蓝色
        
        elif element_type == "image":
            src = element.get("src", "")
            alt = element.get("alt", "图片")
            caption = element.get("caption", "")
            
            caption_html = f'<p class="image-caption" style="text-align: center; color: #7cc5ff; opacity: 0.7; font-size: 0.9rem; margin-top: 0.5rem;">{caption}</p>' if caption else ''  # 改为浅蓝色
            
            return f'''
            <div class="image-container">
                <img src="{src}" alt="{alt}" style="max-width: 100%; height: auto; border: 1px solid #30363d;">
                {caption_html}
            </div>
            '''
        
        elif element_type == "code":
            code = element.get("code", "")
            language = element.get("language", "text")
            
            return f'''
            <pre><code class="language-{language}">{html.escape(code)}</code></pre>
            '''
        
        return ""

# 由于代码长度限制，HTMLGenerator类的剩余方法保持原样

# ============================================
# 内容元素类 - 更新默认颜色为浅蓝色
# ============================================
class ContentElement:
    element_types = {
        "heading": {"name": "标题", "icon": "🏷️"},
        "paragraph": {"name": "段落", "icon": "📝"},
        "note": {"name": "注释/吐槽", "icon": "💬"},
        "button": {"name": "按钮", "icon": "🔗"},
        "video": {"name": "B站视频", "icon": "🎬"},
        "image": {"name": "图片", "icon": "🖼️"},
        "code": {"name": "代码块", "icon": "💻"},
        "divider": {"name": "分割线", "icon": "➖"}
    }
    
    @staticmethod
    def create_element(element_type, **kwargs):
        """创建内容元素"""
        element_id = str(uuid.uuid4())[:8]
        element = {
            "id": element_id,
            "type": element_type,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # 根据元素类型设置默认值（使用浅蓝色）
        if element_type == "heading":
            element.update({
                "text": kwargs.get("text", "新标题"),
                "level": kwargs.get("level", 2),
                "color": kwargs.get("color", "#8ed1ff"),  # 改为亮蓝色
                "align": kwargs.get("align", "left"),
                "animation": kwargs.get("animation", "none")
            })
        elif element_type == "paragraph":
            element.update({
                "text": kwargs.get("text", "请输入段落内容..."),
                "color": kwargs.get("color", "#7cc5ff"),  # 改为浅蓝色
                "background": kwargs.get("background", "transparent"),
                "align": kwargs.get("align", "left"),
                "font_size": kwargs.get("font_size", "1rem"),
                "line_height": kwargs.get("line_height", "1.6")
            })
        elif element_type == "note":
            element.update({
                "text": kwargs.get("text", "这里是注释内容..."),
                "author": kwargs.get("author", ""),
                "color": kwargs.get("color", "#7cc5ff"),  # 改为浅蓝色
                "background": kwargs.get("background", "rgba(56, 139, 253, 0.1)"),
                "show_quotes": kwargs.get("show_quotes", True)
            })
        elif element_type == "button":
            element.update({
                "text": kwargs.get("text", "点击这里"),
                "url": kwargs.get("url", "#"),
                "color": kwargs.get("color", "#ffffff"),
                "background": kwargs.get("background", "#238636"),
                "hover_background": kwargs.get("hover_background", "#2ea043"),
                "size": kwargs.get("size", "medium"),
                "rounded": kwargs.get("rounded", False)
            })
        elif element_type == "video":
            element.update({
                "video_id": kwargs.get("video_id", ""),
                "title": kwargs.get("title", "B站视频"),
                "width": kwargs.get("width", "100%"),
                "height": kwargs.get("height", "400px"),
                "autoplay": kwargs.get("autoplay", False)
            })
        elif element_type == "image":
            element.update({
                "src": kwargs.get("src", ""),
                "alt": kwargs.get("alt", "图片"),
                "caption": kwargs.get("caption", ""),
                "width": kwargs.get("width", "100%"),
                "align": kwargs.get("align", "center")
            })
        elif element_type == "code":
            element.update({
                "code": kwargs.get("code", "print('Hello World')"),
                "language": kwargs.get("language", "python"),
                "theme": kwargs.get("theme", "dark"),
                "show_line_numbers": kwargs.get("show_line_numbers", True)
            })
        elif element_type == "divider":
            element.update({
                "style": kwargs.get("style", "solid"),
                "color": kwargs.get("color", "#30363d"),
                "width": kwargs.get("width", "100%"),
                "thickness": kwargs.get("thickness", "1px")
            })
        
        return element

# ============================================
# 目录树组件 - 更新文字为浅蓝色
# ============================================
def render_directory_tree(structure):
    """渲染目录树侧边栏"""
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2 class="sidebar-title">📚 项目目录</h2>
        <p class="sidebar-subtitle">点击页面进行编辑</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 目录操作按钮
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📄 新建页面", 
                    use_container_width=True,
                    help="创建新的内容页面",
                    key="add_page_btn"):
            add_new_page("page")
    
    with col2:
        if st.button("📑 新建章节", 
                    use_container_width=True,
                    help="创建新的章节页面",
                    key="add_chapter_btn"):
            add_new_page("chapter")
    
    st.sidebar.markdown("---")
    
    # 目录列表
    if structure:
        # 封面页
        cover = structure["cover_page"]
        is_active = st.session_state.current_page and st.session_state.current_page.get("id") == cover.get("id")
        
        col_cover1, col_cover2 = st.sidebar.columns([4, 1])
        with col_cover1:
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"🏠 {cover.get('title', '封面')}", 
                        key=f"tree_{cover['id']}",
                        use_container_width=True,
                        type=btn_type,
                        help="编辑封面页"):
                select_page(cover)
        with col_cover2:
            if st.button("✏️", 
                        key=f"edit_cover",
                        help="编辑封面标题",
                        use_container_width=True):
                edit_page_title(cover["id"])
        
        # 页面列表
        if "pages" in structure and structure["pages"]:
            st.sidebar.markdown("### 📄 页面列表")
            
            for page in structure["pages"]:
                render_page_tree_item(page)
        else:
            st.sidebar.info("📭 还没有其他页面")
    
    # 项目操作
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ 项目操作", expanded=False):
        if st.button("📊 项目统计", use_container_width=True):
            show_project_stats()
        
        if st.button("🗂️ 导出项目", use_container_width=True):
            export_project()
        
        if st.button("🔄 重新加载", use_container_width=True):
            reload_project()
        
        if st.button("🗑️ 删除项目", use_container_width=True, type="secondary"):
            delete_project_confirm()

def render_page_tree_item(page, depth=0):
    """渲染页面树项目"""
    indent = "  " * depth
    icon = "📑" if page.get("type") == "chapter" else "📄"
    
    is_active = st.session_state.current_page and st.session_state.current_page.get("id") == page.get("id")
    
    col1, col2, col3 = st.sidebar.columns([3, 1, 1])
    
    with col1:
        btn_type = "primary" if is_active else "secondary"
        if st.button(
            f"{icon} {page.get('title', '未命名')}",
            key=f"tree_{page['id']}",
            use_container_width=True,
            type=btn_type,
            help=f"编辑页面: {page.get('title', '未命名')}"
        ):
            select_page(page)
    
    with col2:
        if st.button("✏️", 
                    key=f"edit_{page['id']}",
                    help="编辑页面标题",
                    use_container_width=True):
            edit_page_title(page["id"])
    
    with col3:
        if st.button("🗑️", 
                    key=f"del_{page['id']}",
                    help="删除此页面",
                    use_container_width=True,
                    type="secondary"):
            delete_page(page["id"])
    
    # 递归渲染子页面
    if "children" in page and page["children"]:
        for child in page["children"]:
            render_page_tree_item(child, depth + 1)

# ============================================
# 页面编辑器 - 更新文字为浅蓝色
# ============================================
def render_page_editor(page, structure):
    """渲染页面编辑器"""
    # 页面标题编辑
    if st.session_state.edit_page_title and st.session_state.edit_page_id == page["id"]:
        with st.form(f"edit_title_{page['id']}"):
            new_title = st.text_input("页面标题", value=page.get("title", ""), 
                                    key=f"title_input_{page['id']}")
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 保存标题", use_container_width=True):
                    page["title"] = new_title
                    st.session_state.edit_page_title = False
                    if save_project():
                        SessionStateManager.add_notification("标题已保存", "success")
                    st.rerun()
            
            with col_cancel:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state.edit_page_title = False
                    st.rerun()
    else:
        # 显示页面标题和编辑按钮
        col_title, col_edit = st.columns([4, 1])
        with col_title:
            st.markdown(f"## {page.get('title', '未命名页面')}")
        
        with col_edit:
            if st.button("✏️ 编辑标题", 
                        key=f"edit_current_title",
                        use_container_width=True,
                        help="编辑页面标题"):
                st.session_state.edit_page_title = True
                st.session_state.edit_page_id = page["id"]
                st.rerun()
    
    # 页面属性
    with st.expander("⚙️ 页面属性", expanded=False):
        col_type, col_order = st.columns(2)
        
        with col_type:
            page_type = st.selectbox(
                "页面类型",
                ["page", "chapter"],
                index=0 if page.get("type") == "page" else 1,
                format_func=lambda x: "📄 内容页面" if x == "page" else "📑 章节页面",
                key=f"page_type_{page['id']}"
            )
        
        with col_order:
            if "pages" in structure:
                page_index = next((i for i, p in enumerate(structure["pages"]) if p["id"] == page["id"]), -1)
                if page_index >= 0:
                    new_order = st.number_input(
                        "显示顺序",
                        min_value=1,
                        max_value=len(structure["pages"]),
                        value=page_index + 1,
                        key=f"page_order_{page['id']}"
                    )
                    
                    if new_order != page_index + 1:
                        # 重新排序
                        structure["pages"].pop(page_index)
                        structure["pages"].insert(new_order - 1, page)
        
        if st.button("💾 更新属性", key=f"update_attrs_{page['id']}", use_container_width=True):
            page["type"] = page_type
            if save_project():
                SessionStateManager.add_notification("页面属性已更新", "success")
                st.rerun()
    
    # 内容编辑工具栏
    st.markdown("---")
    st.markdown("### 🛠️ 添加内容")
    
    # 内容类型选择
    element_types = list(ContentElement.element_types.items())
    cols = st.columns(min(len(element_types), 5))
    
    for idx, (elem_type, elem_info) in enumerate(element_types):
        with cols[idx % len(cols)]:
            if st.button(
                f"{elem_info['icon']} {elem_info['name']}",
                key=f"add_{elem_type}_{page['id']}",
                use_container_width=True,
                help=f"添加{elem_info['name']}"
            ):
                add_content_element(elem_type)
    
    # 内容列表
    st.markdown("---")
    st.markdown("### 📝 页面内容")
    
    if "content" not in page or not page["content"]:
        st.info("""
        📭 此页面还没有内容。
        
        点击上面的按钮添加您的内容元素。
        """)
    else:
        # 显示所有内容元素
        for i, element in enumerate(page["content"]):
            render_content_element(element, page, i)
    
    # 实时预览
    st.markdown("---")
    with st.expander("👁️ 实时预览", expanded=True):
        with st.container():
            render_preview(page)

def render_content_element(element, page, index):
    """渲染内容元素编辑器"""
    element_type = element["type"]
    element_id = element["id"]
    
    with st.container():
        st.markdown('<div class="content-element">', unsafe_allow_html=True)
        
        # 元素头部
        col_header1, col_header2 = st.columns([5, 1])
        
        with col_header1:
            icon = ContentElement.get_element_icon(element_type)
            name = ContentElement.get_element_name(element_type)
            st.markdown(f"**{icon} {name}**")
        
        with col_header2:
            # 操作按钮
            col_ops1, col_ops2, col_ops3, col_ops4 = st.columns(4)
            
            with col_ops1:
                if st.button("⬆️", key=f"up_{element_id}", help="上移"):
                    if index > 0:
                        page["content"][index], page["content"][index-1] = page["content"][index-1], page["content"][index]
                        if save_project():
                            st.rerun()
            
            with col_ops2:
                if st.button("✏️", key=f"edit_{element_id}", help="编辑"):
                    st.session_state.edit_mode = True
                    st.session_state.edit_element_id = element_id
                    st.rerun()
            
            with col_ops3:
                if st.button("⬇️", key=f"down_{element_id}", help="下移"):
                    if index < len(page["content"]) - 1:
                        page["content"][index], page["content"][index+1] = page["content"][index+1], page["content"][index]
                        if save_project():
                            st.rerun()
            
            with col_ops4:
                if st.button("🗑️", key=f"del_{element_id}", help="删除"):
                    # 标记为待删除
                    st.session_state[f"pending_delete_{element_id}"] = True
                    st.rerun()

            # 如果处于待删除状态，显示确认/取消按钮
            if st.session_state.get(f"pending_delete_{element_id}"):
                st.warning(f"⚠️ 确认删除这个 {name} ?")
                ccol, ycol = st.columns([1,1])
                with ccol:
                    if st.button("取消", key=f"cancel_del_{element_id}"):
                        st.session_state[f"pending_delete_{element_id}"] = False
                        st.rerun()
                with ycol:
                    if st.button("删除", key=f"confirm_del_{element_id}"):
                        # 实际删除元素
                        try:
                            page["content"].pop(index)
                        except Exception:
                            pass
                        if save_project():
                            st.session_state[f"pending_delete_{element_id}"] = False
                            SessionStateManager.add_notification(f"{name}已删除", "success")
                            st.rerun()
                        else:
                            st.session_state[f"pending_delete_{element_id}"] = False
                            SessionStateManager.add_notification("删除失败", "error")
        
        # 元素预览 - 使用浅蓝色
        st.markdown("---")
        
        if element_type == "heading":
            level = element.get("level", 2)
            text = element.get("text", "")
            color = element.get("color", "#8ed1ff")
            st.markdown(f"<h{level} style='color: {color}; margin: 10px 0; border-bottom: 1px solid #30363d; padding-bottom: 0.3em;'>{text}</h{level}>", 
                      unsafe_allow_html=True)
        
        elif element_type == "paragraph":
            text = element.get("text", "")
            color = element.get("color", "#7cc5ff")
            background = element.get("background", "transparent")
            st.markdown(f"""
            <div style="color: {color}; background: {background}; padding: 15px; border-left: 3px solid #58a6ff; margin: 10px 0;">
                {text[:200]}{'...' if len(text) > 200 else ''}
            </div>
            """, unsafe_allow_html=True)
        
        elif element_type == "note":
            text = element.get("text", "")
            author = element.get("author", "")
            st.markdown(f"""
            <div style="color: #7cc5ff; background: rgba(56, 139, 253, 0.1); padding: 15px; margin: 10px 0; font-style: italic; border-left: 3px solid #58a6ff;">
                "{text[:150]}{'...' if len(text) > 150 else ''}"
                {f'<br><small style="color: #7cc5ff;">— {author}</small>' if author else ''}
            </div>
            """, unsafe_allow_html=True)
        
        elif element_type == "button":
            text = element.get("text", "点击这里")
            st.markdown(f"""
            <div style="display: inline-block; background: #238636; color: white; padding: 8px 16px; border-radius: 6px; margin: 10px 0; font-weight: 500; border: 1px solid #238636;">
                {text}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 编辑模式
        if st.session_state.edit_mode and st.session_state.edit_element_id == element_id:
            render_element_editor(element, page, index)

def render_element_editor(element, page, index):
    """渲染元素编辑器"""
    element_type = element["type"]
    
    with st.expander("✏️ 编辑内容", expanded=True):
        st.markdown('<div class="editor-form">', unsafe_allow_html=True)
        
        if element_type == "heading":
            col_text, col_level = st.columns([3, 1])
            with col_text:
                element["text"] = st.text_input("标题文字", value=element.get("text", ""))
            with col_level:
                element["level"] = st.selectbox("标题级别", [1, 2, 3, 4], 
                                              index=min(element.get("level", 2)-1, 3))
            
            col_color, col_align = st.columns(2)
            with col_color:
                element["color"] = st.color_picker("文字颜色", value=element.get("color", "#8ed1ff"))
            with col_align:
                element["align"] = st.selectbox("对齐方式", ["left", "center", "right"],
                                              index=["left", "center", "right"].index(
                                                  element.get("align", "left")))
        
        elif element_type == "paragraph":
            element["text"] = st.text_area("内容", value=element.get("text", ""), height=150)
            
            col_color, col_bg = st.columns(2)
            with col_color:
                element["color"] = st.color_picker("文字颜色", value=element.get("color", "#7cc5ff"))
            with col_bg:
                element["background"] = st.color_picker("背景颜色", value=element.get("background", "transparent"))
            
            element["align"] = st.selectbox("对齐方式", ["left", "center", "right", "justify"],
                                          index=["left", "center", "right", "justify"].index(
                                              element.get("align", "left")))
        
        elif element_type == "note":
            element["text"] = st.text_area("注释内容", value=element.get("text", ""), height=120)
            element["author"] = st.text_input("吐槽者", value=element.get("author", ""))
            
            col_color, col_bg = st.columns(2)
            with col_color:
                element["color"] = st.color_picker("文字颜色", value=element.get("color", "#7cc5ff"))
            with col_bg:
                element["background"] = st.color_picker("背景颜色", value=element.get("background", "rgba(56, 139, 253, 0.1)"))
        
        elif element_type == "button":
            col_text, col_url = st.columns(2)
            with col_text:
                element["text"] = st.text_input("按钮文字", value=element.get("text", "点击这里"))
            with col_url:
                element["url"] = st.text_input("链接地址", value=element.get("url", "#"))
            
            col_color, col_bg = st.columns(2)
            with col_color:
                element["color"] = st.color_picker("文字颜色", value=element.get("color", "#ffffff"))
            with col_bg:
                element["background"] = st.color_picker("背景颜色", value=element.get("background", "#238636"))
        
        elif element_type == "video":
            element["video_id"] = st.text_input("B站视频ID (BV号)", value=element.get("video_id", ""),
                                              help="例如：BV1xx411c7mD")
            element["title"] = st.text_input("视频标题", value=element.get("title", "B站视频"))
            
            col_width, col_height = st.columns(2)
            with col_width:
                element["width"] = st.text_input("宽度", value=element.get("width", "100%"))
            with col_height:
                element["height"] = st.text_input("高度", value=element.get("height", "400px"))
        
        # 保存/取消按钮
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("💾 保存修改", use_container_width=True, type="primary", key=f"save_{element['id']}"):
                st.session_state.edit_mode = False
                st.session_state.edit_element_id = None
                if save_project():
                    SessionStateManager.add_notification("修改已保存", "success")
                st.rerun()
        
        with col_cancel:
            if st.button("❌ 取消", use_container_width=True, key=f"cancel_{element['id']}"):
                st.session_state.edit_mode = False
                st.session_state.edit_element_id = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_preview(page):
    """渲染页面预览 - 使用浅蓝色"""
    if "content" not in page or not page["content"]:
        st.info("暂无内容")
        return
    
    # 创建预览容器
    st.markdown('<div class="preview-container markdown-body">', unsafe_allow_html=True)
    
    for element in page["content"]:
        if element["type"] == "heading":
            level = element.get("level", 2)
            text = element.get("text", "")
            color = element.get("color", "#8ed1ff")
            st.markdown(f"<h{level} style='color: {color}; margin: 15px 0; border-bottom: 1px solid #30363d; padding-bottom: 0.3em;'>{text}</h{level}>", 
                      unsafe_allow_html=True)
        
        elif element["type"] == "paragraph":
            text = element.get("text", "")
            color = element.get("color", "#7cc5ff")
            background = element.get("background", "transparent")
            align = element.get("align", "left")
            
            text_with_breaks = text.replace('\n', '<br>')
            st.markdown(f"""
            <div style="color: {color}; background: {background}; padding: 16px; margin: 15px 0; text-align: {align}; line-height: 1.6; border-left: 3px solid #58a6ff;">
                {text_with_breaks}
            </div>
            """, unsafe_allow_html=True)
        
        elif element["type"] == "note":
            text = element.get("text", "")
            author = element.get("author", "")
            color = element.get("color", "#7cc5ff")
            background = element.get("background", "rgba(56, 139, 253, 0.1)")
            
            author_html = f'<div style="text-align: right; color: #7cc5ff; margin-top: 10px; font-style: italic;">— {author}</div>' if author else ''
            
            st.markdown(f"""
            <div style="background: {background}; color: {color}; padding: 16px; margin: 15px 0; border-left: 3px solid #58a6ff; font-style: italic;">
                <div style="margin-bottom: 10px;">"{text}"</div>
                {author_html}
            </div>
            """, unsafe_allow_html=True)
        
        elif element["type"] == "button":
            text = element.get("text", "点击这里")
            url = element.get("url", "#")
            color = element.get("color", "#ffffff")
            background = element.get("background", "#238636")
            
            st.markdown(f"""
            <a href="{url}" target="_blank" style="display: inline-block; background: {background}; color: {color}; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 500; margin: 12px 0; border: 1px solid {background};">
                {text}
            </a>
            """, unsafe_allow_html=True)
        
        elif element["type"] == "video":
            video_id = element.get("video_id", "")
            title = element.get("title", "B站视频")
            
            if video_id:
                st.markdown(f"""
                <div style="margin: 15px 0;">
                    <h4 style="color: #8ed1ff; margin-bottom: 10px;">{title}</h4>
                    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 6px; background: #000; border: 1px solid #30363d;">
                        <iframe src="https://player.bilibili.com/player.html?bvid={video_id}&page=1"
                                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
                                allowfullscreen>
                        </iframe>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("请添加B站视频ID")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 主页 - 更新文字为浅蓝色
# ============================================
def render_home():
    """渲染主页"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 头部
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">📖 网页手册创建器</h1>
        <p class="app-subtitle">
            一个强大、易用的网页手册制作工具，采用GitHub风格的深色主题。
            无需编程知识即可创建专业级别的响应式网页。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    project_manager = ProjectManager()
    
    # 功能特性
    st.markdown("### ✨ 核心特性")
    cols = st.columns(3)
    
    features = [
        ("🎨 GitHub 风格", "深色主题，现代化UI设计", "#7cc5ff", "采用GitHub深色主题设计，提供专业视觉体验"),
        ("📱 响应式布局", "完美适配各种设备", "#8ed1ff", "自动适应各种屏幕尺寸，提供最佳浏览体验"),
        ("⚡ 高性能", "优化的代码结构，极速加载", "#7cc5ff", "轻量级代码，快速加载，提升用户体验"),
        ("🔧 易于使用", "直观的操作界面，简单编辑", "#8ed1ff", "无需编程知识，简单点击即可创建专业网页"),
        ("📤 一键部署", "生成可部署的HTML文件", "#7cc5ff", "支持GitHub Pages等主流部署平台"),
        ("🔄 实时预览", "编辑时即时查看效果", "#8ed1ff", "实时预览功能，确保设计符合预期")
    ]
    
    for idx, (title, desc, color, detail) in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon" style="color: {color};">{title.split()[0]}</div>
                <h3 class="feature-title">{title}</h3>
                <p class="feature-desc">{desc}</p>
                <p style="color: #7cc5ff; font-size: 0.95rem; line-height: 1.5;">{detail}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 标签页
    tab1, tab2, tab3 = st.tabs(["🚀 创建项目", "📂 我的项目", "📖 使用指南"])
    
    with tab1:
        # 创建项目表单
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 开始新的项目")
            
            with st.form("new_project_form", clear_on_submit=True):
                project_name = st.text_input(
                    "项目名称 *",
                    placeholder="例如：Python教程",
                    help="请输入项目名称，建议使用简洁明了的名称"
                )
                
                project_desc = st.text_area(
                    "项目描述",
                    placeholder="项目的详细描述...",
                    height=120,
                    help="描述项目的用途和主要内容"
                )
                
                # 项目设置
                with st.expander("⚙️ 高级设置", expanded=False):
                    col_setting1, col_setting2 = st.columns(2)
                    with col_setting1:
                        st.checkbox("启用动画效果", value=True, key="enable_animations_home")
                        st.checkbox("显示返回顶部按钮", value=True, key="show_back_to_top_home")
                    with col_setting2:
                        st.selectbox("默认主题", ["dark", "light"], key="default_theme_home", index=0)
                        st.checkbox("自动保存", value=True, key="auto_save_home")
                
                col_submit, col_clear = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button(
                        "🎯 创建项目",
                        use_container_width=True,
                        type="primary"
                    )
                with col_clear:
                    if st.form_submit_button("🗑️ 清空", use_container_width=True, type="secondary"):
                        st.rerun()
                
                if submitted:
                    if project_name:
                        with st.spinner("正在创建项目..."):
                            success, message = project_manager.create_project(project_name, project_desc)
                            if success:
                                st.success("✅ 项目创建成功！正在加载...")
                                SessionStateManager.add_notification("项目创建成功", "success")
                                time.sleep(1)
                                
                                # 加载项目
                                success, result = project_manager.load_project(project_name)
                                if success:
                                    st.session_state.current_project = result
                                    st.session_state.project_structure = result["structure"]
                                    st.session_state.current_page = result["structure"]["cover_page"]
                                    st.session_state.active_tab = "editor"
                                    st.session_state.project_loaded = True
                                    st.rerun()
                            else:
                                st.error(f"❌ {message}")
                                SessionStateManager.add_notification(f"创建失败: {message}", "error")
                    else:
                        st.warning("⚠️ 请输入项目名称")
                        SessionStateManager.add_notification("请输入项目名称", "warning")
        
        with col2:
            # 快速开始指南
            st.markdown("### ⚡ 快速开始")
            st.markdown("""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; color: #7cc5ff;">
                <ol style="color: #7cc5ff; padding-left: 24px;">
                    <li><strong>输入项目名称</strong></li>
                    <li><strong>添加项目描述</strong></li>
                    <li><strong>点击创建按钮</strong></li>
                    <li><strong>开始编辑内容</strong></li>
                    <li><strong>保存并发布</strong></li>
                </ol>
                
                <hr style="border-color: #30363d;">
                
                <div style="color: #7cc5ff; font-size: 0.95rem;">
                    <p><strong>💡 提示:</strong></p>
                    <ul style="padding-left: 20px;">
                        <li>项目名称建议简短明确</li>
                        <li>描述可以帮助您后期管理</li>
                        <li>高级设置可以后续修改</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📂 我的项目")
        
        projects = project_manager.list_projects()
        
        if not projects:
            st.info("""
            📭 还没有任何项目。
            
            点击上方的"创建项目"标签开始您的第一个项目！
            """)
        else:
            # 项目统计
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            with col_stats1:
                st.metric("项目总数", len(projects))
            with col_stats2:
                completed = sum(1 for p in projects if p["has_html"])
                st.metric("已生成HTML", completed)
            with col_stats3:
                total_size = sum(p["size"] for p in projects)
                st.metric("总大小", project_manager.format_size(total_size))
            with col_stats4:
                if projects:
                    latest = max(projects, key=lambda x: x["config"].get("last_modified", ""))
                    st.metric("最近更新", latest["name"][:10] + "...")
            
            # 项目列表
            st.markdown("---")
            
            for project in projects:
                with st.container():
                    st.markdown(f"""
                    <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin: 10px 0; color: #7cc5ff;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                            <div>
                                <h4 style="color: #8ed1ff; margin: 0 0 8px 0; display: flex; align-items: center;">
                                    <span style="background: rgba(56, 139, 253, 0.1); color: #7cc5ff; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; margin-right: 10px; border: 1px solid rgba(56, 139, 253, 0.3);">
                                        v{project['config'].get('version', '1.0')}
                                    </span>
                                    {project['name']}
                                </h4>
                                <p style="color: #7cc5ff; margin: 0 0 12px 0; font-size: 0.95rem;">
                                    {project['config'].get('description', '无描述')}
                                </p>
                            </div>
                            <div style="display: flex; gap: 8px;">
                                <button onclick="openProject('{project['name']}')" style="background: rgba(56, 139, 253, 0.1); border: 1px solid rgba(56, 139, 253, 0.3); color: #7cc5ff; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.9rem;"
                                        onmouseover="this.style.background='rgba(56, 139, 253, 0.2)'"
                                        onmouseout="this.style.background='rgba(56, 139, 253, 0.1)'">
                                    打开
                                </button>
                            </div>
                        </div>
                        <div style="display: flex; gap: 16px; margin-top: 12px; font-size: 0.85rem; color: #7cc5ff;">
                            <span>
                                <i class="fas fa-calendar"></i> {project['config'].get('created_at', '').split('T')[0]}
                            </span>
                            <span>
                                <i class="fas fa-file-alt"></i> {project_manager.format_size(project['size'])}
                            </span>
                            <span>
                                <i class="fas fa-file"></i> {project['page_count']}页
                            </span>
                            <span>
                                {'✅ 已生成HTML' if project["has_html"] else '⏳ 未生成HTML'}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📖 使用指南")
        
        guide_steps = [
            ("1️⃣ 创建项目", "填写项目名称和描述，点击创建按钮"),
            ("2️⃣ 添加页面", "在左侧目录中点击『新建页面』或『新建章节』"),
            ("3️⃣ 编辑内容", "在右侧编辑区域添加和修改内容元素"),
            ("4️⃣ 预览效果", "实时预览区域查看最终效果"),
            ("5️⃣ 保存项目", "点击保存按钮生成HTML文件"),
            ("6️⃣ 部署使用", "将生成的HTML文件部署到GitHub Pages或其他服务器")
        ]
        
        for step, description in guide_steps:
            with st.container():
                st.markdown(f"""
                <div style="background: #161b22; border: 1px solid #30363d; border-left: 4px solid #7cc5ff; border-radius: 0 6px 6px 0; padding: 16px; margin: 10px 0; color: #7cc5ff;">
                    <h4 style="color: #8ed1ff; margin: 0 0 8px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="background: #7cc5ff; color: #0d1117; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold;">
                            {step.split()[0]}
                        </span>
                        {step}
                    </h4>
                    <p style="color: #7cc5ff; margin: 0; padding-left: 42px;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 常见问题
        with st.expander("❓ 常见问题", expanded=False):
            faqs = [
                ("Q: 生成的HTML文件在哪里？", "A: 在项目文件夹下的index.html文件中"),
                ("Q: 如何部署到GitHub Pages？", "A: 将整个项目文件夹上传到GitHub仓库，在设置中启用GitHub Pages功能"),
                ("Q: 支持哪些内容类型？", "A: 支持标题、段落、注释、按钮、B站视频、图片、代码块等多种内容类型"),
                ("Q: 可以导出为其他格式吗？", "A: 目前只支持导出为HTML格式，后续会支持PDF导出"),
                ("Q: 数据会保存到哪里？", "A: 所有数据都保存在本地项目的文件夹中，不会上传到任何服务器")
            ]
            
            for question, answer in faqs:
                st.markdown(f"**{question}**")
                st.markdown(f"{answer}")
                st.markdown("---")
        
        # 快捷键参考
        with st.expander("⌨️ 键盘快捷键", expanded=False):
            shortcuts = [
                ("Ctrl/Cmd + B", "切换侧边栏"),
                ("Ctrl/Cmd + K 或 /", "打开搜索"),
                ("ESC", "关闭搜索或侧边栏"),
                ("← 或 PageUp", "上一页"),
                ("→ 或 PageDown", "下一页"),
                ("T", "切换目录"),
                ("Home", "返回顶部"),
                ("空格键", "下一页")
            ]
            
            for shortcut, description in shortcuts:
                col_shortcut, col_desc = st.columns([1, 3])
                with col_shortcut:
                    st.code(shortcut, language="")
                with col_desc:
                    st.markdown(description)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 项目编辑器主页面 - 更新文字为浅蓝色
# ============================================
def render_project_editor():
    """渲染项目编辑器页面"""
    # 显示通知
    SessionStateManager.show_notifications()
    
    project = st.session_state.current_project
    structure = st.session_state.project_structure
    current_page = st.session_state.current_page
    
    if not project or not structure or not current_page:
        st.error("项目加载失败，请返回主页重新加载")
        if st.button("返回主页"):
            st.session_state.active_tab = "home"
            st.rerun()
        return
    
    # 顶部工具栏
    st.markdown(f"""
    <div style="background: #161b22; border: 1px solid #30363d; border-left: 4px solid #7cc5ff; border-radius: 0 6px 6px 0; padding: 20px; margin-bottom: 24px; color: #7cc5ff;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h2 style="color: #8ed1ff; margin: 0; display: flex; align-items: center; gap: 12px;">
                    <span style="background: rgba(124, 197, 255, 0.1); color: #7cc5ff; padding: 6px 16px; border-radius: 20px; font-size: 1rem; border: 1px solid rgba(124, 197, 255, 0.3);">
                        📝 编辑中
                    </span>
                    {project['name']}
                </h2>
                <p style="color: #7cc5ff; margin: 6px 0 0 0; font-size: 0.95rem;">
                    {project['config'].get('description', '')}
                </p>
            </div>
            <div style="display: flex; gap: 10px;">
                <button onclick="window.location.href='?tab=home'" style="background: #21262d; border: 1px solid #30363d; color: #7cc5ff; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: all 0.2s; display: flex; align-items: center; gap: 6px;"
                        onmouseover="this.style.background='#30363d'"
                        onmouseout="this.style.background='#21262d'">
                    <i class="fas fa-home"></i> 主页
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 操作统计
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    with col_stats1:
        total_pages = len(structure.get('pages', [])) + 1
        st.metric("📄 总页面数", total_pages)
    
    with col_stats2:
        total_elements = sum(len(page.get('content', [])) for page in [structure['cover_page']] + structure.get('pages', []))
        st.metric("📝 内容元素", total_elements)
    
    with col_stats3:
        word_count = HTMLGenerator.calculate_word_count(structure)
        st.metric("📊 总字数", f"{word_count:,}")
    
    with col_stats4:
        if project.get('html_path') and project['html_path'].exists():
            file_size = project['html_path'].stat().st_size
            st.metric("💾 HTML大小", f"{file_size/1024:.1f}KB")
        else:
            st.metric("🚫 HTML状态", "未生成")
    
    # 主要编辑区域
    col_left, col_right = st.columns([1, 2], gap="large")
    
    with col_left:
        # 目录管理
        render_directory_tree(structure)
        
        # 项目设置
        with st.expander("⚙️ 项目设置", expanded=False):
            with st.form("project_settings_form"):
                structure['title'] = st.text_input("网站标题", value=structure.get('title', ''))
                structure['description'] = st.text_area("网站描述", value=structure.get('description', ''))
                
                # 主题设置
                st.markdown("### 🎨 主题设置")
                theme_col1, theme_col2 = st.columns(2)
                with theme_col1:
                    structure['config']['theme'] = st.selectbox(
                        "主题模式",
                        ["dark", "light", "auto"],
                        index=["dark", "light", "auto"].index(structure['config'].get('theme', 'dark'))
                    )
                with theme_col2:
                    structure['config']['animations'] = st.checkbox(
                        "启用动画",
                        value=structure['config'].get('animations', True)
                    )
                
                # 功能设置
                st.markdown("### 🔧 功能设置")
                col_func1, col_func2 = st.columns(2)
                with col_func1:
                    structure['config']['sidebar_collapsible'] = st.checkbox(
                        "可折叠侧边栏",
                        value=structure['config'].get('sidebar_collapsible', True)
                    )
                with col_func2:
                    structure['config']['show_back_to_top'] = st.checkbox(
                        "返回顶部按钮",
                        value=structure['config'].get('show_back_to_top', True)
                    )
                
                if st.form_submit_button("💾 保存设置", use_container_width=True, type="primary"):
                    if save_project():
                        st.success("✅ 项目设置已保存")
                        SessionStateManager.add_notification("项目设置已保存", "success")
    
    with col_right:
        if current_page:
            # 页面编辑区
            render_page_editor(current_page, structure)
    
    # 底部操作栏
    st.markdown("---")
    col_bottom1, col_bottom2, col_bottom3, col_bottom4 = st.columns(4)
    
    with col_bottom1:
        if st.button("💾 保存项目", 
                    use_container_width=True, 
                    type="primary",
                    help="保存项目并生成HTML文件"):
            if save_project():
                st.success("✅ 项目已保存并生成HTML文件！")
                SessionStateManager.add_notification("项目已保存", "success")
                time.sleep(1)
                st.rerun()
    
    with col_bottom2:
        if st.button("📤 导出HTML", 
                    use_container_width=True,
                    help="导出完整的HTML文件"):
            if export_html():
                st.success("✅ HTML文件已生成！")
                SessionStateManager.add_notification("HTML文件已生成", "success")
    
    with col_bottom3:
        if st.button("🔄 重新加载", 
                    use_container_width=True,
                    help="重新加载项目数据"):
            success, result = ProjectManager().load_project(project['name'])
            if success:
                st.session_state.current_project = result
                st.session_state.project_structure = result["structure"]
                st.session_state.current_page = result["structure"]["cover_page"]
                st.success("✅ 项目已重新加载")
                SessionStateManager.add_notification("项目已重新加载", "success")
                st.rerun()
    
    with col_bottom4:
        if st.button("🏠 返回主页", 
                    use_container_width=True,
                    type="secondary",
                    help="返回主页"):
            st.session_state.active_tab = "home"
            st.session_state.current_project = None
            st.rerun()

# ============================================
# 项目操作函数
# ============================================
def save_project():
    """保存项目并生成HTML文件"""
    if not st.session_state.current_project:
        return False
    
    try:
        SessionStateManager.start_operation("保存项目")
        
        project = st.session_state.current_project
        project_path = project["path"]
        
        # 更新最后修改时间
        project["config"]["last_modified"] = datetime.now().isoformat()
        st.session_state.project_structure["config"] = project["config"]["settings"]
        
        # 保存项目配置
        with open(project_path / "project.json", 'w', encoding='utf-8') as f:
            json.dump(project["config"], f, ensure_ascii=False, indent=2)
        
        # 保存项目结构
        with open(project_path / "structure.json", 'w', encoding='utf-8') as f:
            json.dump(st.session_state.project_structure, f, ensure_ascii=False, indent=2)
        
        # 生成HTML文件
        html_generator = HTMLGenerator()
        html_content = html_generator.generate_html(st.session_state.project_structure)
        
        # 保存HTML文件
        html_file_path = project_path / "index.html"
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 更新项目信息
        project["html_path"] = html_file_path
        
        # 创建备份
        project_manager = ProjectManager()
        project_manager.create_backup(project["name"], st.session_state.project_structure)
        
        st.session_state.last_save_time = datetime.now()
        SessionStateManager.end_operation()
        
        return True
        
    except Exception as e:
        SessionStateManager.end_operation()
        st.error(f"保存失败: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False

def export_html():
    """导出HTML文件"""
    if not st.session_state.current_project:
        return False
    
    try:
        SessionStateManager.start_operation("导出HTML")
        
        project = st.session_state.current_project
        project_path = project["path"]
        
        # 生成HTML文件
        html_generator = HTMLGenerator()
        html_content = html_generator.generate_html(st.session_state.project_structure)
        
        # 保存HTML文件
        html_file_path = project_path / "index.html"
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 显示成功信息
        SessionStateManager.end_operation()
        
        return True
        
    except Exception as e:
        SessionStateManager.end_operation()
        st.error(f"导出失败: {str(e)}")
        return False

def show_project_stats():
    """显示项目统计"""
    if not st.session_state.current_project:
        return
    
    project = st.session_state.current_project
    structure = st.session_state.project_structure
    
    # 计算统计信息
    total_pages = len(structure.get('pages', [])) + 1
    total_elements = sum(len(page.get('content', [])) for page in [structure['cover_page']] + structure.get('pages', []))
    word_count = HTMLGenerator.calculate_word_count(structure)
    
    # 显示统计信息
    st.info(f"""
    ### 📊 项目统计
    
    **基本信息:**
    - 项目名称: {project['name']}
    - 创建时间: {project['config'].get('created_at', '').split('T')[0]}
    - 最后修改: {project['config'].get('last_modified', '').split('T')[0]}
    
    **内容统计:**
    - 总页面数: {total_pages}
    - 内容元素: {total_elements}
    - 总字数: {word_count:,}
    - 文件大小: {ProjectManager().format_size(project_path.stat().st_size) if project['path'].exists() else '未知'}
    
    **HTML文件:**
    - 状态: {'✅ 已生成' if project.get('html_path') and project['html_path'].exists() else '❌ 未生成'}
    - 位置: {project['path'] / 'index.html' if project.get('html_path') else '未生成'}
    """)

def export_project():
    """导出整个项目"""
    if not st.session_state.current_project:
        return
    
    project = st.session_state.current_project
    
    # 创建导出包
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = export_dir / f"{project['name']}_{timestamp}.zip"
    
    try:
        import zipfile
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加项目文件
            for file_path in project['path'].rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project['path'])
                    zipf.write(file_path, arcname)
        
        st.success(f"项目已导出到: {export_path}")
        SessionStateManager.add_notification("项目导出成功", "success")
        
    except Exception as e:
        st.error(f"导出失败: {str(e)}")
        SessionStateManager.add_notification("导出失败", "error")

def reload_project():
    """重新加载项目"""
    if not st.session_state.current_project:
        return
    
    project_name = st.session_state.current_project["name"]
    project_manager = ProjectManager()
    
    success, result = project_manager.load_project(project_name)
    if success:
        st.session_state.current_project = result
        st.session_state.project_structure = result["structure"]
        st.session_state.current_page = result["structure"]["cover_page"]
        SessionStateManager.add_notification("项目已重新加载", "success")
        st.rerun()
    else:
        SessionStateManager.add_notification(f"重新加载失败: {result}", "error")

def delete_project_confirm():
    """确认删除项目"""
    if not st.session_state.current_project:
        return
    
    project_name = st.session_state.current_project["name"]
    
    st.warning(f"⚠️  确定要删除项目 '{project_name}' 吗？")
    
    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("🗑️ 确认删除", type="secondary", use_container_width=True):
            project_manager = ProjectManager()
            success, message = project_manager.delete_project(project_name)
            if success:
                st.success(message)
                SessionStateManager.add_notification("项目已删除", "success")
                st.session_state.active_tab = "home"
                st.session_state.current_project = None
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
                SessionStateManager.add_notification(f"删除失败: {message}", "error")
    
    with col_cancel:
        if st.button("❌ 取消", use_container_width=True):
            st.rerun()

# ============================================
# 主应用入口
# ============================================
def main():
    # 加载CSS
    load_css()
    
    # 初始化会话状态
    SessionStateManager.initialize()
    
    # 显示通知
    SessionStateManager.show_notifications()
    
    # 根据当前状态渲染相应页面
    try:
        if st.session_state.active_tab == "home" or not st.session_state.current_project:
            render_home()
        else:
            render_project_editor()
    except Exception as e:
        st.error(f"应用程序错误: {str(e)}")
        st.info("请尝试刷新页面或返回主页重新开始")
        
        col_refresh, col_home = st.columns(2)
        with col_refresh:
            if st.button("🔄 刷新页面", use_container_width=True):
                st.rerun()
        with col_home:
            if st.button("🏠 返回主页", use_container_width=True):
                st.session_state.active_tab = "home"
                st.session_state.current_project = None
                st.rerun()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"应用程序启动失败: {str(e)}")
        st.info("请确保所有依赖已正确安装，并检查文件权限")
        st.code("pip install streamlit", language="bash")