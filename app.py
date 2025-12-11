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
import html
import streamlit.components.v1 as components
import re
import traceback
import sys
from pathlib import Path as _Path

# Safe rerun helper to support multiple Streamlit versions
def safe_rerun():
    """Try to rerun the Streamlit script in a compatible way.
    If Streamlit provides experimental_rerun() or rerun(), call it.
    Otherwise attempt a harmless fallback that nudges a rerender.
    """
    try:
        if hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
            return
        if hasattr(st, 'rerun'):
            st.rerun()
            return
    except Exception:
        pass

    # Fallback: toggle a session_state key and try to set query params to force redraw
    try:
        key = '_copilot_force_rerun'
        st.session_state[key] = not st.session_state.get(key, False)
        try:
            if hasattr(st, 'experimental_set_query_params'):
                st.experimental_set_query_params(_r=int(time.time() * 1000))
        except Exception:
            pass
    except Exception:
        # Last resort: call st.stop() to end current run gracefully
        try:
            st.stop()
        except Exception:
            pass

    # -------------------------
    # 错误日志记录工具
    # -------------------------
    LOG_DIR = _Path("logs")
    LOG_DIR.mkdir(exist_ok=True)
    LOG_FILE = LOG_DIR / "streamlit_errors.log"

    def log_error(message: str):
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as lf:
                lf.write(f"\n=== {datetime.now().isoformat()} ===\n")
                lf.write(message)
                lf.write("\n")
        except Exception:
            # 不要在记录失败时打断主流程
            pass

    # 捕获未处理异常并记录
    def _global_excepthook(exc_type, exc_value, exc_tb):
        try:
            tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
            log_error(tb)
        except Exception:
            pass

    sys.excepthook = _global_excepthook

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
# 自定义CSS（已由 change.py 的 GitHub 深色主题全量替换）
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
        overflow-y: auto;
        overflow-x: hidden;  /* 移除横向滚动条 */
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
        color: #7cc5ff !important;  /* 改為浅蓝色 */
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
            'selected_theme': 'light',
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
# HTML生成器类
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
            </div>
            
            <div class="directory-tree" role="tree">
                <div class="tree-item cover-item" data-page="cover" role="treeitem" aria-selected="true">
                    <i class="fas fa-home"></i>
                    <span>🏠 {cover_title}</span>
                </div>
                {pages_html}
            </div>
        </nav>
        
        <!-- 主内容区 -->
        <main class="content" id="content">
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
        cover_title = structure["cover_page"].get("title", "封面")
        
        # 计算字数
        word_count = HTMLGenerator.calculate_word_count(structure)
        
        # 生成各部分内容
        css = HTMLGenerator.generate_css()
        additional_css = HTMLGenerator.generate_additional_css()
        description_html = f'<p class="sidebar-description">{description}</p>' if description else ''
        pages_html = HTMLGenerator.generate_pages_html(structure["pages"])
        pages_content = HTMLGenerator.generate_pages_content(structure["pages"])
        cover_content = HTMLGenerator.generate_page_content(structure["cover_page"])
        javascript = HTMLGenerator.generate_javascript()
        additional_js = HTMLGenerator.generate_additional_js()
        
        # 格式化HTML
        html = html_template.format(
            title=title,
            description=description,
            description_html=description_html,
            cover_title=cover_title,
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
            # 以字符数为准，去掉空白（空格与换行），更适合中文统计
            if not s:
                return 0
            return len(s.replace('\n', '').replace(' ', ''))

        # 统计封面页
        if "content" in structure.get("cover_page", {}):
            for element in structure["cover_page"]["content"]:
                if element.get("type") in ["heading", "paragraph", "note"]:
                    text = element.get("text", "")
                    word_count += chars_count(text)

        # 统计其他页面
        for page in structure.get("pages", []):
            if "content" in page:
                for element in page["content"]:
                    if element.get("type") in ["heading", "paragraph", "note"]:
                        text = element.get("text", "")
                        word_count += chars_count(text)

        return word_count
    
    @staticmethod
    def generate_css():
        """生成CSS样式 - 固定深色主题"""
        bg_color = "#0f172a"
        text_color = "#f1f5f9"
        sidebar_bg = "#1e293b"
        card_bg = "#334155"
        border_color = "#475569"
        code_bg = "#1e293b"
        primary_color = "#667eea"
        secondary_color = "#764ba2"
        font_family = "Inter, 'Microsoft YaHei', sans-serif"
        
        return f"""
        :root {{
            --primary-color: {primary_color};
            --secondary-color: {secondary_color};
            --accent-color: #f093fb;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --info-color: #3b82f6;
            
            --bg-color: {bg_color};
            --text-color: {text_color};
            --sidebar-bg: {sidebar_bg};
            --card-bg: {card_bg};
            --border-color: {border_color};
            --code-bg: {code_bg};
            
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            
            --radius-sm: 0.5rem;
            --radius-md: 0.75rem;
            --radius-lg: 1rem;
            --radius-xl: 1.5rem;
            --radius-2xl: 2rem;
            
            --spacing-xs: 0.5rem;
            --spacing-sm: 0.75rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;
            --spacing-2xl: 3rem;
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
            font-family: {font_family};
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.7;
            transition: all 0.3s ease;
            overflow-x: hidden;
            min-height: 100vh;
            position: relative;
        }}
        
        /* 容器布局 */
        .container {{
            display: flex;
            min-height: 100vh;
            position: relative;
            max-width: 1800px;
            margin: 0 auto;
        }}
        
        /* 侧边栏样式 */
        .sidebar {{
            width: 320px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            overflow-y: auto;
            z-index: 1000;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-xl);
            display: flex;
            flex-direction: column;
            padding: 2.5rem;
        }}
        
        .sidebar.hidden {{
            transform: translateX(-100%);
            box-shadow: none;
        }}
        
        /* 侧边栏头部 */
        .sidebar-header {{
            position: relative;
            padding-bottom: 2rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        }}
        
        .close-sidebar {{
            position: absolute;
            top: 0;
            right: 0;
            background: transparent;
            color: var(--text-color);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            transition: all 0.3s ease;
            opacity: 0.7;
        }}
        
        .close-sidebar:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--primary-color);
            opacity: 1;
            transform: rotate(90deg);
        }}
        
        .sidebar-title {{
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            line-height: 1.2;
        }}
        
        .sidebar-description {{
            font-size: 1.05rem;
            color: var(--text-color);
            opacity: 0.8;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }}
        
        /* 目录树 */
        .directory-tree {{
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;  /* 移除横向滚动条 */
            padding-right: 0.5rem;
        }}
        
        .tree-item {{
            padding: 1rem 1.25rem;
            margin: 0.75rem 0;
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 1rem;
            color: var(--text-color);
            font-size: 1.05rem;
            border-left: 4px solid transparent;
            background: rgba(255, 255, 255, 0.05);
            position: relative;
            overflow: hidden;
            font-weight: 500;
        }}
        
        .tree-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, rgba(var(--primary-color-rgb), 0.15), rgba(var(--secondary-color-rgb), 0.08));
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .tree-item:hover {{
            transform: translateX(10px);
            border-left-color: var(--primary-color);
            box-shadow: var(--shadow-md);
        }}
        
        .tree-item:hover::before {{
            opacity: 1;
        }}
        
        .tree-item.active {{
            background: linear-gradient(90deg, rgba(var(--primary-color-rgb), 0.2), rgba(var(--secondary-color-rgb), 0.1));
            border-left-color: var(--primary-color);
            color: var(--text-color);
            font-weight: 700;
            box-shadow: var(--shadow-md);
            transform: translateX(10px);
        }}
        
        .tree-item.active::before {{
            opacity: 1;
        }}
        
        .tree-item i {{
            font-size: 1.1rem;
            width: 24px;
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .tree-item:hover i {{
            transform: scale(1.2);
        }}
        
        /* 侧边栏切换按钮 */
        .sidebar-toggle {{
            position: fixed;
            top: 2rem;
            left: 2rem;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--radius-lg);
            width: 60px;
            height: 60px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            z-index: 999;
            box-shadow: var(--shadow-xl);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
            animation: fadeIn 0.5s ease 0.3s forwards;
        }}
        
        .sidebar.hidden ~ .sidebar-toggle {{
            opacity: 1;
            transform: translateX(0);
            animation: bounceInLeft 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }}
        
        .sidebar:not(.hidden) ~ .sidebar-toggle {{
            opacity: 0;
            pointer-events: none;
        }}
        
        .sidebar-toggle:hover {{
            background: var(--secondary-color);
            transform: scale(1.1) rotate(90deg);
            box-shadow: var(--shadow-2xl);
        }}
        
        @keyframes fadeIn {{
            to {{ opacity: 1; }}
        }}
        
        @keyframes bounceInLeft {{
            0% {{
                opacity: 0;
                transform: translateX(-50px);
            }}
            60% {{
                opacity: 1;
                transform: translateX(10px);
            }}
            80% {{
                transform: translateX(-5px);
            }}
            100% {{
                transform: translateX(0);
            }}
        }}
        
        /* 内容区域 */
        .content {{
            flex: 1;
            margin-left: 320px;
            padding: 3rem 4rem;
            min-height: 100vh;
            background: var(--bg-color);
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .sidebar.hidden ~ .content {{
            margin-left: 0;
            padding-left: 6rem;
        }}
        
        /* 页面样式 */
        .page {{
            max-width: 900px;
            margin: 0 auto;
            display: none;
            animation: fadeInUp 0.5s ease-out;
            padding-bottom: 4rem;
        }}
        
        .page.active {{
            display: block;
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .page-title {{
            font-size: 3.5rem;
            font-weight: 900;
            color: var(--text-color);
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 3px solid var(--primary-color);
            position: relative;
            line-height: 1.2;
        }}
        
        .page-title::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 150px;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }}
        
        /* 内容元素 */
        .element {{
            margin: 2.5rem 0;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.5s ease;
        }}
        
        .element.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        .heading {{
            color: var(--text-color);
            margin: 1.5rem 0;
            font-weight: 700;
            line-height: 1.3;
        }}
        
        .heading-1 {{ 
            font-size: 2.8rem;
            margin-top: 3rem;
        }}
        
        .heading-2 {{ 
            font-size: 2.2rem;
            margin-top: 2.5rem;
        }}
        
        .heading-3 {{ 
            font-size: 1.8rem;
            margin-top: 2rem;
        }}
        
        .heading-4 {{ 
            font-size: 1.5rem;
            margin-top: 1.5rem;
        }}
        
        .paragraph {{
            line-height: 1.8;
            font-size: 1.15rem;
            color: var(--text-color);
            padding: 1.5rem 2rem;
            border-radius: var(--radius-lg);
            margin: 1.5rem 0;
            background: var(--card-bg);
            border-left: 4px solid var(--primary-color);
            box-shadow: var(--shadow-sm);
        }}
        
        .note {{
            background: var(--card-bg);
            border-left: 4px solid var(--primary-color);
            padding: 2rem 2.5rem;
            border-radius: var(--radius-lg);
            margin: 2rem 0;
            position: relative;
            font-style: italic;
            box-shadow: var(--shadow-md);
        }}
        
        .note::before {{
            content: '"';
            font-size: 4rem;
            color: var(--primary-color);
            opacity: 0.2;
            position: absolute;
            top: 0.5rem;
            left: 1rem;
            font-family: Georgia, serif;
        }}
        
        .note-content {{
            color: ar(--gh-light-blue) !important;
            font-size: 1.1rem;
            position: relative;
            z-index: 1;
            line-height: 1.7;
        }}
        
        .note-author {{
            text-align: right;
            color: ar(--gh-light-blue) !important;
            opacity: 0.7;
            font-size: 1rem;
            margin-top: 1.5rem;
            font-style: italic;
            font-weight: 500;
        }}
        
        .button {{
            display: inline-block;
            padding: 1rem 2.5rem;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            text-decoration: none;
            border-radius: var(--radius-lg);
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none;
            cursor: pointer;
            margin: 1.5rem 0;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
        }}
        
        .button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.7s ease;
        }}
        
        .button:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-xl);
        }}
        
        .button:hover::before {{
            left: 100%;
        }}
        
        .button:active {{
            transform: translateY(-1px);
        }}
        
        .video-container {{
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            margin: 2.5rem 0;
            background: #000;
        }}
        
        .video-container iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
            border-radius: var(--radius-lg);
        }}
        
        /* 返回顶部按钮 */
        .back-to-top {{
            position: fixed;
            bottom: 3rem;
            right: 3rem;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: var(--shadow-xl);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1000;
            opacity: 0;
        }}
        
        .back-to-top.show {{
            display: flex;
            opacity: 1;
            animation: bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }}
        
        .back-to-top:hover {{
            transform: translateY(-5px) scale(1.1);
            box-shadow: var(--shadow-2xl);
        }}
        
        @keyframes bounceIn {{
            0% {{
                opacity: 0;
                transform: scale(0.3) translateY(30px);
            }}
            50% {{
                opacity: 0.9;
                transform: scale(1.1);
            }}
            80% {{
                opacity: 1;
                transform: scale(0.89);
            }}
            100% {{
                opacity: 1;
                transform: scale(1);
            }}
        }}
        
        /* 快速导航 */
        .quick-nav {{
            position: fixed;
            bottom: 3rem;
            right: 3rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            z-index: 998;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .quick-nav.visible {{
            opacity: 1;
        }}
        
        .nav-btn {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            color: var(--text-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-lg);
        }}
        
        .nav-btn:hover {{
            background: var(--primary-color);
            color: white;
            transform: translateY(-3px) scale(1.1);
            border-color: var(--primary-color);
            box-shadow: var(--shadow-xl);
        }}
        
        /* 搜索模态框 */
        .search-modal {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            z-index: 2000;
            display: none;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .search-modal.active {{
            display: flex;
            opacity: 1;
        }}
        
        .search-container {{
            width: 90%;
            max-width: 800px;
            background: var(--card-bg);
            border-radius: var(--radius-xl);
            padding: 2.5rem;
            box-shadow: var(--shadow-2xl);
            position: relative;
        }}
        
        .search-input {{
            width: 100%;
            padding: 1.5rem;
            font-size: 1.3rem;
            border: 3px solid var(--border-color);
            border-radius: var(--radius-lg);
            background: var(--bg-color);
            color: var(--text-color);
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 4px rgba(var(--primary-color-rgb), 0.1);
        }}
        
        .search-close {{
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            background: transparent;
            border: none;
            color: var(--text-color);
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .search-close:hover {{
            color: var(--primary-color);
            transform: rotate(90deg);
        }}
        
        .search-results {{
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .search-result-item {{
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .search-result-item:hover {{
            background: var(--bg-color);
            padding-left: 2rem;
        }}
        
        .search-result-title {{
            font-weight: 700;
            color: var(--text-color);
            margin-bottom: 0.5rem;
        }}
        
        .search-result-content {{
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.95rem;
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
            transition: opacity 0.5s ease;
        }}
        
        .loading-overlay.hidden {{
            opacity: 0;
            pointer-events: none;
        }}
        
        .loading-spinner-large {{
            width: 80px;
            height: 80px;
            border: 5px solid var(--border-color);
            border-top: 5px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 2rem;
        }}
        
        .loading-overlay p {{
            font-size: 1.2rem;
            color: var(--text-color);
            font-weight: 500;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* 响应式设计 */
        @media (max-width: 1200px) {{
            .content {{
                padding: 2.5rem 3rem;
            }}
            
            .sidebar.hidden ~ .content {{
                padding-left: 4rem;
            }}
        }}
        
        @media (max-width: 992px) {{
            .sidebar {{
                width: 280px;
                padding: 2rem;
            }}
            
            .content {{
                margin-left: 280px;
                padding: 2rem;
            }}
            
            .sidebar.hidden ~ .content {{
                padding-left: 2rem;
            }}
            
            .page-title {{
                font-size: 2.8rem;
            }}
            
            .heading-1 {{ font-size: 2.4rem; }}
            .heading-2 {{ font-size: 2rem; }}
            .heading-3 {{ font-size: 1.6rem; }}
            .heading-4 {{ font-size: 1.4rem; }}
        }}
        
        @media (max-width: 768px) {{
            .sidebar {{
                width: 100%;
                max-width: 320px;
                box-shadow: var(--shadow-2xl);
            }}
            
            .sidebar.hidden {{
                transform: translateX(-100%);
            }}
            
            .sidebar:not(.hidden) ~ .sidebar-toggle {{
                display: none;
            }}
            
            .content {{
                margin-left: 0;
                padding: 1.5rem;
            }}
            
            .sidebar.hidden ~ .content {{
                padding-left: 1.5rem;
            }}
            
            .page {{
                padding-bottom: 3rem;
            }}
            
            .page-title {{
                font-size: 2.4rem;
                padding-bottom: 1rem;
            }}
            
            .quick-nav {{
                bottom: 2rem;
                right: 2rem;
            }}
            
            .nav-btn {{
                width: 50px;
                height: 50px;
                font-size: 1.2rem;
            }}
            
            .back-to-top {{
                bottom: 2rem;
                right: 2rem;
                width: 50px;
                height: 50px;
                font-size: 1.2rem;
            }}
            
            .sidebar-toggle {{
                top: 1.5rem;
                left: 1.5rem;
                width: 50px;
                height: 50px;
                font-size: 1.3rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .content {{
                padding: 1rem;
            }}
            
            .sidebar.hidden ~ .content {{
                padding-left: 1rem;
            }}
            
            .page {{
                padding-bottom: 2rem;
            }}
            
            .page-title {{
                font-size: 2rem;
            }}
            
            .heading-1 {{ font-size: 1.8rem; }}
            .heading-2 {{ font-size: 1.6rem; }}
            .heading-3 {{ font-size: 1.4rem; }}
            .heading-4 {{ font-size: 1.2rem; }}
            
            .paragraph {{
                padding: 1rem;
                font-size: 1.05rem;
            }}
            
            .note {{
                padding: 1.5rem;
            }}
            
            .button {{
                padding: 0.8rem 1.5rem;
                font-size: 1rem;
            }}
            
            .quick-nav {{
                bottom: 1.5rem;
                right: 1.5rem;
                gap: 0.75rem;
            }}
            
            .nav-btn {{
                width: 45px;
                height: 45px;
                font-size: 1.1rem;
            }}
            
            .back-to-top {{
                bottom: 1.5rem;
                right: 1.5rem;
                width: 45px;
                height: 45px;
            }}
            
            .sidebar-toggle {{
                top: 1rem;
                left: 1rem;
                width: 45px;
                height: 45px;
            }}
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
            
            .page {{
                max-width: 100%;
                padding: 0;
                margin: 0;
            }}
            
            .page-title {{
                font-size: 2rem;
            }}
            
            .heading-1 {{ font-size: 1.8rem; }}
            .heading-2 {{ font-size: 1.6rem; }}
            .heading-3 {{ font-size: 1.4rem; }}
            .heading-4 {{ font-size: 1.2rem; }}
            
            .paragraph {{
                background: none;
                border: none;
                box-shadow: none;
                padding: 0.5rem 0;
            }}
            
            .note {{
                background: none;
                border: 1px solid #ccc;
                box-shadow: none;
            }}
        }}
        """
    
    @staticmethod
    def generate_additional_css():
        """生成额外的CSS"""
        return """<style>
        /* 自定义滚动条 */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-color);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border-radius: 10px;
            border: 3px solid var(--bg-color);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
        }
        
        /* 选择文本样式 */
        ::selection {
            background: rgba(var(--primary-color-rgb), 0.3);
            color: var(--text-color);
        }
        
        ::-moz-selection {
            background: rgba(var(--primary-color-rgb), 0.3);
            color: var(--text-color);
        }
        
        /* 焦点样式 */
        :focus {
            outline: 3px solid rgba(var(--primary-color-rgb), 0.5);
            outline-offset: 2px;
        }
        
        :focus:not(:focus-visible) {
            outline: none;
        }
        
        /* 平滑滚动锚点 */
        html {
            scroll-padding-top: 2rem;
        }
        
        /* 图片样式 */
        img {
            max-width: 100%;
            height: auto;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
        }
        
        img:hover {
            transform: scale(1.02);
            box-shadow: var(--shadow-lg);
        }
        
        /* 代码块样式 */
        pre, code {
            font-family: 'Courier New', Monaco, monospace;
            background: var(--code-bg);
            border-radius: var(--radius-md);
            padding: 1rem;
            overflow-x: auto;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        code {
            padding: 0.2rem 0.5rem;
            margin: 0 0.2rem;
        }
        
        pre code {
            padding: 0;
            background: none;
        }
        
        /* 表格样式 */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }
        
        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        th {
            background: var(--primary-color);
            color: white;
            font-weight: 700;
        }
        
        tr:hover {
            background: var(--bg-color);
        }
        
        /* 引用样式 */
        blockquote {
            border-left: 4px solid var(--primary-color);
            margin: 2rem 0;
            padding: 1.5rem 2rem;
            background: var(--card-bg);
            border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
            font-style: italic;
            box-shadow: var(--shadow-sm);
        }
        
        blockquote p {
            margin: 0;
            color: var(--text-color);
            opacity: 0.9;
        }
        
        /* 列表样式 */
        ul, ol {
            margin: 1.5rem 0;
            padding-left: 2rem;
        }
        
        li {
            margin: 0.75rem 0;
            line-height: 1.6;
        }
        
        li::marker {
            color: var(--primary-color);
        }
        
        /* 分割线 */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, var(--primary-color), transparent);
            margin: 3rem 0;
        }
        
        /* 工具提示 */
        [data-tooltip] {
            position: relative;
            cursor: help;
        }
        
        [data-tooltip]:hover::before {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--card-bg);
            color: var(--text-color);
            padding: 0.75rem 1rem;
            border-radius: var(--radius-sm);
            font-size: 0.9rem;
            white-space: nowrap;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            margin-bottom: 0.5rem;
            border: 1px solid var(--border-color);
        }
        
        [data-tooltip]:hover::after {
            content: '';
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            border-width: 5px;
            border-style: solid;
            border-color: var(--card-bg) transparent transparent transparent;
            margin-bottom: -5px;
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
                    <i class="fas fa-file-alt fa-3x" style="color: var(--text-color); opacity: 0.3; margin-bottom: 1rem;"></i>
                    <p style="color: var(--text-color); opacity: 0.5; font-style: italic;">暂无内容</p>
                </div>
            </div>
            '''
        
        content_html = ""
        for element in page["content"]:
            element_html = HTMLGenerator.generate_element_html(element)
            content_html += f'<div class="element">{element_html}</div>'
        
        return content_html
    
    @staticmethod
    def generate_element_html(element):
        """生成单个元素HTML"""
        element_type = element["type"]
        
        if element_type == "heading":
            level = element.get("level", 2)
            text = element.get("text", "")
            color = element.get("color", "var(--text-color)")
            align = element.get("align", "left")
            font_family = element.get('font_family', "Inter, 'Microsoft YaHei', sans-serif")
            font_size = element.get('font_size', '2rem')
            bold = element.get('bold', True)
            underline = element.get('underline', False)
            strike = element.get('strike', False)
            weight = '700' if bold else '400'
            text_decoration = 'line-through' if strike else ('underline' if underline else 'none')
            # Use format() to avoid f-string parsing issues when attributes contain braces
            return '<h{lvl} class="heading heading-{lvl}" style="color: {color}; text-align: {align}; font-family: {ff}; font-size: {fs}; font-weight: {wt}; text-decoration: {td};">{text}</h{lvl}>'.format(
                lvl=level,
                color=html.escape(color),
                align=html.escape(align),
                ff=font_family,
                fs=font_size,
                wt=weight,
                td=text_decoration,
                text=html.escape(text)
            )
        
        elif element_type == "paragraph":
            text = element.get("text", "")
            color = element.get("color", "var(--text-color)")
            background = element.get("background", "var(--card-bg)")
            align = element.get("align", "left")
            font_family = element.get('font_family', "Inter, 'Microsoft YaHei', sans-serif")
            font_size = element.get('font_size', '1rem')
            bold = element.get('bold', False)
            underline = element.get('underline', False)
            strike = element.get('strike', False)
            text_with_breaks = text.replace('\n', '<br>')
            style_dec = f"font-family: {font_family}; font-size: {font_size}; font-weight: {'700' if bold else '400'}; text-decoration: {'line-through' if strike else ('underline' if underline else 'none')};"
            return f'''
            <div class="paragraph" style="color: {color}; background: {background}; text-align: {align}; {style_dec}">
                {text_with_breaks}
            </div>
            '''
        
        elif element_type == "note":
            text = element.get("text", "")
            author = element.get("author", "")
            color = element.get("color", "var(--text-color)")
            background = element.get("background", "var(--card-bg)")
            font_family = element.get('font_family', "Inter, 'Microsoft YaHei', sans-serif")
            font_size = element.get('font_size', '1rem')
            underline = element.get('underline', False)
            author_html = f'<div class="note-author">{author}</div>' if author else ''
            return f'''
            <div class="note" style="background: {background};">
                <div class="note-content" style="color: {color}; font-family: {font_family}; font-size: {font_size}; text-decoration: {'underline' if underline else 'none'};">
                    "{text}"
                    {author_html}
                </div>
            </div>
            '''
        
        elif element_type == "button":
            text = element.get("text", "点击这里")
            url = element.get("url", "#")
            color = element.get("color", "#ffffff")
            background = element.get("background", "var(--primary-color)")
            
            return f'''
            <a href="{url}" target="_blank" class="button" style="background: {background}; color: {color};">
                {text}
            </a>
            '''
        
        elif element_type == "video":
            embed_code = element.get("embed_code", "")
            video_id = element.get("video_id", "")
            # 如果用户提供了 embed_code，直接使用（保持不改动）
            if embed_code:
                return embed_code

            # 如果只有 video_id，生成更健壮的 iframe，增加 allow、referrerpolicy、loading 等属性
            if video_id:
                player_src = f"https://player.bilibili.com/player.html?bvid={video_id}&page=1"
                fallback_url = f"https://www.bilibili.com/video/{video_id}"
                return f'''
                <div class="video-container" aria-label="B站视频">
                    <iframe src="{player_src}"
                            loading="lazy"
                            scrolling="no"
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                            allowfullscreen
                            referrerpolicy="no-referrer-when-downgrade"
                            title="B站视频播放器">
                    </iframe>
                    <noscript style="display:block; margin-top:8px; color:var(--text-color); opacity:0.8;">
                        如果视频无法播放，请<a href="{fallback_url}" target="_blank" rel="noopener noreferrer">在B站打开</a>。
                    </noscript>
                </div>
                '''
            else:
                return '<p style="color: var(--text-color); opacity: 0.5; font-style: italic;">[视频未设置]</p>'
        
        elif element_type == "image":
            src = element.get("src", "")
            alt = element.get("alt", "图片")
            caption = element.get("caption", "")
            
            caption_html = f'<p class="image-caption" style="text-align: center; color: var(--text-color); opacity: 0.7; font-size: 0.9rem; margin-top: 0.5rem;">{caption}</p>' if caption else ''
            # 如果用户只填写了文件名，则导出时引用 pictures/ 目录
            img_src = src
            if src and not (src.startswith('http://') or src.startswith('https://') or src.startswith('/') or src.startswith('pictures/')):
                img_src = f'pictures/{src}'

            return f'''
            <div class="image-container">
                <img src="{img_src}" alt="{alt}" style="max-width: 100%; height: auto;">
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
    
    @staticmethod
    def generate_javascript():
        """生成JavaScript代码 - 移除主题切换功能"""
        return """
        // 页面加载完成
        window.addEventListener('DOMContentLoaded', () => {
            // 隐藏加载遮罩
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                setTimeout(() => {
                    loadingOverlay.classList.add('hidden');
                    setTimeout(() => loadingOverlay.style.display = 'none', 500);
                }, 500);
            }
            
            // 初始化RGB颜色值
            const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
            const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue('--secondary-color').trim();
            
            // 转换颜色为RGB
            function hexToRgb(hex) {
                const result = /^#?([a-f\\d]{2})([a-f\\d]{2})([a-f\\d]{2})$/i.exec(hex);
                return result ? {
                    r: parseInt(result[1], 16),
                    g: parseInt(result[2], 16),
                    b: parseInt(result[3], 16)
                } : null;
            }
            
            const primaryRgb = hexToRgb(primaryColor);
            const secondaryRgb = hexToRgb(secondaryColor);
            
            if (primaryRgb) {
                document.documentElement.style.setProperty('--primary-color-rgb', `${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}`);
            }
            
            if (secondaryRgb) {
                document.documentElement.style.setProperty('--secondary-color-rgb', `${secondaryRgb.r}, ${secondaryRgb.g}, ${secondaryRgb.b}`);
            }
        });
        
        // 侧边栏功能
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('sidebarToggle');
        const closeBtn = document.getElementById('closeSidebar');
        const content = document.querySelector('.content');
        
        // 初始化侧边栏状态
        function initSidebar() {
            const isMobile = window.innerWidth <= 768;
            const wasCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            
            if (isMobile || wasCollapsed) {
                sidebar.classList.add('hidden');
                if (toggleBtn) toggleBtn.style.display = 'flex';
            } else {
                sidebar.classList.remove('hidden');
                if (toggleBtn) toggleBtn.style.display = 'none';
            }
            
            // 更新快速导航可见性
            updateQuickNavVisibility();
        }
        
        // 页面加载时初始化
        window.addEventListener('load', initSidebar);
        window.addEventListener('resize', initSidebar);
        
        // 切换侧边栏
        if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                sidebar.classList.toggle('hidden');
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('hidden'));
                
                // 更新按钮图标
                if (sidebar.classList.contains('hidden')) {
                    toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
                    toggleBtn.setAttribute('aria-label', '展开侧边栏');
                } else {
                    toggleBtn.innerHTML = '<i class="fas fa-times"></i>';
                    toggleBtn.setAttribute('aria-label', '折叠侧边栏');
                }
                
                updateQuickNavVisibility();
            });
        }
        
        // 关闭侧边栏
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                sidebar.classList.add('hidden');
                localStorage.setItem('sidebarCollapsed', 'true');
                if (toggleBtn) {
                    toggleBtn.style.display = 'flex';
                    toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
                    toggleBtn.setAttribute('aria-label', '展开侧边栏');
                }
                updateQuickNavVisibility();
            });
        }
        
        // 点击外部关闭侧边栏（移动端）
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                const isClickInsideSidebar = sidebar.contains(e.target);
                const isClickOnToggle = toggleBtn && toggleBtn.contains(e.target);
                
                if (!isClickInsideSidebar && !isClickOnToggle && !sidebar.classList.contains('hidden')) {
                    sidebar.classList.add('hidden');
                    localStorage.setItem('sidebarCollapsed', 'true');
                    if (toggleBtn) {
                        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
                        toggleBtn.setAttribute('aria-label', '展开侧边栏');
                    }
                    updateQuickNavVisibility();
                }
            }
        });
        
        // 阻止侧边栏点击事件冒泡
        sidebar.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // 页面切换
        document.querySelectorAll('.tree-item').forEach(item => {
            item.addEventListener('click', function() {
                const pageId = this.dataset.page;
                
                // 更新活动状态
                document.querySelectorAll('.tree-item').forEach(i => {
                    i.classList.remove('active');
                    i.setAttribute('aria-selected', 'false');
                });
                this.classList.add('active');
                this.setAttribute('aria-selected', 'true');
                
                // 切换页面
                document.querySelectorAll('.page').forEach(page => {
                    page.classList.remove('active');
                });
                
                const targetPage = document.getElementById(pageId + '-page');
                if (targetPage) {
                    targetPage.classList.add('active');
                    
                    // 更新URL哈希（用于分享链接）
                    window.history.replaceState(null, null, `#${pageId}`);
                    
                    // 更新页面标题
                    const pageTitle = targetPage.querySelector('.page-title')?.textContent || document.title.split(' - ')[0];
                    document.title = `${pageTitle} - ${document.title.split(' - ')[0]}`;
                }
                
                // 滚动到顶部
                window.scrollTo({ top: 0, behavior: 'smooth' });
                
                // 移动端：选择页面后自动折叠侧边栏
                if (window.innerWidth <= 768) {
                    sidebar.classList.add('hidden');
                    localStorage.setItem('sidebarCollapsed', 'true');
                    if (toggleBtn) {
                        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
                        toggleBtn.setAttribute('aria-label', '展开侧边栏');
                    }
                    updateQuickNavVisibility();
                }
            });
        });
        
        // 检查URL哈希并跳转到对应页面
        function checkUrlHash() {
            const hash = window.location.hash.substring(1);
            if (hash) {
                const targetItem = document.querySelector(`.tree-item[data-page="${hash}"]`);
                if (targetItem) {
                    setTimeout(() => targetItem.click(), 100);
                }
            }
        }
        
        window.addEventListener('load', checkUrlHash);
        window.addEventListener('hashchange', checkUrlHash);
        
        // 返回顶部功能
        const backToTop = document.getElementById('backToTop');
        
        function updateBackToTop() {
            if (window.pageYOffset > 300) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        }
        
        window.addEventListener('scroll', updateBackToTop);
        updateBackToTop();
        
        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        // 快速导航
        const quickNav = document.getElementById('quickNav');
        
        function updateQuickNavVisibility() {
            if (!quickNav) return;
            
            if (sidebar.classList.contains('hidden')) {
                quickNav.classList.add('visible');
            } else {
                quickNav.classList.remove('visible');
            }
        }
        
        // 快速导航按钮功能
        if (quickNav) {
            const navButtons = quickNav.querySelectorAll('.nav-btn');
            
            navButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    const action = this.dataset.action;
                    
                    switch(action) {
                        case 'prev':
                            navigateToPreviousPage();
                            break;
                        case 'next':
                            navigateToNextPage();
                            break;
                        case 'toc':
                            toggleSidebar();
                            break;
                        case 'search':
                            openSearch();
                            break;
                    }
                });
            });
        }
        
        function navigateToPreviousPage() {
            const currentItem = document.querySelector('.tree-item.active');
            const prevItem = currentItem?.previousElementSibling;
            
            if (prevItem && prevItem.classList.contains('tree-item')) {
                prevItem.click();
            }
        }
        
        function navigateToNextPage() {
            const currentItem = document.querySelector('.tree-item.active');
            const nextItem = currentItem?.nextElementSibling;
            
            if (nextItem && nextItem.classList.contains('tree-item')) {
                nextItem.click();
            }
        }
        
        function toggleSidebar() {
            if (toggleBtn) {
                toggleBtn.click();
            }
        }
        
        // 搜索功能
        const searchModal = document.getElementById('searchModal');
        const searchInput = document.getElementById('searchInput');
        const searchClose = document.getElementById('searchClose');
        const searchResults = document.getElementById('searchResults');
        
        function openSearch() {
            if (searchModal) {
                searchModal.classList.add('active');
                setTimeout(() => {
                    if (searchInput) searchInput.focus();
                }, 100);
            }
        }
        
        function closeSearch() {
            if (searchModal) {
                searchModal.classList.remove('active');
                if (searchInput) searchInput.value = '';
                if (searchResults) searchResults.innerHTML = '';
            }
        }
        
        if (searchClose) {
            searchClose.addEventListener('click', closeSearch);
        }
        
        if (searchModal) {
            searchModal.addEventListener('click', (e) => {
                if (e.target === searchModal) {
                    closeSearch();
                }
            });
        }
        
        // 搜索功能
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const query = this.value.trim().toLowerCase();
                
                if (!query) {
                    if (searchResults) searchResults.innerHTML = '';
                    return;
                }
                
                // 搜索所有页面内容
                const results = [];
                const pages = document.querySelectorAll('.page');
                
                pages.forEach(page => {
                    const pageId = page.id.replace('-page', '');
                    const pageTitle = page.querySelector('.page-title')?.textContent || '未命名页面';
                    const elements = page.querySelectorAll('.element');
                    
                    elements.forEach((element, index) => {
                        const text = element.textContent.toLowerCase();
                        if (text.includes(query)) {
                            const preview = element.textContent.substring(0, 150) + (element.textContent.length > 150 ? '...' : '');
                            const title = element.querySelector('h1, h2, h3, h4, h5, h6')?.textContent || `内容块 #${index + 1}`;
                            
                            results.push({
                                pageId,
                                pageTitle,
                                title,
                                preview,
                                element: element
                            });
                        }
                    });
                });
                
                // 显示搜索结果
                if (searchResults) {
                    if (results.length > 0) {
                        searchResults.innerHTML = results.map(result => `
                            <div class="search-result-item" data-page="${result.pageId}">
                                <div class="search-result-title">${result.title} - ${result.pageTitle}</div>
                                <div class="search-result-content">${result.preview}</div>
                            </div>
                        `).join('');
                        
                        // 添加点击事件
                        searchResults.querySelectorAll('.search-result-item').forEach(item => {
                            item.addEventListener('click', function() {
                                const pageId = this.dataset.page;
                                const targetItem = document.querySelector(`.tree-item[data-page="${pageId}"]`);
                                if (targetItem) {
                                    targetItem.click();
                                    closeSearch();
                                    
                                    // 滚动到对应元素
                                    setTimeout(() => {
                                        const elementIndex = Array.from(searchResults.querySelectorAll('.search-result-item')).indexOf(this);
                                        if (results[elementIndex]?.element) {
                                            results[elementIndex].element.scrollIntoView({
                                                behavior: 'smooth',
                                                block: 'center'
                                            });
                                        }
                                    }, 300);
                                }
                            });
                        });
                    } else {
                        searchResults.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-color); opacity: 0.5;">未找到匹配的内容</div>';
                    }
                }
            });
            
            // 支持回车键搜索
            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const firstResult = searchResults?.querySelector('.search-result-item');
                    if (firstResult) {
                        firstResult.click();
                    }
                } else if (e.key === 'Escape') {
                    closeSearch();
                }
            });
        }
        
        // 动画效果
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.05, rootMargin: '0px 0px -50px 0px' });
        
        document.querySelectorAll('.element').forEach(el => {
            observer.observe(el);
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + B 切换侧边栏
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                if (toggleBtn) toggleBtn.click();
            }
            
            // Ctrl/Cmd + K 或 / 键打开搜索
            if ((e.ctrlKey || e.metaKey) && e.key === 'k' || e.key === '/') {
                e.preventDefault();
                openSearch();
            }
            
            // ESC 键关闭搜索或侧边栏
            if (e.key === 'Escape') {
                if (searchModal?.classList.contains('active')) {
                    closeSearch();
                } else if (window.innerWidth <= 768 && !sidebar.classList.contains('hidden')) {
                    sidebar.classList.add('hidden');
                    localStorage.setItem('sidebarCollapsed', 'true');
                    if (toggleBtn) {
                        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
                        toggleBtn.setAttribute('aria-label', '展开侧边栏');
                    }
                    updateQuickNavVisibility();
                }
            }
            
            // 方向键导航
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                navigateToPreviousPage();
            }
            
            if (e.key === 'ArrowRight') {
                e.preventDefault();
                navigateToNextPage();
            }
            
            // T 键切换目录
            if (e.key === 't' || e.key === 'T') {
                e.preventDefault();
                toggleSidebar();
            }
            
            // 空格键或PgDn翻页
            if (e.key === ' ' || e.key === 'PageDown') {
                e.preventDefault();
                navigateToNextPage();
            }
            
            // PgUp翻页
            if (e.key === 'PageUp') {
                e.preventDefault();
                navigateToPreviousPage();
            }
        });
        
        // 阻止空格键滚动页面
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ' && e.target === document.body) {
                e.preventDefault();
            }
        }, false);
        
        // 初始化：显示第一个页面
        setTimeout(() => {
            const coverItem = document.querySelector('.cover-item');
            if (coverItem) {
                coverItem.click();
            }
        }, 100);
        
        // 打印按钮（可选功能）
        function addPrintButton() {
            const printBtn = document.createElement('button');
            printBtn.className = 'nav-btn';
            printBtn.setAttribute('data-action', 'print');
            printBtn.setAttribute('aria-label', '打印页面');
            printBtn.setAttribute('title', '打印页面 (Ctrl+P)');
            printBtn.innerHTML = '<i class="fas fa-print"></i>';
            
            printBtn.addEventListener('click', () => {
                window.print();
            });
            
            if (quickNav) {
                quickNav.appendChild(printBtn);
            }
        }
        
        // 可选：添加打印按钮
        // addPrintButton();
        """
    
    @staticmethod
    def generate_additional_js():
        """生成额外的JavaScript"""
        return """<script>
        // 平滑滚动到锚点
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // 图片懒加载
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // 代码高亮（可选）
        function highlightCode() {
            if (typeof hljs !== 'undefined') {
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightBlock(block);
                });
            }
        }
        
        // 可选：加载代码高亮库
        // const highlightScript = document.createElement('script');
        // highlightScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.0/highlight.min.js';
        // highlightScript.onload = highlightCode;
        // document.head.appendChild(highlightScript);
        
        // 添加复制代码按钮
        function addCopyButtons() {
            document.querySelectorAll('pre').forEach(pre => {
                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-code-btn';
                copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                copyBtn.setAttribute('aria-label', '复制代码');
                copyBtn.setAttribute('title', '复制代码');
                
                copyBtn.addEventListener('click', async () => {
                    const code = pre.querySelector('code').textContent;
                    try {
                        await navigator.clipboard.writeText(code);
                        copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                        copyBtn.style.background = 'var(--success-color)';
                        setTimeout(() => {
                            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                            copyBtn.style.background = '';
                        }, 2000);
                    } catch (err) {
                        console.error('复制失败:', err);
                    }
                });
                
                pre.style.position = 'relative';
                pre.appendChild(copyBtn);
            });
        }
        
        // 可选：添加复制按钮
        // addCopyButtons();
        
        // 添加回到顶部快捷键提示
        window.addEventListener('scroll', () => {
            const backToTop = document.getElementById('backToTop');
            if (backToTop && window.pageYOffset > 1000) {
                backToTop.setAttribute('title', '返回顶部 (↑ 或 Home)');
            }
        });
        
        // Home键返回顶部
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Home') {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
        
        // 添加页面切换动画
        let isPageTransitioning = false;
        
        function switchPageWithAnimation(newPageId) {
            if (isPageTransitioning) return;
            isPageTransitioning = true;
            
            const currentPage = document.querySelector('.page.active');
            const newPage = document.getElementById(newPageId + '-page');
            
            if (!currentPage || !newPage) {
                isPageTransitioning = false;
                return;
            }
            
            // 淡出当前页面
            currentPage.style.opacity = '0';
            currentPage.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                currentPage.classList.remove('active');
                newPage.classList.add('active');
                
                // 淡入新页面
                newPage.style.opacity = '0';
                newPage.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    newPage.style.opacity = '1';
                    newPage.style.transform = 'translateY(0)';
                    isPageTransitioning = false;
                    
                    // 更新URL和标题
                    window.history.replaceState(null, null, `#${newPageId}`);
                    const pageTitle = newPage.querySelector('.page-title')?.textContent || document.title.split(' - ')[0];
                    document.title = `${pageTitle} - ${document.title.split(' - ')[0]}`;
                }, 50);
            }, 300);
        }
        
        // 添加页面加载完成事件
        window.addEventListener('load', () => {
            // 添加加载完成类
            document.body.classList.add('page-loaded');
        });
        
        // 错误处理
        window.addEventListener('error', (e) => {
            console.error('页面错误:', e.error);
        });
        </script>"""

# ============================================
# 内容元素类
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
        
        # 根据元素类型设置默认值
        if element_type == "heading":
            element.update({
                "text": kwargs.get("text", "新标题"),
                "level": kwargs.get("level", 2),
                "color": kwargs.get("color", "#007acc"),
                "align": kwargs.get("align", "left"),
                "animation": kwargs.get("animation", "none"),
                "font_family": kwargs.get("font_family", "Inter, 'Microsoft YaHei', sans-serif"),
                "font_size": kwargs.get("font_size", "2rem"),
                "bold": kwargs.get("bold", True),
                "underline": kwargs.get("underline", False),
                "strike": kwargs.get("strike", False)
            })
        elif element_type == "paragraph":
            element.update({
                "text": kwargs.get("text", "请输入段落内容..."),
                "color": kwargs.get("color", "#007acc"),
                "background": kwargs.get("background", "#ffffff"),
                "align": kwargs.get("align", "left"),
                "font_size": kwargs.get("font_size", "1rem"),
                "line_height": kwargs.get("line_height", "1.7"),
                "font_family": kwargs.get("font_family", "Inter, 'Microsoft YaHei', sans-serif"),
                "bold": kwargs.get("bold", False),
                "underline": kwargs.get("underline", False),
                "strike": kwargs.get("strike", False)
            })
        elif element_type == "note":
            element.update({
                "text": kwargs.get("text", "这里是注释内容..."),
                "author": kwargs.get("author", ""),
                "color": kwargs.get("color", "#007acc"),
                "background": kwargs.get("background", "#f8f9fa"),
                "show_quotes": kwargs.get("show_quotes", True),
                "font_family": kwargs.get("font_family", "Inter, 'Microsoft YaHei', sans-serif"),
                "font_size": kwargs.get("font_size", "1rem"),
                "bold": kwargs.get("bold", False),
                "underline": kwargs.get("underline", False)
            })
        elif element_type == "button":
            element.update({
                "text": kwargs.get("text", "点击这里"),
                "url": kwargs.get("url", "#"),
                "color": kwargs.get("color", "#ffffff"),
                "background": kwargs.get("background", "#667eea"),
                "hover_background": kwargs.get("hover_background", "#764ba2"),
                "size": kwargs.get("size", "medium"),
                "rounded": kwargs.get("rounded", True)
            })
        elif element_type == "video":
            element.update({
                "video_id": kwargs.get("video_id", ""),
                "embed_code": kwargs.get("embed_code", ""),
                "title": kwargs.get("title", "B站视频"),
                "width": kwargs.get("width", "100%"),
                "height": kwargs.get("height", "500px"),
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
                "theme": kwargs.get("theme", "default"),
                "show_line_numbers": kwargs.get("show_line_numbers", True)
            })
        elif element_type == "divider":
            element.update({
                "style": kwargs.get("style", "solid"),
                "color": kwargs.get("color", "#e2e8f0"),
                "width": kwargs.get("width", "100%"),
                "thickness": kwargs.get("thickness", "2px")
            })
        
        return element
    
    @staticmethod
    def get_element_icon(element_type):
        """获取元素类型图标"""
        return ContentElement.element_types.get(element_type, {}).get("icon", "📄")
    
    @staticmethod
    def get_element_name(element_type):
        """获取元素类型名称"""
        return ContentElement.element_types.get(element_type, {}).get("name", "未知元素")

# ============================================
# 目录树组件
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
            if st.button(f"🏠 {cover.get('title', '封面')}", 
                        key=f"tree_{cover['id']}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
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
    
    # 增加移动按钮：上移/下移，以及编辑/删除
    col1, col2, col3, col4 = st.sidebar.columns([3, 1, 1, 1])
    
    with col1:
        if st.button(
            f"{icon} {page.get('title', '未命名')}",
            key=f"tree_{page['id']}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
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
        if st.button("⬆️", key=f"move_up_{page['id']}", help="上移页面"):
            structure = st.session_state.project_structure
            if "pages" in structure:
                idx = next((i for i, p in enumerate(structure["pages"]) if p["id"] == page["id"]), -1)
                if idx > 0:
                    structure["pages"][idx], structure["pages"][idx-1] = structure["pages"][idx-1], structure["pages"][idx]
                    save_project()
                    st.session_state.current_page = structure["pages"][idx+1]
                    save_project()
                    st.session_state.current_page = structure["pages"][idx+1]
                    safe_rerun()
            structure = st.session_state.project_structure
            if "pages" in structure:
                idx = next((i for i, p in enumerate(structure["pages"]) if p["id"] == page["id"]), -1)
                if idx >= 0 and idx < len(structure["pages"]) - 1:
                    structure["pages"][idx], structure["pages"][idx+1] = structure["pages"][idx+1], structure["pages"][idx]
                    save_project()
                    st.session_state.current_page = structure["pages"][idx+1]
                    safe_rerun()

    with col4:
        if st.button("🗑️", 
                    key=f"del_{page['id']}",
                    help="删除此页面",
                    use_container_width=True,
                    type="secondary"):
            delete_page(page["id"])
    
    # 递归渲染子页面（如果支持嵌套）
    if "children" in page and page["children"]:
        for child in page["children"]:
            render_page_tree_item(child, depth + 1)

# ============================================
# 页面操作函数
# ============================================
def select_page(page):
    """选择页面"""
    st.session_state.current_page = page
    st.session_state.edit_mode = False
    st.session_state.edit_element_id = None
    st.session_state.edit_page_title = False
    safe_rerun()

def add_new_page(page_type):
    """添加新页面"""
    structure = st.session_state.project_structure
    
    new_page = {
        "id": f"page_{str(uuid.uuid4())[:8]}",
        "title": f"新{('页面' if page_type == 'page' else '章节')}",
        "type": page_type,
        "content": [],
        "created_at": datetime.now().isoformat(),
        "order": len(structure.get("pages", [])) + 1
    }
    
    if "pages" not in structure:
        structure["pages"] = []
    
    structure["pages"].append(new_page)
    
    if save_project():
        select_page(new_page)
        SessionStateManager.add_notification(f"已创建新{('页面' if page_type == 'page' else '章节')}", "success")
    else:
        SessionStateManager.add_notification("创建失败", "error")

def delete_page(page_id):
    """删除页面"""
    structure = st.session_state.project_structure
    
    if page_id == "cover":
        SessionStateManager.add_notification("不能删除封面页", "warning")
        return
    
    if "pages" in structure:
        # 递归删除页面（处理嵌套）
        def remove_page_by_id(pages_list, pid):
            for i, p in enumerate(pages_list):
                if p.get("id") == pid:
                    return pages_list.pop(i)
                if "children" in p and p["children"]:
                    removed = remove_page_by_id(p["children"], pid)
                    if removed:
                        return removed
            return None

        pending_key = f"pending_delete_page_{page_id}"
        title = None
        # 尝试在扁平 pages 中查找标题，若有嵌套则在所有页面中查找
        def find_title(pages_list, pid):
            for p in pages_list:
                if p.get('id') == pid:
                    return p.get('title')
                if 'children' in p and p['children']:
                    t = find_title(p['children'], pid)
                    if t:
                        return t
            return None

        title = find_title(structure.get('pages', []), page_id) or page_id

        if st.session_state.get(pending_key):
            # 严格删除确认：要求输入完整页面标题
            st.warning(f"⚠️ 将永久删除页面: '{title}'. 此操作不可撤销。\n请输入完整页面标题以确认删除。")
            user_input = st.text_input("输入页面标题以确认删除", value="", key=f"confirm_input_{page_id}")
            colc, coly = st.columns([1,1])
            with colc:
                if st.button("取消", key=f"cancel_delete_page_{page_id}"):
                    st.session_state[pending_key] = False
                    safe_rerun()
            with coly:
                confirm_enabled = (user_input.strip() == (title or '').strip() and user_input.strip() != "")
                if st.button("🗑️ 确认删除", key=f"confirm_delete_page_{page_id}", disabled=not confirm_enabled):
                    if not confirm_enabled:
                        SessionStateManager.add_notification("输入不匹配，删除已取消", "warning")
                        st.session_state[pending_key] = False
                        safe_rerun()
                    else:
                        deleted_page = remove_page_by_id(structure.get('pages', []), page_id)
                        if deleted_page:
                            if st.session_state.current_page and st.session_state.current_page.get("id") == page_id:
                                st.session_state.current_page = structure["cover_page"]
                            if save_project():
                                st.session_state[pending_key] = False
                                SessionStateManager.add_notification("页面已删除", "success")
                                safe_rerun()
                            else:
                                SessionStateManager.add_notification("删除失败", "error")
                        else:
                            SessionStateManager.add_notification("未找到要删除的页面", "warning")
                            st.session_state[pending_key] = False
                            safe_rerun()
        else:
            if st.button("🗑️ 确认删除此页面", key=f"del_btn_page_{page_id}"):
                st.session_state[pending_key] = True
                safe_rerun()

def edit_page_title(page_id):
    """编辑页面标题"""
    st.session_state.edit_page_title = True
    st.session_state.edit_page_id = page_id
    safe_rerun()

def add_content_element(element_type):
    """添加内容元素"""
    if not st.session_state.current_page:
        SessionStateManager.add_notification("请先选择一个页面", "warning")
        return
    
    if "content" not in st.session_state.current_page:
        st.session_state.current_page["content"] = []
    
    new_element = ContentElement.create_element(element_type)
    st.session_state.current_page["content"].append(new_element)
    
    if save_project():
        st.session_state.edit_mode = True
        st.session_state.edit_element_id = new_element["id"]
        SessionStateManager.add_notification(f"已添加{ContentElement.get_element_name(element_type)}", "success")
        safe_rerun()
    else:
        SessionStateManager.add_notification("添加失败", "error")

# ============================================
# 页面编辑器
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
                    safe_rerun()
            
            with col_cancel:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state.edit_page_title = False
                    safe_rerun()
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
                safe_rerun()
    
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
                safe_rerun()
    
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
        st.markdown(f'<div id="elem-{element_id}" class="content-element">', unsafe_allow_html=True)
        
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
                            safe_rerun()
            
            with col_ops2:
                if st.button("✏️", key=f"edit_{element_id}", help="编辑"):
                        st.session_state.edit_mode = True
                        st.session_state.edit_element_id = element_id
                        st.session_state['_scroll_to_element'] = element_id
                        safe_rerun()
            
            with col_ops3:
                if st.button("⬇️", key=f"down_{element_id}", help="下移"):
                    if index < len(page["content"]) - 1:
                        page["content"][index], page["content"][index+1] = page["content"][index+1], page["content"][index]
                        if save_project():
                            safe_rerun()
            
            with col_ops4:
                if st.button("🗑️", key=f"del_{element_id}", help="删除"):
                    # 标记为待删除（在下一次渲染显示确认按钮）
                    st.session_state[f"pending_delete_{element_id}"] = True
                    safe_rerun()

            # 如果处于待删除状态，显示确认/取消按钮
            if st.session_state.get(f"pending_delete_{element_id}"):
                st.warning(f"⚠️ 确认删除这个 {name} ?")
                ccol, ycol = st.columns([1,1])
                with ccol:
                    if st.button("取消", key=f"cancel_del_{element_id}"):
                        st.session_state[f"pending_delete_{element_id}"] = False
                        safe_rerun()
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
                            safe_rerun()
                        else:
                            st.session_state[f"pending_delete_{element_id}"] = False
                            SessionStateManager.add_notification("删除失败", "error")
        
        # 元素预览
        st.markdown("---")
        
        if element_type == "heading":
            level = element.get("level", 2)
            text = element.get("text", "")
            color = element.get("color", "#2d3748")
            st.markdown(f"<h{level} style='color: {color}; margin: 10px 0;'>{text}</h{level}>", 
                      unsafe_allow_html=True)
        
        elif element_type == "paragraph":
            text = element.get("text", "")
            color = element.get("color", "#4a5568")
            background = element.get("background", "#ffffff")
            st.markdown(f"""
            <div style="color: {color}; background: {background}; padding: 15px; border-radius: 10px; margin: 10px 0;">
                {text[:200]}{'...' if len(text) > 200 else ''}
            </div>
            """, unsafe_allow_html=True)
        
        elif element_type == "note":
            text = element.get("text", "")
            author = element.get("author", "")
            st.markdown(f"""
            <div style="color: #666; background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; font-style: italic; border-left: 4px solid #667eea;">
                "{text[:150]}{'...' if len(text) > 150 else ''}"
                {f'<br><small style="color: #888;">— {author}</small>' if author else ''}
            </div>
            """, unsafe_allow_html=True)
        
        elif element_type == "button":
            text = element.get("text", "点击这里")
            st.markdown(f"""
            <div style="display: inline-block; background: #667eea; color: white; padding: 10px 20px; border-radius: 8px; margin: 10px 0; font-weight: bold; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
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
            
            col_left, col_right = st.columns(2)
            with col_left:
                element["color"] = st.color_picker("文字颜色", value=element.get("color", "#2d3748"))
                element["font_family"] = st.selectbox("字体", ["Inter, 'Microsoft YaHei', sans-serif", "Arial, sans-serif", "'Noto Sans SC', 'Microsoft YaHei', sans-serif"], index=0 if element.get("font_family","Inter, 'Microsoft YaHei', sans-serif") == "Inter, 'Microsoft YaHei', sans-serif" else 1)
                element["font_size"] = st.selectbox("字号", ["2.8rem","2.4rem","2rem","1.6rem"], index=0 if element.get("font_size","2rem")=="2.8rem" else (1 if element.get("font_size","2rem")=="2.4rem" else (2 if element.get("font_size","2rem")=="2rem" else 3)))
            with col_right:
                element["align"] = st.selectbox("对齐方式", ["left", "center", "right"],
                                              index=["left", "center", "right"].index(
                                                  element.get("align", "left")))
                # 样式开关
                element["bold"] = st.checkbox("加粗", value=element.get("bold", True))
                element["underline"] = st.checkbox("下划线", value=element.get("underline", False))
                element["strike"] = st.checkbox("删除线", value=element.get("strike", False))
        
        elif element_type == "paragraph":
            # 自适应高度：根据换行数估算高度
            def estimate_height(text):
                lines = text.count('\n') + 1
                est = min(max(120, lines * 28), 1200)
                return est

            element["text"] = st.text_area("内容", value=element.get("text", ""), height=estimate_height(element.get("text", "")))
            col_left, col_right = st.columns(2)
            with col_left:
                element["color"] = st.color_picker("文字颜色", value=element.get("color", "#4a5568"))
                element["font_family"] = st.selectbox("字体", ["Inter, 'Microsoft YaHei', sans-serif", "Arial, sans-serif", "'Noto Sans SC', 'Microsoft YaHei', sans-serif"], index=0 if element.get("font_family","Inter, 'Microsoft YaHei', sans-serif") == "Inter, 'Microsoft YaHei', sans-serif" else 1)
                element["font_size"] = st.selectbox("字号", ["1.25rem","1rem","0.9rem","0.8rem"], index=0 if element.get("font_size","1rem")=="1.25rem" else (1 if element.get("font_size","1rem")=="1rem" else (2 if element.get("font_size","1rem")=="0.9rem" else 3)))
            with col_right:
                element["background"] = st.color_picker("背景颜色", value=element.get("background", "#ffffff"))
                element["align"] = st.selectbox("对齐方式", ["left", "center", "right", "justify"],
                                          index=["left", "center", "right", "justify"].index(
                                              element.get("align", "left")))
                # 样式
                style_col1, style_col2 = st.columns(2)
                with style_col1:
                    element["bold"] = st.checkbox("加粗", value=element.get("bold", False))
                    element["underline"] = st.checkbox("下划线", value=element.get("underline", False))
                with style_col2:
                    element["strike"] = st.checkbox("删除线", value=element.get("strike", False))
        
        elif element_type == "note":
            element["text"] = st.text_area("注释内容", value=element.get("text", ""), height=120)
            element["author"] = st.text_input("吐槽者", value=element.get("author", ""))
            col_left, col_right = st.columns(2)
            with col_left:
                element["color"] = st.color_picker("文字颜色", value=element.get("color", "#666666"))
                element["font_family"] = st.selectbox("字体", ["Inter, 'Microsoft YaHei', sans-serif", "Arial, sans-serif", "'Noto Sans SC', 'Microsoft YaHei', sans-serif"], index=0)
            with col_right:
                element["background"] = st.color_picker("背景颜色", value=element.get("background", "#f8f9fa"))
                element["font_size"] = st.selectbox("字号", ["1.1rem","1rem","0.9rem"], index=0 if element.get("font_size","1rem")=="1.1rem" else (1 if element.get("font_size","1rem")=="1rem" else 2))
                element["underline"] = st.checkbox("下划线", value=element.get("underline", False))
        
        elif element_type == "image":
            element["src"] = st.text_input("图片文件名（仅文件名或相对/绝对URL）", value=element.get("src", ""), help="示例: mypic.jpg 或 https://.../img.png")
            element["alt"] = st.text_input("替代文本 (alt)", value=element.get("alt", "图片"))
            element["caption"] = st.text_input("图片说明 (caption)", value=element.get("caption", ""))
            col_w, col_a = st.columns(2)
            with col_w:
                element["width"] = st.text_input("宽度", value=element.get("width", "100%"))
            with col_a:
                element["align"] = st.selectbox("对齐方式", ["center", "left", "right"], index=["center", "left", "right"].index(element.get("align", "center")))

        elif element_type == "code":
            element["code"] = st.text_area("代码内容", value=element.get("code", ""), height=200)
            element["language"] = st.text_input("语言 (例如 python, javascript)", value=element.get("language", "python"))
            element["show_line_numbers"] = st.checkbox("显示行号", value=element.get("show_line_numbers", True))
            element["theme"] = st.selectbox("主题", ["default", "dark", "light"], index=["default", "dark", "light"].index(element.get("theme", "default")))
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
                element["background"] = st.color_picker("背景颜色", value=element.get("background", "#667eea"))
        
        elif element_type == "video":
            element["video_id"] = st.text_input("B站视频ID (BV号)", value=element.get("video_id", ""),
                                              help="例如：BV1xx411c7mD")
            element["embed_code"] = st.text_area("B站嵌入代码 (可选)", value=element.get("embed_code", ""), help="如果填入完整的 iframe 嵌入代码，将直接使用该代码进行嵌入")
            element["title"] = st.text_input("视频标题", value=element.get("title", "B站视频"))
            
            col_width, col_height = st.columns(2)
            with col_width:
                element["width"] = st.text_input("宽度", value=element.get("width", "100%"))
            with col_height:
                element["height"] = st.text_input("高度", value=element.get("height", "500px"))
        
        # 保存/取消按钮
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("💾 保存修改", use_container_width=True, key=f"save_{element['id']}"):
                st.session_state.edit_mode = False
                st.session_state.edit_element_id = None
                if save_project():
                    SessionStateManager.add_notification("修改已保存", "success")
                safe_rerun()
        
        with col_cancel:
            if st.button("❌ 取消", use_container_width=True, key=f"cancel_{element['id']}"):
                st.session_state.edit_mode = False
                st.session_state.edit_element_id = None
                safe_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_preview(page):
    """渲染页面预览"""
    if "content" not in page or not page["content"]:
        st.info("暂无内容")
        return
    
    # 创建预览容器
    for element in page["content"]:
        if element["type"] == "heading":
            level = element.get("level", 2)
            text = element.get("text", "")
            color = element.get("color", "#2d3748")
            font_family = element.get("font_family", "Inter, 'Microsoft YaHei', sans-serif")
            font_size = element.get("font_size", "2rem")
            bold = element.get("bold", True)
            underline = element.get("underline", False)
            strike = element.get("strike", False)
            weight = '700' if bold else '400'
            text_decoration = 'line-through' if strike else ('underline' if underline else 'none')
            st.markdown(f"<h{level} style='color: {color}; margin: 15px 0; font-family: {font_family}; font-size: {font_size}; font-weight: {weight}; text-decoration: {text_decoration};'>{text}</h{level}>", 
                      unsafe_allow_html=True)
        
        elif element["type"] == "paragraph":
            text = element.get("text", "")
            color = element.get("color", "#4a5568")
            background = element.get("background", "#ffffff")
            align = element.get("align", "left")
            font_family = element.get('font_family', "Inter, 'Microsoft YaHei', sans-serif")
            font_size = element.get('font_size', '1rem')
            bold = element.get('bold', False)
            underline = element.get('underline', False)
            strike = element.get('strike', False)
            text_with_breaks = text.replace('\n', '<br>')
            style_dec = f"font-family: {font_family}; font-size: {font_size}; font-weight: {'700' if bold else '400'}; text-decoration: {'line-through' if strike else ('underline' if underline else 'none')};"
            st.markdown(f"""
            <div style="color: {color}; background: {background}; padding: 20px; border-radius: 12px; margin: 15px 0; text-align: {align}; line-height: 1.7; border-left: 4px solid #667eea; {style_dec}">
                {text_with_breaks}
            </div>
            """, unsafe_allow_html=True)
        
        elif element["type"] == "note":
            text = element.get("text", "")
            author = element.get("author", "")
            color = element.get("color", "#666666")
            background = element.get("background", "#f8f9fa")
            font_family = element.get('font_family', "Inter, 'Microsoft YaHei', sans-serif")
            font_size = element.get('font_size', '1rem')
            underline = element.get('underline', False)
            author_html = f'<div style="text-align: right; color: #888; margin-top: 10px; font-style: italic;">— {author}</div>' if author else ''
            st.markdown(f"""
            <div style="background: {background}; color: {color}; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #667eea; font-style: italic; box-shadow: 0 5px 20px rgba(0,0,0,0.05); font-family: {font_family}; font-size: {font_size}; text-decoration: {'underline' if underline else 'none'};">
                <div style="font-size: 1.1em; margin-bottom: 10px;">"{text}"</div>
                {author_html}
            </div>
            """, unsafe_allow_html=True)
        
        elif element["type"] == "button":
            text = element.get("text", "点击这里")
            url = element.get("url", "#")
            color = element.get("color", "#ffffff")
            background = element.get("background", "#667eea")
            
            st.markdown(f"""
            <a href="{url}" target="_blank" style="display: inline-block; background: {background}; color: {color}; padding: 12px 30px; border-radius: 10px; text-decoration: none; font-weight: bold; margin: 15px 0; transition: all 0.3s; box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);"
               onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 10px 30px rgba(0,0,0,0.2)'"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 5px 20px rgba(102, 126, 234, 0.3)'">
                {text}
            </a>
            """, unsafe_allow_html=True)
        
        elif element["type"] == "video":
            video_id = element.get("video_id", "")
            title = element.get("title", "B站视频")
            
            embed_code = element.get("embed_code", "")
            if embed_code:
                # 直接使用用户提供的 iframe 代码
                st.markdown(embed_code, unsafe_allow_html=True)
            elif video_id:
                st.markdown(f"""
                <div style="margin: 20px 0;">
                    <h4 style="color: #2d3748; margin-bottom: 10px;">{title}</h4>
                    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 12px; background: #000; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                        <iframe src="https://player.bilibili.com/player.html?bvid={video_id}&page=1"
                                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
                                allowfullscreen>
                        </iframe>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("请添加B站视频ID")
        
        elif element["type"] == "image":
            src = element.get("src", "")
            alt = element.get("alt", "图片")
            caption = element.get("caption", "")
            img_src = src
            if src and not (src.startswith('http://') or src.startswith('https://') or src.startswith('/') or src.startswith('pictures/')):
                img_src = f'pictures/{src}'
            st.markdown(f"""
            <div style="text-align: {element.get('align', 'center')}; margin: 15px 0;">
                <img src="{img_src}" alt="{alt}" style="max-width: {element.get('width','100%')}; height: auto; border-radius: 8px;" />
                {f'<div style="color: #8da9c9; margin-top:8px;">{caption}</div>' if caption else ''}
            </div>
            """, unsafe_allow_html=True)

        elif element["type"] == "code":
            code = element.get("code", "")
            language = element.get("language", "text")
            escaped = html.escape(code)
            st.markdown(f"""
            <pre style="background: #0b1220; color: #cddbf6; padding:12px; border-radius:8px; overflow:auto;"><code class="language-{language}">{escaped}</code></pre>
            """, unsafe_allow_html=True)

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
        safe_rerun()
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
                safe_rerun()
            else:
                st.error(message)
                SessionStateManager.add_notification(f"删除失败: {message}", "error")
    
    with col_cancel:
        if st.button("❌ 取消", use_container_width=True):
            safe_rerun()

# ============================================
# 主页
# ============================================
def render_home():
    """渲染主页"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 头部
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">📖 网页手册创建器</h1>
        <p class="app-subtitle">
            一个强大、易用的网页手册制作工具，无需编程知识即可创建专业级别的响应式网页。
            支持一键部署到 GitHub Pages，让您的知识分享变得更简单。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    project_manager = ProjectManager()
    
    # 功能特性
    st.markdown("### ✨ 核心特性")
    cols = st.columns(3)
    
    features = [
        ("🎨 视觉设计", "现代化的UI设计，丰富的主题和样式选项", "#667eea", "提供多种主题和自定义选项，打造独特视觉风格"),
        ("📱 响应式布局", "完美适配桌面、平板和手机设备", "#764ba2", "自动适应各种屏幕尺寸，提供最佳浏览体验"),
        ("⚡ 高性能", "优化的代码结构，极速加载体验", "#f093fb", "轻量级代码，快速加载，提升用户体验"),
        ("🔧 易于使用", "直观的操作界面，拖拽式编辑", "#4fd1c7", "无需编程知识，简单点击即可创建专业网页"),
        ("📤 一键部署", "直接生成可部署的HTML文件", "#ed8936", "支持GitHub Pages、Netlify等主流部署平台"),
        ("🔄 实时预览", "编辑时即时查看效果，所见即所得", "#9f7aea", "实时预览功能，确保设计符合预期")
    ]
    
    for idx, (title, desc, color, detail) in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon" style="color: {color};">{title.split()[0]}</div>
                <h3 class="feature-title">{title}</h3>
                <p class="feature-desc">{desc}</p>
                <p style="color: #718096; font-size: 0.95rem; line-height: 1.6;">{detail}</p>
                <!-- 已移除“了解更多”按钮以简化界面 -->
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
                        st.selectbox("默认主题", ["light", "dark"], key="default_theme_home")
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
                        safe_rerun()
                
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
                                    safe_rerun()
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
            1. **输入项目名称**
            2. **添加项目描述**
            3. **点击创建按钮**
            4. **开始编辑内容**
            5. **保存并发布**
            
            ---
            
            **💡 提示:**
            - 项目名称建议简短明确
            - 描述可以帮助您后期管理
            - 高级设置可以后续修改
            """)
    
    with tab2:
        st.markdown("### 📂 我的项目")
        
        # 修复：使用project_manager正确获取项目列表
        projects = project_manager.list_projects()
        
        if not projects:
            st.info("""
            📭 还没有任何项目。
            
            点击上方的"创建项目"标签开始您的第一个项目！
            """)
        else:
            # 项目统计 - 修复数据获取
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            with col_stats1:
                st.metric("项目总数", len(projects))
            with col_stats2:
                completed = sum(1 for p in projects if p.get("has_html", False))
                st.metric("已生成HTML", completed)
            with col_stats3:
                total_size = sum(p.get("size", 0) for p in projects)
                st.metric("总大小", project_manager.format_size(total_size))
            with col_stats4:
                if projects:
                    # 修复：正确处理最后修改时间
                    latest_project = max(
                        [p for p in projects if p.get("config", {}).get("last_modified")], 
                        key=lambda x: x["config"]["last_modified"],
                        default=projects[0]
                    )
                    st.metric("最近更新", latest_project["name"][:10] + "...")
            
            # 项目列表 - 修复项目信息显示
            st.markdown("---")
            
            for project in projects:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        # 修复：确保获取到所有项目信息
                        project_name = project.get('name', '未命名项目')
                        config = project.get('config', {})
                        description = config.get('description', '无描述')
                        created_at = config.get('created_at', '').split('T')[0] if config.get('created_at') else '未知'
                        page_count = project.get('page_count', 0) + 1  # 包括封面页
                        version = config.get('version', '1.0')
                        
                        st.markdown(f"""
                        <div style="padding: 20px; background: white; border-radius: 15px; margin: 10px 0; box-shadow: 0 5px 20px rgba(0,0,0,0.05);">
                            <h4 style="color: #2d3748; margin: 0 0 10px 0; display: flex; align-items: center;">
                                <span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; margin-right: 10px;">
                                    v{version}
                                </span>
                                {project_name}
                            </h4>
                            <p style="color: #718096; margin: 0 0 8px 0; font-size: 0.95em;">
                                {description}
                            </p>
                            <div style="display: flex; gap: 15px; margin-top: 10px;">
                                <span style="color: #a0aec0; font-size: 0.85em;">
                                    <i class="fas fa-calendar"></i> {created_at}
                                </span>
                                <span style="color: #a0aec0; font-size: 0.85em;">
                                    <i class="fas fa-file-alt"></i> {project_manager.format_size(project.get('size', 0))}
                                </span>
                                <span style="color: #a0aec0; font-size: 0.85em;">
                                    <i class="fas fa-file"></i> {page_count}页
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # 修复：正确判断HTML文件状态
                        has_html = project.get("has_html", False)
                        if has_html:
                            st.markdown("""
                            <div style="padding: 10px; text-align: center; border-radius: 10px; background: rgba(16, 185, 129, 0.1); color: #10b981; font-weight: 600;">
                                ✅ 已生成HTML
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="padding: 10px; text-align: center; border-radius: 10px; background: rgba(245, 158, 11, 0.1); color: #f59e0b; font-weight: 600;">
                                ⏳ 未生成HTML
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col3:
                        if st.button("打开", 
                                    key=f"open_{project_name}", 
                                    use_container_width=True,
                                    help=f"打开项目: {project_name}"):
                            success, result = project_manager.load_project(project_name)
                            if success:
                                st.session_state.current_project = result
                                st.session_state.project_structure = result["structure"]
                                st.session_state.current_page = result["structure"]["cover_page"]
                                st.session_state.active_tab = "editor"
                                st.session_state.project_loaded = True
                                SessionStateManager.add_notification(f"已加载项目: {project_name}", "success")
                                safe_rerun()
                            else:
                                SessionStateManager.add_notification(f"加载失败: {result}", "error")
                    
                    with col4:
                        if st.button("删除", 
                                    key=f"delete_{project_name}", 
                                    type="secondary",
                                    use_container_width=True,
                                    help=f"删除项目: {project_name}"):
                            # 使用会话状态记录删除确认
                            confirm_key = f"confirm_delete_{project_name}"
                            if not st.session_state.get(confirm_key):
                                st.session_state[confirm_key] = True
                                safe_rerun()
    
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
                <div style="background: white; padding: 20px; border-radius: 15px; margin: 10px 0; border-left: 5px solid #667eea; box-shadow: 0 5px 20px rgba(0,0,0,0.05);">
                    <h4 style="color: #2d3748; margin: 0 0 10px 0; display: flex; align-items: center; gap: 10px;">
                        <span style="background: #667eea; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">
                            {step.split()[0]}
                        </span>
                        {step}
                    </h4>
                    <p style="color: #718096; margin: 0; padding-left: 46px;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 常见问题
        with st.expander("❓ 常见问题", expanded=False):
            faqs = [
                ("Q: 生成的HTML文件在哪里？", "A: 在项目文件夹下的index.html文件中"),
                ("Q: 如何部署到GitHub Pages？", "A: 将整个项目文件夹上传到GitHub仓库，在设置中启用GitHub Pages功能"),
                ("Q: 支持哪些内容类型？", "A: 支持标题、段落、注释、按钮、B站视频、图片、代码块等多种内容类型"),
                ("Q: 可以导出为其他格式吗？", "A: 目前只支持导出为HTML格式，后续会支持PDF导出"),
                ("Q: 数据会保存到哪里？", "A: 所有数据都保存在本地项目的文件夹中，不会上传到任何服务器"),
                ("Q: 侧边栏折叠后如何打开？", "A: 点击左上角的汉堡菜单按钮(≡)即可展开侧边栏"),
                ("Q: 支持键盘快捷键吗？", "A: 支持！Ctrl+B切换侧边栏，Ctrl+K打开搜索，方向键导航页面")
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
# 项目编辑器主页面
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
            safe_rerun()
        return
    
    # 顶部工具栏
    st.markdown(f"""
    <div style="background: white; padding: 25px 35px; border-radius: 20px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-left: 6px solid #667eea;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h2 style="color: #2d3748; margin: 0; display: flex; align-items: center; gap: 15px;">
                    <span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 20px; border-radius: 30px; font-size: 1.1rem; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                        📝 编辑中
                    </span>
                    {project['name']}
                </h2>
                <p style="color: #718096; margin: 8px 0 0 0; font-size: 1.05rem;">
                    {project['config'].get('description', '')}
                </p>
            </div>
            <div style="display: flex; gap: 12px;">
                <button onclick="window.location.href='?tab=home'" style="background: #f8fafc; border: 2px solid #e2e8f0; color: #4a5568; padding: 12px 25px; border-radius: 12px; cursor: pointer; font-weight: 600; transition: all 0.3s; display: flex; align-items: center; gap: 8px;"
                        onmouseover="this.style.background='#e2e8f0'; this.style.transform='translateY(-2px)'"
                        onmouseout="this.style.background='#f8fafc'; this.style.transform='translateY(0)'">
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
                        ["light", "dark", "auto"],
                        index=["light", "dark", "auto"].index(structure['config'].get('theme', 'light'))
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

    # 如果需要滚动到某个元素（由编辑操作触发），注入前端脚本执行平滑滚动
    if st.session_state.get('_scroll_to_element'):
        target = st.session_state.pop('_scroll_to_element')
        js = f"""
        <script>
        (function(){{
            var id = 'elem-{target}';
            var el = document.getElementById(id);
            if (el) {{
                el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
            }} else {{
                var tries = 0;
                var t = setInterval(function(){{
                    tries += 1;
                    var e = document.getElementById(id);
                    if (e) {{ e.scrollIntoView({{behavior: 'smooth', block: 'center'}}); clearInterval(t); }}
                    if (tries > 10) clearInterval(t);
                }}, 200);
            }}
        }})();
        </script>
        """
        components.html(js, height=1)
    
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
                safe_rerun()
    
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
                safe_rerun()
    
    with col_bottom4:
        if st.button("🏠 返回主页", 
                    use_container_width=True,
                    type="secondary",
                    help="返回主页"):
            st.session_state.active_tab = "home"
            st.session_state.current_project = None
            safe_rerun()

# ============================================
# 主应用入口
# ============================================
def main():
    # 加载CSS
    load_css()
    # 注入全局脚本：在任何按钮点击前保存滚动位置，并在渲染时恢复，防止重跑导致页面跳顶
    components.html("""
    <script>
    (function(){
        // 保存滚动位置到 localStorage：使用 mousedown/touchstart 提前捕获（比 click 更早）
        function saveScroll() {
            try { localStorage.setItem('manual_creator_scroll', window.pageYOffset); } catch(e){}
        }

        document.addEventListener('mousedown', function(e){
            var btn = e.target.closest('button');
            if (btn) saveScroll();
        }, true);

        document.addEventListener('touchstart', function(e){
            var btn = e.target.closest('button');
            if (btn) saveScroll();
        }, true);

        // 防止按钮获得焦点后触发浏览器自动滚动：在 focusin 后快速失焦
        document.addEventListener('focusin', function(e){
            try {
                var t = e.target;
                if (t && (t.tagName === 'BUTTON' || t.getAttribute && t.getAttribute('role') === 'button')) {
                    setTimeout(function(){ try{ t.blur(); } catch(e){} }, 10);
                }
            } catch(e){}
        }, true);

        // 页面加载后尝试多次恢复滚动位置，兼容 Streamlit 重渲染
        window.addEventListener('load', function(){
            try{
                var attempts = 0;
                var y = localStorage.getItem('manual_creator_scroll');
                if (y !== null) {
                    var target = parseInt(y);
                    var restore = setInterval(function(){
                        window.scrollTo(0, target);
                        attempts += 1;
                        // 在恢复后清理并移除本地存储
                        if (attempts > 6) {
                            try { localStorage.removeItem('manual_creator_scroll'); } catch(e){}
                            clearInterval(restore);
                        }
                    }, 120);
                }
            }catch(e){}
        });
    })();
    </script>
    """, height=1)
    
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
                safe_rerun()
        with col_home:
            if st.button("🏠 返回主页", use_container_width=True):
                st.session_state.active_tab = "home"
                st.session_state.current_project = None
                safe_rerun()

if __name__ == "__main__":
    # 错误处理
    try:
        main()
    except Exception as e:
        st.error(f"应用程序启动失败: {str(e)}")
        st.info("请确保所有依赖已正确安装，并检查文件权限")
        st.code("pip install streamlit", language="bash")