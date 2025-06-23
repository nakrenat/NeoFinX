import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import sqlite3
import os
import requests
import json
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import statistics
import math
from dotenv import load_dotenv
import openai
import pandas as pd
from personality_analyzer import PersonalityAnalyzer

# .env dosyasını yükle
load_dotenv()

# Modern sayfa konfigürasyonu
st.set_page_config(
    page_title="NeoFinX - Akıllı Bütçe Asistanı",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode toggle - Prominente yerleştirme
st.sidebar.markdown("---")
dark_mode = st.sidebar.checkbox("🌙 **Dark Mode**", value=False, key="dark_mode_toggle", help="Karanlık tema ile göz yorgunluğunu azaltın")
st.sidebar.markdown("---")

# Dynamic CSS based on dark mode
if dark_mode:
    # Dark mode CSS - Modern Theme
    st.markdown("""
    <style>
        /* Modern Dark theme renkleri */
        :root {
            --primary-color: #8b5cf6;
            --secondary-color: #06b6d4;
            --accent-color: #3b82f6;
            --success-color: #059669;
            --warning-color: #d97706;
            --danger-color: #dc2626;
            --bg-color: linear-gradient(135deg, #0f172a, #1e293b);
            --card-bg: linear-gradient(145deg, #1e293b, #334155);
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --border-color: #475569;
            --input-bg: rgba(30, 41, 59, 0.8);
            --sidebar-bg: linear-gradient(180deg, #0f172a, #334155);
            --shadow-light: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
            --shadow-heavy: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }
        
        /* Ana body ve container - Modern Dark */
        .stApp {
            background: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            background: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main {
            background: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Sidebar dark - güçlü selector'lar */
        .css-1d391kg, .css-1oe6wy4, .sidebar .sidebar-content {
            background: linear-gradient(180deg, var(--sidebar-bg), #1e293b) !important;
        }
        
        /* Streamlit'in varsayılan beyaz arka planını override et */
        [data-testid="stApp"] {
            background-color: var(--bg-color) !important;
        }
        
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* Tüm section'ları dark yap */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--sidebar-bg), #1e293b) !important;
        }
        
        section[data-testid="stSidebar"] > div {
            background: linear-gradient(180deg, var(--sidebar-bg), #1e293b) !important;
        }
        
        /* Main header dark */
        .main-header {
            background: linear-gradient(135deg, #4338ca, #6366f1);
            color: white;
        }
        
        /* Kartlar dark - Modern Glass */
        [data-testid="metric-container"] {
            background: var(--card-bg) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: var(--text-primary) !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: var(--shadow-medium) !important;
            border-radius: 16px !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        [data-testid="metric-container"]::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            height: 3px !important;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color)) !important;
            border-radius: 16px 16px 0 0 !important;
        }
        
        [data-testid="metric-container"] > div {
            color: var(--text-primary) !important;
        }
        
        [data-testid="metric-container"] label {
            color: var(--text-secondary) !important;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-4px) !important;
            box-shadow: var(--shadow-heavy) !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
        }
        
        /* Tüm text elementleri dark - GÜÇLÜ SELECTOR'LAR */
        .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: var(--text-primary) !important;
        }
        
        /* Streamlit native text elements */
        div[data-testid="stMarkdown"] {
            color: var(--text-primary) !important;
        }
        
        div[data-testid="stMarkdown"] * {
            color: var(--text-primary) !important;
        }
        
        /* Sidebar text elements */
        .css-1d391kg * {
            color: var(--text-primary) !important;
        }
        
        section[data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }
        
        /* Tüm yazı elementleri için global override */
        p, span, div, h1, h2, h3, h4, h5, h6, label, strong, em, li, ul, ol {
            color: var(--text-primary) !important;
        }
        
        /* Streamlit specific text */
        .stSelectbox label, .stNumberInput label, .stTextInput label, .stDateInput label {
            color: var(--text-secondary) !important;
        }
        
        /* Form container dark */
        [data-testid="stForm"] {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Input field'lar dark - güçlü selector'lar */
        .stSelectbox > div > div, [data-testid="stSelectbox"] > div {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stSelectbox > div > div > div {
            color: var(--text-primary) !important;
        }
        
        .stSelectbox div[role="listbox"] {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stSelectbox div[role="option"] {
            background-color: var(--input-bg) !important;
            color: var(--text-primary) !important;
        }
        
        .stSelectbox div[role="option"]:hover {
            background-color: var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stNumberInput > div > div > input, [data-testid="stNumberInput"] input {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stTextInput > div > div > input, [data-testid="stTextInput"] input {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stDateInput > div > div > input, [data-testid="stDateInput"] input {
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Placeholder text */
        .stSelectbox input::placeholder, .stNumberInput input::placeholder, .stTextInput input::placeholder {
            color: var(--text-secondary) !important;
        }
        
        /* Checkbox dark */
        .stCheckbox > label {
            color: var(--text-primary) !important;
        }
        
        /* Radio buttons dark - Sidebar sayfa seçimi */
        .stRadio > div {
            background: transparent !important;
        }
        
        .stRadio > div > label {
            color: var(--text-primary) !important;
            background: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            margin: 0.25rem 0 !important;
            transition: all 0.3s ease !important;
            display: block !important;
            cursor: pointer !important;
        }
        
        .stRadio > div > label:hover {
            background: var(--primary-color) !important;
            color: white !important;
            border-color: var(--primary-color) !important;
            transform: translateX(5px) !important;
        }
        
        .stRadio > div > label[data-checked="true"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border-color: var(--primary-color) !important;
            box-shadow: var(--shadow-medium) !important;
        }
        
        /* Radio input gizle */
        .stRadio input[type="radio"] {
            display: none !important;
        }
        
        /* Sidebar widget'ları genel */
        .css-1d391kg .stRadio,
        .css-1d391kg .stSelectbox,
        section[data-testid="stSidebar"] .stRadio,
        section[data-testid="stSidebar"] .stSelectbox {
            background: transparent !important;
        }
        
        /* Sidebar radio seçenekleri */
        .css-1d391kg .stRadio > div > label,
        section[data-testid="stSidebar"] .stRadio > div > label {
            background: rgba(30, 41, 59, 0.8) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px !important;
            padding: 0.75rem 1rem !important;
            margin: 0.3rem 0 !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        .css-1d391kg .stRadio > div > label:hover,
        section[data-testid="stSidebar"] .stRadio > div > label:hover {
            background: var(--primary-color) !important;
            color: white !important;
            transform: translateX(8px) !important;
            box-shadow: var(--shadow-light) !important;
        }
        
        /* Modern Streamlit Radio Buttons Dark */
        [data-testid="stSidebar"] [data-baseweb="radio"] {
            background: transparent !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="radio"] > div {
            background: transparent !important;
            gap: 0.5rem !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="radio"] label {
            background: rgba(30, 41, 59, 0.8) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 0.8rem 1.2rem !important;
            margin: 0.3rem 0 !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            display: block !important;
            width: 100% !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="radio"] label:hover {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            transform: translateX(8px) !important;
            box-shadow: var(--shadow-light) !important;
            border-color: var(--primary-color) !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="radio"] label[data-checked="true"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border-color: var(--accent-color) !important;
            box-shadow: var(--shadow-medium) !important;
        }
        
        /* Radio input circles gizle */
        [data-testid="stSidebar"] [data-baseweb="radio"] input {
            display: none !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="radio"] span[role="radio"] {
            display: none !important;
        }
        
        /* Sidebar selectbox dark - ULTRA GÜÇLÜ */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background: rgba(30, 41, 59, 0.9) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
            border-radius: 12px !important;
            padding: 0.8rem !important;
            font-weight: 500 !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox > div > div > div {
            color: var(--text-primary) !important;
            background: transparent !important;
        }
        
        /* Selectbox dropdown menüsü - SÜPER GÜÇLÜ */
        [data-testid="stSidebar"] .stSelectbox div[role="listbox"] {
            background: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            color: var(--text-primary) !important;
            box-shadow: var(--shadow-heavy) !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox div[role="option"] {
            background: transparent !important;
            color: var(--text-primary) !important;
            padding: 0.8rem 1rem !important;
            border-radius: 8px !important;
            margin: 0.2rem !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox div[role="option"]:hover {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            transform: translateX(5px) !important;
        }
        
        /* EN GÜÇLÜ DROPDOWN OVERRIDE */
        body [data-baseweb="popover"] {
            background: var(--card-bg) !important;
        }
        
        body [data-baseweb="popover"] > div {
            background: var(--card-bg) !important;
        }
        
        body [data-baseweb="popover"] [data-baseweb="menu"] {
            background: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
        }
        
        body [data-baseweb="popover"] [role="option"] {
            background: transparent !important;
            color: var(--text-primary) !important;
        }
        
        body [data-baseweb="popover"] [role="option"]:hover {
            background: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Dropdown container'ın arka planı */
        [data-baseweb="popover"] [data-baseweb="menu"] > ul {
            background: var(--card-bg) !important;
            color: var(--text-primary) !important;
        }
        
        [data-baseweb="popover"] [data-baseweb="menu"] ul li {
            background: transparent !important;
            color: var(--text-primary) !important;
        }
        
        /* Selectbox label */
        [data-testid="stSidebar"] .stSelectbox label {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Sidebar başlıkları */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] .css-1d391kg h1,
        [data-testid="stSidebar"] .css-1d391kg h2,
        [data-testid="stSidebar"] .css-1d391kg h3 {
            color: var(--text-primary) !important;
        }
        
        /* Buton dark - güçlü selector'lar */
        .stButton > button, [data-testid="stButton"] button {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border: 2px solid transparent !important;
        }
        
        /* Ekspander dark */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, var(--card-bg), #334155);
            color: var(--text-primary);
        }
        
        /* Grafik container dark */
        .js-plotly-plot {
            background: var(--card-bg);
        }
        
        /* Success/Error mesajları dark */
        .stSuccess {
            background: linear-gradient(90deg, #064e3b, #065f46);
            color: #d1fae5;
        }
        
        .stError {
            background: linear-gradient(90deg, #7f1d1d, #991b1b);
            color: #fecaca;
        }
        
        .stWarning {
            background: linear-gradient(90deg, #78350f, #92400e);
            color: #fed7aa;
        }
        
        .stInfo {
            background: linear-gradient(90deg, #1e3a8a, #1e40af);
            color: #dbeafe;
        }
        
        /* Global dark theme override - En güçlü selector'lar */
        html, body {
            background: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* ULTIMATE DROPDOWN FIX */
        [class*="baseweb"] [role="listbox"],
        [class*="baseweb"] [data-baseweb="popover"],
        [class*="baseweb"] [data-baseweb="menu"],
        div[role="listbox"],
        ul[role="listbox"] {
            background: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        [class*="baseweb"] [role="option"],
        [role="option"],
        li[role="option"] {
            background: transparent !important;
            color: var(--text-primary) !important;
        }
        
        [class*="baseweb"] [role="option"]:hover,
        [role="option"]:hover,
        li[role="option"]:hover {
            background: var(--primary-color) !important;
            color: white !important;
        }
        
        .main > .block-container {
            background: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Ultra güçlü text color override */
        * {
            color: var(--text-primary) !important;
        }
        
        /* Modern Streamlit Selectbox - Sidebar */
        [data-testid="stSidebar"] [data-baseweb="select"] {
            background: rgba(30, 41, 59, 0.9) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: transparent !important;
            color: var(--text-primary) !important;
            font-weight: 500 !important;
            padding: 0.8rem !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"] {
            color: var(--text-primary) !important;
            background: transparent !important;
        }
        
        /* Dropdown menu - ULTRA GÜÇLÜ */
        [data-baseweb="popover"] [data-baseweb="menu"] {
            background: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            box-shadow: var(--shadow-heavy) !important;
        }
        
        [data-baseweb="popover"] [role="option"] {
            background: transparent !important;
            color: var(--text-primary) !important;
            padding: 0.8rem 1rem !important;
            border-radius: 8px !important;
            margin: 0.2rem !important;
            transition: all 0.3s ease !important;
        }
        
        [data-baseweb="popover"] [role="option"]:hover {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
        }
        
        /* Çok daha güçlü dropdown selector'ları */
        .css-1d391kg [data-baseweb="popover"],
        section[data-testid="stSidebar"] [data-baseweb="popover"],
        [data-testid="stSidebar"] [data-baseweb="popover"] {
            background: var(--card-bg) !important;
        }
        
        .css-1d391kg [data-baseweb="popover"] [data-baseweb="menu"],
        section[data-testid="stSidebar"] [data-baseweb="popover"] [data-baseweb="menu"],
        [data-testid="stSidebar"] [data-baseweb="popover"] [data-baseweb="menu"] {
            background: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .css-1d391kg [role="option"],
        section[data-testid="stSidebar"] [role="option"],
        [data-testid="stSidebar"] [role="option"] {
            background: transparent !important;
            color: var(--text-primary) !important;
        }
        
        /* Streamlit'in beyaz dropdown'ını override et */
        div[data-baseweb="popover"] {
            background: var(--card-bg) !important;
        }
        
        div[data-baseweb="popover"] ul {
            background: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
        }
        
        div[data-baseweb="popover"] li {
            background: transparent !important;
            color: var(--text-primary) !important;
        }
        
        div[data-baseweb="popover"] li:hover {
            background: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Streamlit specific overrides */
        .stApp, .stApp * {
            color: var(--text-primary) !important;
        }
        
        /* Tab content text */
        .stTabs [data-baseweb="tab-list"] {
            color: var(--text-primary) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-primary) !important;
        }
        
        /* Column text */
        .stColumn, .stColumn * {
            color: var(--text-primary) !important;
        }
        
        /* Container text */
        .stContainer, .stContainer * {
            color: var(--text-primary) !important;
        }
        
        /* Radio, checkbox, multi-select */
        .stRadio label, .stCheckbox label, .stMultiSelect label {
            color: var(--text-primary) !important;
        }
        
        /* Metric labels and values */
        [data-testid="metric-container"] div {
            color: var(--text-primary) !important;
        }
        
        [data-testid="metric-container"] [data-testid="metric-label"] {
            color: var(--text-secondary) !important;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            color: var(--text-primary) !important;
        }
        
        /* Ekspander ve diğer widget'lar */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, var(--card-bg), var(--border-color)) !important;
            color: var(--text-primary) !important;
        }
        
        .streamlit-expanderContent {
            background: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .streamlit-expanderContent * {
            color: var(--text-primary) !important;
        }
        
        /* Divider */
        hr {
            border-color: var(--border-color) !important;
        }
        
        /* Code blocks */
        code {
            background: var(--input-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        pre {
            background: var(--input-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Tablo dark */
        .stDataFrame {
            background: var(--card-bg) !important;
            color: var(--text-primary) !important;
        }
        
        .stDataFrame table {
            background: var(--card-bg) !important;
            color: var(--text-primary) !important;
        }
        
        .stDataFrame th {
            background: var(--input-bg) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }
        
        .stDataFrame td {
            background: var(--card-bg) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }
        
        /* DataFrame component */
        [data-testid="stDataFrame"] {
            background: var(--card-bg) !important;
        }
        
        [data-testid="stDataFrame"] * {
            color: var(--text-primary) !important;
        }
        
        /* Grafik container'ları dark */
        [data-testid="stPlotlyChart"] {
            background-color: var(--card-bg) !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Light mode CSS - Modern Theme
    st.markdown("""
    <style>
        /* Modern Light theme renkleri */
        :root {
            --primary-color: #6366f1;
            --secondary-color: #8b5cf6;
            --accent-color: #06b6d4;
            --success-color: #059669;
            --warning-color: #d97706;
            --danger-color: #dc2626;
            --bg-color: #f8fafc;
            --card-bg: linear-gradient(145deg, #ffffff, #f1f5f9);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --border-color: #e2e8f0;
            --input-bg: #ffffff;
            --sidebar-bg: linear-gradient(180deg, #f1f5f9, #e2e8f0);
            --shadow-light: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-heavy: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        
        /* Ana container light - güçlü selector'lar */
        .stApp {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main .block-container {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        .main {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Sidebar modern - güçlü selector'lar */
        .css-1d391kg, .css-1oe6wy4, .sidebar .sidebar-content {
            background: var(--sidebar-bg) !important;
        }
        
        [data-testid="stApp"] {
            background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
        }
        
        section[data-testid="stSidebar"] {
            background: var(--sidebar-bg) !important;
        }
        
        section[data-testid="stSidebar"] > div {
            background: var(--sidebar-bg) !important;
        }
    
    /* Genel görünüm */
    .main {
        padding-top: 1rem;
    }
    
    /* Başlık stilleri - Modern */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-heavy);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Buton stilleri */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        border: 2px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Sidebar stilleri - Modern Glass */
    .css-1d391kg {
        background: var(--sidebar-bg);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Metrik kartları - Modern Glass Effect */
    [data-testid="metric-container"] {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: var(--shadow-medium);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-heavy);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        border-radius: 16px 16px 0 0;
    }
    
    /* Form stilleri - Modern Glass */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid rgba(226, 232, 240, 0.5);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        background: rgba(255, 255, 255, 0.95);
    }
    
    .stNumberInput > div > div > input {
        border-radius: 12px;
        border: 2px solid rgba(226, 232, 240, 0.5);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        background: rgba(255, 255, 255, 0.95);
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid rgba(226, 232, 240, 0.5);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
        background: rgba(255, 255, 255, 0.95);
    }
    
    /* Ekspander stilleri - Modern Glass */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(241, 245, 249, 0.8));
        border-radius: 12px;
        border: 1px solid rgba(226, 232, 240, 0.5);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: var(--shadow-light);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Success/Error mesajları */
    .stSuccess {
        background: linear-gradient(90deg, #dcfce7, #bbf7d0);
        border-left: 4px solid var(--success-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    .stError {
        background: linear-gradient(90deg, #fef2f2, #fecaca);
        border-left: 4px solid var(--danger-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    .stWarning {
        background: linear-gradient(90deg, #fffbeb, #fed7aa);
        border-left: 4px solid var(--warning-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    .stInfo {
        background: linear-gradient(90deg, #eff6ff, #dbeafe);
        border-left: 4px solid var(--primary-color);
        border-radius: 10px;
        animation: slideIn 0.3s ease;
    }
    
    /* Animasyonlar */
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Grafik konteyneri - Modern */
    .js-plotly-plot {
        border-radius: 16px;
        box-shadow: var(--shadow-medium);
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .js-plotly-plot:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-heavy);
    }
    
    /* Modern Pulse Animation */
    @keyframes modernPulse {
        0% { 
            box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4);
        }
        70% { 
            box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
        }
    }
    
    /* Loading states */
    .stSpinner {
        animation: modernPulse 2s infinite;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(241, 245, 249, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
    }
        background: white;
    }
</style>
""", unsafe_allow_html=True)

# Veritabanı bağlantısı
DB_PATH = "data/neofinx.db"

# Para birimi ve kur fonksiyonları
@st.cache_data(ttl=3600)  # 1 saat cache
def get_exchange_rates():
    """Güncel döviz kurlarını getir"""
    try:
        # Merkez Bankası API'si
        url = "https://api.exchangerate-api.com/v4/latest/TRY"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # TRY bazında kurlar, bize ters kurlar lazım (diğer para birimlerini TRY'ye çevirmek için)
            rates = data.get('rates', {})
            
            # Manuel olarak popüler kurları ekleyelim (fallback)
            exchange_rates = {
                'TRY': 1.0,
                'USD': 32.50,  # Fallback değerler
                'EUR': 35.20,
                'GBP': 41.80,
                'CHF': 36.40,
                'CAD': 24.10,
                'AUD': 21.30,
                'JPY': 0.22,
                'CNY': 4.52,
                'RUB': 0.35
            }
            
            # API'den gelen kurları kullan (eğer varsa)
            if rates:
                for currency in exchange_rates.keys():
                    if currency in rates and rates[currency] > 0:
                        # TRY bazından diğer para birimine ters kur hesapla
                        exchange_rates[currency] = 1.0 / rates[currency]
            
            return exchange_rates
            
        else:
            raise Exception("API yanıt vermedi")
            
    except Exception as e:
        st.warning(f"⚠️ Kur bilgileri alınamadı, manuel kurlar kullanılıyor: {str(e)}")
        # Manuel fallback kurlar
        return {
            'TRY': 1.0,
            'USD': 32.50,
            'EUR': 35.20,
            'GBP': 41.80,
            'CHF': 36.40,
            'CAD': 24.10,
            'AUD': 21.30,
            'JPY': 0.22,
            'CNY': 4.52,
            'RUB': 0.35
        }

def convert_to_try(amount, currency, exchange_rates):
    """Para birimini TRY'ye çevir"""
    if currency == 'TRY':
        return amount
    
    rate = exchange_rates.get(currency, 1.0)
    return amount * rate

def format_currency_display(amount, currency):
    """Para birimi ile görünüm formatı"""
    currency_symbols = {
        'TRY': '₺',
        'USD': '$',
        'EUR': '€', 
        'GBP': '£',
        'CHF': 'CHF',
        'CAD': 'C$',
        'AUD': 'A$',
        'JPY': '¥',
        'CNY': '¥',
        'RUB': '₽'
    }
    
    symbol = currency_symbols.get(currency, currency)
    if currency in ['JPY', 'CNY']:
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

# Yatırım fiyat takibi fonksiyonları
@st.cache_data(ttl=3600)  # 1 saat cache
def get_crypto_prices():
    """Kripto para fiyatlarını getir"""
    try:
        # CoinGecko API'si - ücretsiz
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,try"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'BTC': {
                    'price_usd': data.get('bitcoin', {}).get('usd', 0),
                    'price_try': data.get('bitcoin', {}).get('try', 0)
                },
                'ETH': {
                    'price_usd': data.get('ethereum', {}).get('usd', 0),
                    'price_try': data.get('ethereum', {}).get('try', 0)
                }
            }
        else:
            raise Exception("API yanıt vermedi")
            
    except Exception as e:
        # Fallback fiyatlar
        return {
            'BTC': {'price_usd': 43000, 'price_try': 1395000},
            'ETH': {'price_usd': 2600, 'price_try': 84500}
        }

@st.cache_data(ttl=3600)  # 1 saat cache  
def get_precious_metal_prices():
    """Değerli metal fiyatlarını getir"""
    try:
        # Metal fiyatları için API
        url = "https://api.metals.live/v1/spot"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            exchange_rates = get_exchange_rates()
            usd_to_try = exchange_rates.get('USD', 32.5)
            
            return {
                'GOLD': {
                    'price_usd': data.get('gold', 2000),
                    'price_try': data.get('gold', 2000) * usd_to_try
                },
                'SILVER': {
                    'price_usd': data.get('silver', 25),
                    'price_try': data.get('silver', 25) * usd_to_try
                }
            }
        else:
            raise Exception("API yanıt vermedi")
            
    except Exception as e:
        # Fallback fiyatlar
        exchange_rates = get_exchange_rates()
        usd_to_try = exchange_rates.get('USD', 32.5)
        return {
            'GOLD': {'price_usd': 2000, 'price_try': 2000 * usd_to_try},
            'SILVER': {'price_usd': 25, 'price_try': 25 * usd_to_try}
        }

@st.cache_data(ttl=3600)  # 1 saat cache
def get_stock_prices():
    """Hisse senedi ve endeks fiyatlarını getir"""
    try:
        # Yahoo Finance alternatifi - Alpha Vantage (free tier)
        # Bu örnek için manuel fiyatlar kullanacağız
        exchange_rates = get_exchange_rates()
        usd_to_try = exchange_rates.get('USD', 32.5)
        
        return {
            'XU100': {'price_try': 9500, 'change_percent': 1.5},
            'SPX': {'price_usd': 4800, 'price_try': 4800 * usd_to_try, 'change_percent': 0.8},
            'IXIC': {'price_usd': 15000, 'price_try': 15000 * usd_to_try, 'change_percent': -0.3}
        }
        
    except Exception as e:
        # Fallback fiyatlar
        exchange_rates = get_exchange_rates()
        usd_to_try = exchange_rates.get('USD', 32.5)
        return {
            'XU100': {'price_try': 9500, 'change_percent': 1.5},
            'SPX': {'price_usd': 4800, 'price_try': 4800 * usd_to_try, 'change_percent': 0.8},
            'IXIC': {'price_usd': 15000, 'price_try': 15000 * usd_to_try, 'change_percent': -0.3}
        }

@st.cache_data(ttl=3600)  # 1 saat cache
def get_all_investment_prices():
    """Tüm yatırım araçlarının fiyatlarını getir"""
    exchange_rates = get_exchange_rates()
    crypto_prices = get_crypto_prices()
    metal_prices = get_precious_metal_prices()
    stock_prices = get_stock_prices()
    
    all_prices = {}
    
    # Döviz kurları
    for currency, rate in exchange_rates.items():
        if currency != 'TRY':
            all_prices[currency] = {
                'name': currency,
                'price_try': rate,
                'type': 'currency',
                'change_percent': 0  # API'den gerçek değişim yüzdesi alınabilir
            }
    
    # Kripto paralar
    for symbol, data in crypto_prices.items():
        all_prices[symbol] = {
            'name': 'Bitcoin' if symbol == 'BTC' else 'Ethereum',
            'price_try': data['price_try'],
            'price_usd': data['price_usd'],
            'type': 'crypto',
            'change_percent': 0  # API'den gerçek değişim yüzdesi alınabilir
        }
    
    # Değerli metaller
    for symbol, data in metal_prices.items():
        name = 'Altın (Ons)' if symbol == 'GOLD' else 'Gümüş (Ons)'
        all_prices[symbol] = {
            'name': name,
            'price_try': data['price_try'],
            'price_usd': data['price_usd'],
            'type': 'precious_metal',
            'change_percent': 0
        }
    
    # Hisse senedi endeksleri
    for symbol, data in stock_prices.items():
        names = {'XU100': 'BIST 100', 'SPX': 'S&P 500', 'IXIC': 'Nasdaq'}
        all_prices[symbol] = {
            'name': names.get(symbol, symbol),
            'price_try': data.get('price_try', data.get('price_usd', 0)),
            'type': 'stock_index',
            'change_percent': data.get('change_percent', 0)
        }
    
    return all_prices

def init_database():
    """Veritabanını başlat"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        cursor = conn.cursor()
        
        # Kategoriler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#3498db'
            )
        ''')
        
        # Harcamalar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                original_amount REAL,
                currency TEXT DEFAULT 'TRY',
                exchange_rate REAL DEFAULT 1.0,
                description TEXT,
                category_id INTEGER,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Mevcut verilere para birimi sütunları ekle (eğer yoksa)
        try:
            cursor.execute('ALTER TABLE expenses ADD COLUMN original_amount REAL')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE expenses ADD COLUMN currency TEXT DEFAULT "TRY"')
        except:
            pass
        try:
            cursor.execute('ALTER TABLE expenses ADD COLUMN exchange_rate REAL DEFAULT 1.0')
        except:
            pass
        
        # Mevcut NULL değerleri düzelt
        cursor.execute('''
            UPDATE expenses 
            SET original_amount = amount, currency = 'TRY', exchange_rate = 1.0 
            WHERE original_amount IS NULL OR currency IS NULL OR exchange_rate IS NULL
        ''')
        
        # Test için örnek farklı para birimi verileri ekle (sadece bir kez)
        cursor.execute('SELECT COUNT(*) FROM expenses WHERE currency != "TRY"')
        foreign_count = cursor.fetchone()[0]
        
        if foreign_count == 0:
            # Test verileri ekle
            test_expenses = [
                (325.0, 10.0, 'USD', 32.5, 'Starbucks kahve', 1, '2024-01-20'),
                (704.0, 20.0, 'EUR', 35.2, 'Amazon alışveriş', 5, '2024-01-21'), 
                (418.0, 10.0, 'GBP', 41.8, 'Uber ride', 2, '2024-01-22'),
                (182.0, 5.0, 'USD', 36.4, 'Apple App Store', 3, '2024-01-23'),
                (1760.0, 50.0, 'EUR', 35.2, 'Hotel booking', 3, '2024-01-24')
            ]
            
            for tl_amount, orig_amount, currency, rate, desc, cat_id, date_str in test_expenses:
                cursor.execute('''
                    INSERT INTO expenses (amount, original_amount, currency, exchange_rate, description, category_id, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (tl_amount, orig_amount, currency, rate, desc, cat_id, date_str))
        
        # Yatırım türleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investment_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                symbol TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                icon TEXT DEFAULT '📈',
                currency TEXT DEFAULT 'TRY',
                api_source TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Yatırımlar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                investment_type_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                quantity REAL NOT NULL,
                purchase_price REAL NOT NULL,
                purchase_date DATE NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (investment_type_id) REFERENCES investment_types (id)
            )
        ''')
        
        # Yatırım fiyat geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investment_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investment_type_id INTEGER NOT NULL,
                price REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (investment_type_id) REFERENCES investment_types (id)
            )
        ''')
        
        # Varsayılan kategoriler ekle
        default_categories = [
            ('Yemek', '#e74c3c'),
            ('Ulaşım', '#3498db'),
            ('Eğlence', '#9b59b6'),
            ('Sağlık', '#2ecc71'),
            ('Alışveriş', '#f39c12'),
            ('Faturalar', '#34495e'),
            ('Diğer', '#95a5a6')
        ]
        
        for cat_name, color in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)
            ''', (cat_name, color))
        
        # Varsayılan yatırım türlerini ekle
        default_investments = [
            ('Dolar', 'USD', 'currency', '💵', 'USD'),
            ('Euro', 'EUR', 'currency', '💶', 'EUR'),
            ('Sterlin', 'GBP', 'currency', '💷', 'GBP'),
            ('Altın (Ons)', 'GOLD', 'precious_metal', '🥇', 'USD'),
            ('Gümüş (Ons)', 'SILVER', 'precious_metal', '🥈', 'USD'),
            ('Bitcoin', 'BTC', 'crypto', '₿', 'USD'),
            ('Ethereum', 'ETH', 'crypto', '⟠', 'USD'),
            ('BIST 100', 'XU100', 'stock_index', '📊', 'TRY'),
            ('S&P 500', 'SPX', 'stock_index', '📈', 'USD'),
            ('Nasdaq', 'IXIC', 'stock_index', '💻', 'USD')
        ]
        
        for name, symbol, inv_type, icon, currency in default_investments:
            cursor.execute('''
                INSERT OR IGNORE INTO investment_types (name, symbol, type, icon, currency)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, symbol, inv_type, icon, currency))
        
        conn.commit()
        
    except Exception as e:
        st.error(f"Veritabanı başlatma hatası: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_expense(amount, description, category_id, date, currency='TRY', exchange_rate=1.0):
    """Yeni harcama ekle"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Original amount (girilen miktar)
        original_amount = amount
        
        # TL karşılığı hesaplama
        if currency != 'TRY':
            tl_amount = amount * exchange_rate
        else:
            tl_amount = amount
        
        cursor.execute('''
            INSERT INTO expenses (amount, original_amount, currency, exchange_rate, description, category_id, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tl_amount, original_amount, currency, exchange_rate, description, category_id, date))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Harcama ekleme hatası: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_categories():
    """Kategorileri getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, color FROM categories')
        categories = cursor.fetchall()
        return categories
    except Exception as e:
        st.error(f"Kategori getirme hatası: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

# Yatırım veritabanı fonksiyonları
def get_investment_types():
    """Mevcut yatırım türlerini getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, symbol, type, icon, currency FROM investment_types WHERE is_active = 1')
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Yatırım türleri alınırken hata: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def add_investment(investment_type_id, amount, quantity, purchase_price, purchase_date, description=''):
    """Yeni yatırım ekle"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO investments (user_id, investment_type_id, amount, quantity, purchase_price, purchase_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (1, investment_type_id, amount, quantity, purchase_price, purchase_date, description))  # user_id=1 for demo
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Yatırım eklenirken hata: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_user_investments():
    """Kullanıcının yatırımlarını getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.id, i.amount, i.quantity, i.purchase_price, i.purchase_date, i.description,
                   it.name, it.symbol, it.type, it.icon, it.currency
            FROM investments i
            JOIN investment_types it ON i.investment_type_id = it.id
            WHERE i.user_id = 1 AND i.is_active = 1
            ORDER BY i.created_at DESC
        ''')
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Yatırımlar alınırken hata: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def calculate_portfolio_performance():
    """Portföy performansını hesapla"""
    investments = get_user_investments()
    current_prices = get_all_investment_prices()
    
    portfolio = []
    total_investment = 0
    total_current_value = 0
    
    for inv in investments:
        (inv_id, amount, quantity, purchase_price, purchase_date, description, 
         name, symbol, inv_type, icon, currency) = inv
        
        current_price_data = current_prices.get(symbol, {})
        current_price = current_price_data.get('price_try', purchase_price)
        
        current_value = quantity * current_price
        profit_loss = current_value - amount
        profit_loss_percent = (profit_loss / amount * 100) if amount > 0 else 0
        
        portfolio.append({
            'id': inv_id,
            'name': name,
            'symbol': symbol,
            'icon': icon,
            'type': inv_type,
            'quantity': quantity,
            'purchase_price': purchase_price,
            'purchase_date': purchase_date,
            'purchase_amount': amount,
            'current_price': current_price,
            'current_value': current_value,
            'profit_loss': profit_loss,
            'profit_loss_percent': profit_loss_percent,
            'description': description
        })
        
        total_investment += amount
        total_current_value += current_value
    
    total_profit_loss = total_current_value - total_investment
    total_profit_loss_percent = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
    
    return {
        'investments': portfolio,
        'total_investment': total_investment,
        'total_current_value': total_current_value,
        'total_profit_loss': total_profit_loss,
        'total_profit_loss_percent': total_profit_loss_percent
    }

# Finansal hedef yönetimi fonksiyonları
def get_goal_templates():
    """Hedef şablonlarını getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, category, icon, description FROM goal_templates WHERE is_active = 1')
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Hedef şablonları alınırken hata: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def add_financial_goal(title, goal_type, target_amount, target_date, description=''):
    """Yeni finansal hedef ekle"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Hedef tarihine kadar kalan ay sayısını hesapla
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        today = datetime.now().date()
        months_remaining = ((target_date_obj.year - today.year) * 12 + 
                          (target_date_obj.month - today.month))
        
        # Aylık hedef hesapla
        monthly_target = target_amount / max(1, months_remaining) if months_remaining > 0 else target_amount
        
        cursor.execute('''
            INSERT INTO financial_goals (user_id, title, goal_type, target_amount, target_date, monthly_target, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (1, title, goal_type, target_amount, target_date, monthly_target, description))  # user_id=1 for demo
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Hedef eklenirken hata: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_user_goals():
    """Kullanıcının hedeflerini getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, goal_type, target_amount, current_amount, target_date, 
                   monthly_target, description, created_at
            FROM financial_goals
            WHERE user_id = 1 AND is_active = 1
            ORDER BY target_date ASC
        ''')
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Hedefler alınırken hata: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def add_goal_contribution(goal_id, amount, contribution_date, description=''):
    """Hedefe katkı ekle"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Katkı ekle
        cursor.execute('''
            INSERT INTO goal_contributions (goal_id, amount, contribution_date, description)
            VALUES (?, ?, ?, ?)
        ''', (goal_id, amount, contribution_date, description))
        
        # Hedefin current_amount'ını güncelle
        cursor.execute('''
            UPDATE financial_goals 
            SET current_amount = current_amount + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (amount, goal_id))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Katkı eklenirken hata: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def calculate_goal_analytics(goal):
    """Hedef analitiklerini hesapla"""
    goal_id, title, goal_type, target_amount, current_amount, target_date, monthly_target, description, created_at = goal
    
    # Tarih hesaplamaları
    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    created_date_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').date()
    today = datetime.now().date()
    
    # Zaman hesaplamaları
    total_days = (target_date_obj - created_date_obj).days
    elapsed_days = (today - created_date_obj).days
    remaining_days = (target_date_obj - today).days
    
    # İlerleme hesaplamaları
    progress_percent = (current_amount / target_amount * 100) if target_amount > 0 else 0
    time_progress_percent = (elapsed_days / total_days * 100) if total_days > 0 else 0
    
    # Gereken aylık tasarruf (kalan süreye göre)
    remaining_months = max(1, remaining_days / 30)
    required_monthly = (target_amount - current_amount) / remaining_months
    
    # Durum değerlendirmesi
    if remaining_days <= 0:
        status = "expired"
    elif progress_percent >= 100:
        status = "completed"
    elif progress_percent >= time_progress_percent:
        status = "on_track"
    elif progress_percent >= time_progress_percent * 0.8:
        status = "slightly_behind"
    else:
        status = "behind"
    
    return {
        'goal_id': goal_id,
        'title': title,
        'goal_type': goal_type,
        'target_amount': target_amount,
        'current_amount': current_amount,
        'target_date': target_date_obj,
        'monthly_target': monthly_target,
        'description': description,
        'progress_percent': progress_percent,
        'time_progress_percent': time_progress_percent,
        'remaining_days': remaining_days,
        'remaining_months': remaining_months,
        'required_monthly': required_monthly,
        'status': status
    }

def get_expenses(limit=None):
    """Harcamaları getir"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        query = '''
            SELECT e.amount, e.original_amount, e.currency, e.exchange_rate, 
                   e.description, c.name as category_name, e.date, c.color, e.created_at
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            ORDER BY e.created_at DESC, e.date DESC, e.id DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        expenses = cursor.fetchall()
        return expenses
    except Exception as e:
        st.error(f"Harcama getirme hatası: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_real_data():
    """Gerçek veritabanından veri getir"""
    expenses = get_expenses()
    data = []
    
    for row in expenses:
        try:
            # Yeni format: amount, original_amount, currency, exchange_rate, description, category_name, date, color, created_at
            if len(row) >= 9:
                amount, original_amount, currency, exchange_rate, description, category_name, date_str, color, created_at = row
                
                # NULL değerleri düzelt
                original_amount = original_amount if original_amount is not None else amount
                currency = currency if currency is not None else 'TRY'
                exchange_rate = exchange_rate if exchange_rate is not None else 1.0
                
            elif len(row) >= 8:
                amount, original_amount, currency, exchange_rate, description, category_name, date_str, color = row
                created_at = None
                
                # NULL değerleri düzelt
                original_amount = original_amount if original_amount is not None else amount
                currency = currency if currency is not None else 'TRY'
                exchange_rate = exchange_rate if exchange_rate is not None else 1.0
                
            else:
                # Eski format için uyumluluk
                amount, description, category_name, date_str, color = row
                original_amount = amount
                currency = 'TRY'
                exchange_rate = 1.0
                created_at = None
            
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                date_obj = datetime.now()
                
            try:
                if created_at:
                    created_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                else:
                    created_obj = date_obj
            except:
                created_obj = date_obj
            
            data.append({
                'date': date_obj,
                'created_at': created_obj,
                'amount': float(amount),  # TL cinsinden
                'original_amount': float(original_amount),
                'currency': str(currency),
                'exchange_rate': float(exchange_rate),
                'category_name': category_name.lower(),
                'description': description or 'Açıklama yok'
            })
            
        except Exception as e:
            print(f"Veri işleme hatası: {e}, Row: {row}")
            continue
    
    return data

@st.cache_data
def create_demo_data():
    """Demo veri oluştur (gerçek veri yoksa)"""
    random.seed(42)
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()
    current_date = start_date
    
    categories = ['yemek', 'ulasim', 'eglence', 'saglik', 'alisveris', 'faturalar']
    data = []
    
    while current_date <= end_date:
        num_expenses = random.randint(1, 4)
        for _ in range(num_expenses):
            category = random.choice(categories)
            
            if category == 'yemek':
                amount = random.gauss(50, 20)
            elif category == 'ulasim':
                amount = random.gauss(30, 10)
            elif category == 'eglence':
                amount = random.gauss(100, 40)
            else:
                amount = random.gauss(80, 30)
            
            amount = max(10, amount)
            
            data.append({
                'date': current_date,
                'amount': round(amount, 2),
                'category_name': category,
                'description': f"{category.title()} harcamasi"
            })
        
        current_date += timedelta(days=1)
    
    return data

# Akıllı öneriler fonksiyonu
def analyze_spending_patterns():
    """Harcama kalıplarını analiz et ve akıllı öneriler üret"""
    try:
        conn = sqlite3.connect('data/neofinx.db', timeout=30)
        conn.execute('PRAGMA journal_mode=WAL')
        cursor = conn.cursor()
        
        # Bu ay ve geçen ayın verilerini al
        current_month = datetime.now().strftime('%Y-%m')
        last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        
        # Bu ayın harcamaları
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY c.name
        """, (current_month,))
        current_month_data = cursor.fetchall()
        
        # Geçen ayın harcamaları
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY c.name
        """, (last_month,))
        last_month_data = cursor.fetchall()
        
        # Son 7 günün harcamaları
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count,
                   AVG(e.amount) as avg_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date >= ?
            GROUP BY c.name
            ORDER BY total DESC
        """, (week_ago,))
        week_data = cursor.fetchall()
        
        # Günlük ortalama harcamalar (son 30 gün)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT DATE(e.date) as expense_date, SUM(e.amount) as daily_total
            FROM expenses e
            WHERE e.date >= ?
            GROUP BY DATE(e.date)
            ORDER BY expense_date
        """, (thirty_days_ago,))
        daily_data = cursor.fetchall()
        
        # En sık harcama yapılan kategoriler
        cursor.execute("""
            SELECT c.name, COUNT(e.id) as frequency, AVG(e.amount) as avg_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date >= ?
            GROUP BY c.name
            ORDER BY frequency DESC
            LIMIT 5
        """, (thirty_days_ago,))
        frequent_categories = cursor.fetchall()
        
        conn.close()
        
        insights = []
        
        # 1. Aylık karşılaştırma analizi
        current_dict = {item[0]: item[1] for item in current_month_data}
        last_dict = {item[0]: item[1] for item in last_month_data}
        
        for category, current_amount in current_dict.items():
            if category in last_dict:
                last_amount = last_dict[category]
                if last_amount > 0:
                    change_percent = ((current_amount - last_amount) / last_amount) * 100
                    
                    if change_percent > 20:
                        insights.append({
                            'type': 'warning',
                            'icon': '📈',
                            'title': f'{category.title()} Harcaması Arttı',
                            'message': f'Bu ay {category} harcamanız geçen aya göre %{change_percent:.0f} arttı ({current_amount:,.0f} TL)',
                            'suggestion': f'{category} harcamalarınızı gözden geçirin ve gereksiz harcamaları belirleyin.',
                            'priority': 'high' if change_percent > 50 else 'medium'
                        })
                    elif change_percent < -15:
                        insights.append({
                            'type': 'success',
                            'icon': '💰',
                            'title': f'{category.title()} Tasarrufu',
                            'message': f'Bu ay {category} kategorisinde {abs(current_amount - last_amount):,.0f} TL tasarruf ettiniz!',
                            'suggestion': f'Harika! {category} harcamalarınızı kontrol altında tutmaya devam edin.',
                            'priority': 'low'
                        })
        
        # 2. Haftalık trend analizi
        if week_data:
            top_weekly_category = week_data[0]
            if top_weekly_category[1] > 500:  # Test için 500 TL'ye düşürdüm
                insights.append({
                    'type': 'info',
                    'icon': '🎯',
                    'title': 'Haftalık En Yüksek Harcama',
                    'message': f'Son 7 günde en çok {top_weekly_category[0]} kategorisinde harcama yaptınız ({top_weekly_category[1]:,.0f} TL)',
                    'suggestion': f'Ortalama işlem tutarınız {top_weekly_category[3]:,.0f} TL. Daha küçük tutarlarda alışveriş yapmayı düşünün.',
                    'priority': 'medium'
                })
        
        # 3. Günlük harcama pattern analizi
        if daily_data and len(daily_data) >= 7:
            daily_amounts = [item[1] for item in daily_data]
            avg_daily = sum(daily_amounts) / len(daily_amounts)
            recent_week_avg = sum(daily_amounts[-7:]) / 7
            
            if recent_week_avg > avg_daily * 1.3:
                insights.append({
                    'type': 'warning',
                    'icon': '⚠️',
                    'title': 'Günlük Harcama Artışı',
                    'message': f'Son 7 günlük ortalama harcamanız ({recent_week_avg:,.0f} TL) aylık ortalamanızdan %{((recent_week_avg/avg_daily)-1)*100:.0f} yüksek',
                    'suggestion': 'Günlük harcamalarınızı kontrol altına almak için bütçe limiti belirleyin.',
                    'priority': 'high'
                })
            elif recent_week_avg < avg_daily * 0.8:
                insights.append({
                    'type': 'success',
                    'icon': '🎉',
                    'title': 'Başarılı Tasarruf',
                    'message': f'Son hafta günlük ortalama {avg_daily - recent_week_avg:,.0f} TL daha az harcadınız!',
                    'suggestion': 'Bu tasarruf alışkanlığınızı sürdürmeye devam edin.',
                    'priority': 'low'
                })
        
        # 4. Sık harcama kategorileri analizi
        if frequent_categories:
            most_frequent = frequent_categories[0]
            if most_frequent[1] > 10:  # 10'dan fazla işlem
                insights.append({
                    'type': 'info',
                    'icon': '🔄',
                    'title': 'En Sık Harcama Kategorisi',
                    'message': f'{most_frequent[0]} kategorisinde son 30 günde {most_frequent[1]} işlem yaptınız',
                    'suggestion': f'Ortalama işlem tutarınız {most_frequent[2]:,.0f} TL. Daha az sıklıkta, daha planlı alışveriş yapabilirsiniz.',
                    'priority': 'low'
                })
        
        # 5. Genel bütçe önerileri
        if current_month_data:
            total_current = sum(item[1] for item in current_month_data)
            if total_current > 1000:  # Test için 1000 TL'ye düşürdüm
                insights.append({
                    'type': 'info',
                    'icon': '📊',
                    'title': 'Aylık Harcama Özeti',
                    'message': f'Bu ay toplam {total_current:,.0f} TL harcama yaptınız',
                    'suggestion': 'Ayın geri kalanı için günlük bütçe planlayarak harcamalarınızı optimize edebilirsiniz.',
                    'priority': 'medium'
                })
        
        # Önceliklere göre sırala
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        insights.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return insights[:8]  # En fazla 8 öneri göster
        
    except Exception as e:
        return []  # Hata durumunda boş liste döndür


# Chatbot Fonksiyonları
def get_user_spending_summary():
    """Kullanıcının harcama özetini getir"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Bu ayki toplam harcama
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = ?", (current_month,))
        this_month_total = cursor.fetchone()[0] or 0
        
        # En çok harcama yapılan kategori
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY c.name
            ORDER BY total DESC
            LIMIT 1
        """, (current_month,))
        top_category = cursor.fetchone()
        
        # Toplam harcama sayısı
        cursor.execute("SELECT COUNT(*) FROM expenses")
        total_expenses = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'this_month_total': this_month_total,
            'top_category': top_category,
            'total_expenses': total_expenses
        }
    except:
        return None


def generate_chatbot_response(user_input, user_data=None):
    """OpenAI ChatGPT ile güçlendirilmiş chatbot yanıtları"""
    
    # OpenAI API key'i kontrol et
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Kullanıcı verisini context olarak hazırla
    context = ""
    if user_data:
        context = f"""
Kullanıcı finansal bilgileri:
- Bu ay toplam harcama: {user_data['this_month_total']:,.0f} ₺
- Toplam harcama kaydı: {user_data['total_expenses']} adet
- En çok harcama yapılan kategori: {user_data['top_category'][0] if user_data['top_category'] else 'Henüz analiz edilecek veri yok'}
"""
    
    # OpenAI API mevcut ve key varsa gerçek ChatGPT kullan
    if api_key and api_key != 'your_new_api_key_here':
        try:
            # OpenAI client'ı oluştur
            client = openai.OpenAI(api_key=api_key)
            
            # System message (NeoFinX asistanı rolü)
            system_message = f"""Sen NeoFinX akıllı finansal asistanısın. Türkçe konuşuyorsun ve kullanıcılara finansal konularda yardımcı oluyorsun.

NeoFinX özellikleri:
- Çoklu para birimi desteği (TL, USD, EUR, GBP, vb.)
- AI destekli harcama tahmini
- Anormal harcama tespiti
- PDF raporlama
- Trend analizi ve grafik görselleştirmeler
- Kategori bazlı harcama takibi (Yemek, Ulaşım, Eğlence, Sağlık, Alışveriş, Faturalar, Diğer)

{context}

Yanıtlarında:
- Kısa ve anlaşılır ol (maksimum 200 kelime)
- Emoji kullan
- Pratik öneriler ver
- Kullanıcının mevcut verilerini referans al
- Finansal terminolojiyi basit açıkla"""

            # ChatGPT'ye istek gönder
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=300,
                temperature=0.7,
                timeout=10  # 10 saniye timeout
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # OpenAI API hatası durumunda fallback kullan
            st.error(f"ChatGPT API hatası: {str(e)}")
            return generate_fallback_response(user_input, user_data)
    
    else:
        # API key yoksa fallback kullan
        return generate_fallback_response(user_input, user_data)

def generate_fallback_response(user_input, user_data=None):
    """Fallback chatbot yanıtları (OpenAI API olmadığında)"""
    user_input = user_input.lower().strip()
    
    # Finansal olmayan sorular için uyarı
    non_financial_keywords = ['yaş', 'isim', 'kim', 'nerede', 'nasıl', 'hava', 'spor', 'müzik', 'film', 'oyun']
    if any(keyword in user_input for keyword in non_financial_keywords):
        # Eğer soru finansal değilse
        if not any(fin_word in user_input for fin_word in ['para', 'harcama', 'bütçe', 'tasarruf', 'kategori', 'NeoFinX']):
            return "🤖 Ben sadece finansal konularda yardımcı olabilen NeoFinX AI asistanıyım. Size harcama analizi, bütçe önerileri veya tasarruf ipuçları konularında yardımcı olabilirim. Finansal bir soru sormak ister misiniz?"
    
    # Temel yanıt şablonları
    responses = {
        # Selamlama
        'merhaba': "🤖 Merhaba! Ben NeoFinX AI asistanınızım. Size finansal konularda yardımcı olabilirim. Nasıl yardımcı olabilirim?",
        'selam': "🤖 Selam! NeoFinX'a hoş geldiniz. Hangi konuda yardıma ihtiyacınız var?",
        'hello': "🤖 Hello! I'm your NeoFinX AI assistant. How can I help you with your finances?",
        
        # Harcama sorguları
        'harcama': "💰 Harcama verilerinizi analiz ediyorum...",
        
        'bütçe': "📊 Bütçe planlaması için 50/30/20 kuralını öneriyorum: Gelirinizin %50'si ihtiyaçlar, %30'u istekler, %20'si tasarruf için ayırın.",
        'budget': "📊 For budgeting, I recommend the 50/30/20 rule: 50% for needs, 30% for wants, 20% for savings.",
        
        # Tasarruf tavsiyeleri
        'tasarruf': "💡 Tasarruf ipuçları:\n• Günlük harcamalarınızı takip edin\n• Gereksiz aboneliklerinizi iptal edin\n• Market alışverişinden önce liste yapın\n• Yemek dışında yemek yerine evde pişirin",
        'saving': "💡 Saving tips:\n• Track your daily expenses\n• Cancel unnecessary subscriptions\n• Make a grocery list before shopping\n• Cook at home instead of eating out",
        
        # Kategoriler
        'kategori': "📁 NeoFinX'da şu kategoriler var: Yemek, Ulaşım, Eğlence, Sağlık, Alışveriş, Faturalar, Diğer. Hangi kategori hakkında bilgi almak istiyorsunuz?",
        
        # Raporlar
        'rapor': "📄 PDF raporlarınızı 'PDF Rapor' sayfasından oluşturabilirsiniz. Aylık harcama analizlerinizi indirip saklayabilirsiniz.",
        
        # Yardım
        'yardım': "🆘 Size şu konularda yardımcı olabilirim:\n• Harcama analizi\n• Bütçe önerileri\n• Tasarruf ipuçları\n• NeoFinX özelliklerini öğrenme\n\nSadece sorunuzu yazın!",
        'help': "🆘 I can help you with:\n• Expense analysis\n• Budget recommendations\n• Saving tips\n• Learning NeoFinX features\n\nJust type your question!",
        
        # Özellikler
        'özellik': "🌟 NeoFinX özellikleri:\n• Çoklu para birimi desteği\n• AI destekli harcama tahmini\n• Anormal harcama tespiti\n• PDF raporlama\n• Trend analizi",
        
        # Teşekkür
        'teşekkür': "😊 Rica ederim! Başka sorunuz varsa çekinmeden sorun.",
        'teşekkürler': "😊 Rica ederim! Size yardımcı olabildiysem ne mutlu bana.",
        'thanks': "😊 You're welcome! Feel free to ask if you have more questions.",
    }
    
    # Akıllı eşleştirme
    for key, response in responses.items():
        if key in user_input:
            # Harcama sorusu için özel mantık
            if key == 'harcama' and user_data:
                category_info = f"En çok {user_data['top_category'][0]} kategorisinde harcama yapıyorsunuz." if user_data['top_category'] else "Henüz kategori analizi yapılabilecek veri yok."
                return f"💰 Bu ay toplam {user_data['this_month_total']:,.0f} ₺ harcamanız var. {category_info}"
            elif key == 'harcama' and not user_data:
                return "💰 Harcamalarınızı görmek için lütfen önce bazı harcama kayıtları ekleyin."
            return response
    
    # Sayısal sorguları tespit et (sadece finansal bağlamda)
    if any(word in user_input for word in ['kaç', 'ne kadar', 'toplam', 'how much', 'total']):
        # Finansal kelimeler var mı kontrol et
        if any(fin_word in user_input for fin_word in ['para', 'harcama', 'lira', 'tl', '₺', 'money', 'expense']):
            if user_data:
                return f"📊 İstatistikleriniz:\n• Bu ay: {user_data['this_month_total']:,.0f} ₺\n• Toplam kayıt: {user_data['total_expenses']} adet\n• En çok harcama: {user_data['top_category'][0] if user_data['top_category'] else 'Veri yok'}"
            else:
                return "📊 Henüz harcama kaydınız bulunmuyor. Lütfen önce birkaç harcama ekleyin."
    
    # Varsayılan yanıt
    return "🤖 Ben finansal konularda uzman bir asistanım. Size şu konularda yardımcı olabilirim:\n• 💰 Harcama analizi\n• 📊 Bütçe tavsiyeleri\n• 💡 Tasarruf ipuçları\n• 📈 Finansal planlama\n\nFinansal bir soru sormak ister misiniz?"


def get_spending_recommendations():
    """Harcama önerileri ve ipuçları"""
    recommendations = [
        {
            'icon': '🎯',
            'title': 'Bütçe Hedefi Belirleyin',
            'description': 'Her kategori için aylık bütçe limiti belirleyerek harcamalarınızı kontrol altında tutun.',
            'action': 'Bütçe Planlama sayfasından kategori limitlerini ayarlayın.'
        },
        {
            'icon': '📱',
            'title': 'Düzenli Takip',
            'description': 'Harcamalarınızı günlük olarak kaydetme alışkanlığı edinin.',
            'action': 'Her gün en az bir kez uygulamayı kontrol edin.'
        },
        {
            'icon': '💡',
            'title': 'Analiz Yapın',
            'description': 'Haftalık ve aylık harcama trendlerinizi düzenli olarak inceleyin.',
            'action': 'Harcama Analizi sayfasından raporlarınızı gözden geçirin.'
        },
        {
            'icon': '🛒',
            'title': 'Planlı Alışveriş',
            'description': 'Alışveriş öncesi liste hazırlayarak gereksiz harcamaları önleyin.',
            'action': 'Büyük harcamalar öncesi bütçenizi kontrol edin.'
        },
        {
            'icon': '📈',
            'title': 'Trend Takibi',
            'description': 'Aylık harcama artış/azalışlarınızı takip ederek finansal hedefinize odaklanın.',
            'action': 'Ana sayfadaki trend grafiklerini düzenli inceleyin.'
        }
    ]
    return recommendations

# PDF Rapor Fonksiyonları
def generate_monthly_pdf_report(month_year):
    """Aylık PDF raporu oluştur"""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.fonts import addMapping
        
        # UTF-8 desteği için font kaydetme
        try:
            # Windows'ta mevcut olan Arial fontunu kullan
            pdfmetrics.registerFont(TTFont('Arial-Unicode', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Unicode-Bold', 'arialbd.ttf'))
            addMapping('Arial-Unicode', 0, 0, 'Arial-Unicode')
            addMapping('Arial-Unicode', 1, 0, 'Arial-Unicode-Bold')
            font_name = 'Arial-Unicode'
        except:
            # Arial bulunamazsa DejaVu fontunu dene
            try:
                pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'DejaVuSans-Bold.ttf'))
                addMapping('DejaVu', 0, 0, 'DejaVu')
                addMapping('DejaVu', 1, 0, 'DejaVu-Bold')
                font_name = 'DejaVu'
            except:
                # Hiçbiri yoksa varsayılan Helvetica kullan
                font_name = 'Helvetica'
        
        # Seçilen ay için veri al
        conn = sqlite3.connect('data/neofinx.db', timeout=30)
        cursor = conn.cursor()
        
        # Aylık harcamalar
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count,
                   AVG(e.amount) as avg_amount, MAX(e.amount) as max_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY c.name
            ORDER BY total DESC
        """, (month_year,))
        category_data = cursor.fetchall()
        
        # Günlük harcamalar
        cursor.execute("""
            SELECT DATE(e.date) as expense_date, SUM(e.amount) as daily_total
            FROM expenses e
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY DATE(e.date)
            ORDER BY expense_date
        """, (month_year,))
        daily_data = cursor.fetchall()
        
        conn.close()
        
        # PDF oluştur
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Türkçe karakterler için font ayarları
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=20,
            spaceAfter=30,
            textColor=colors.HexColor('#667eea'),
            encoding='utf-8'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#333333'),
            encoding='utf-8'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            encoding='utf-8'
        )
        
        # Emojileri kaldırarak sadece metin kullan
        story.append(Paragraph("NeoFinX Aylik Harcama Raporu", title_style))
        story.append(Paragraph(f"Rapor Donemi: {month_year}", heading_style))
        story.append(Spacer(1, 20))
        
        # Özet bilgiler
        if category_data:
            total_spending = sum(item[1] for item in category_data)
            total_transactions = sum(item[2] for item in category_data)
            
            summary_data = [
                ['Toplam Harcama', f'{total_spending:,.2f} TL'],
                ['Toplam Islem', f'{total_transactions} adet'],
                ['Ortalama Islem', f'{total_spending/total_transactions:,.2f} TL' if total_transactions > 0 else '0 TL'],
                ['Aktif Gun Sayisi', f'{len(daily_data)} gun']
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), font_name)
            ]))
            
            story.append(Paragraph("Aylik Ozet", heading_style))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Kategori bazlı analiz
            story.append(Paragraph("Kategori Bazli Analiz", heading_style))
            
            category_table_data = [['Kategori', 'Toplam Tutar', 'Islem Sayisi', 'Ortalama', 'En Yuksek']]
            for item in category_data:
                category_table_data.append([
                    item[0].title(),
                    f'{item[1]:,.2f} TL',
                    f'{item[2]} adet',
                    f'{item[3]:,.2f} TL',
                    f'{item[4]:,.2f} TL'
                ])
            
            category_table = Table(category_table_data)
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), font_name)
            ]))
            
            story.append(category_table)
            
        else:
            story.append(Paragraph("Bu ay icin harcama kaydi bulunamadi.", normal_style))
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("NeoFinX - Akilli Butce Asistani", normal_style))
        story.append(Paragraph(f"Rapor Olusturma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        return None

# Harcama Tahmini Fonksiyonları
def predict_next_month_spending():
    """Gelecek ay harcama tahmini"""
    try:
        conn = sqlite3.connect('data/neofinx.db', timeout=30)
        cursor = conn.cursor()
        
        # Son 6 ayın verilerini al
        months_data = []
        for i in range(6):
            target_date = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_str = target_date.strftime('%Y-%m')
            
            cursor.execute("""
                SELECT c.name, SUM(e.amount) as total
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE strftime('%Y-%m', e.date) = ?
                GROUP BY c.name
            """, (month_str,))
            
            month_expenses = cursor.fetchall()
            total_month = sum(item[1] for item in month_expenses)
            months_data.append({
                'month': month_str,
                'total': total_month,
                'categories': dict(month_expenses)
            })
        
        conn.close()
        
        predictions = {}
        
        # Genel trend analizi
        monthly_totals = [month['total'] for month in months_data if month['total'] > 0]
        if len(monthly_totals) >= 3:
            # Basit linear trend
            trend = calculate_trend(monthly_totals)
            next_month_total = monthly_totals[0] + trend
            predictions['total'] = max(0, next_month_total)
            
            # Kategori bazlı tahmin
            all_categories = set()
            for month in months_data:
                all_categories.update(month['categories'].keys())
            
            category_predictions = {}
            for category in all_categories:
                category_amounts = []
                for month in months_data:
                    if category in month['categories']:
                        category_amounts.append(month['categories'][category])
                    else:
                        category_amounts.append(0)
                
                if len(category_amounts) >= 3:
                    cat_trend = calculate_trend(category_amounts)
                    next_cat_amount = category_amounts[0] + cat_trend
                    category_predictions[category] = max(0, next_cat_amount)
            
            predictions['categories'] = category_predictions
            
            # Sezonsal pattern analizi
            seasonal_factor = analyze_seasonal_pattern(months_data)
            predictions['seasonal_adjustment'] = seasonal_factor
            
            # Güven aralığı hesaplama
            if len(monthly_totals) > 1:
                variance = statistics.variance(monthly_totals)
                std_dev = math.sqrt(variance)
                predictions['confidence_range'] = {
                    'lower': max(0, predictions['total'] - std_dev),
                    'upper': predictions['total'] + std_dev
                }
        
        return predictions
        
    except Exception as e:
        return {}

def calculate_trend(values):
    """Basit linear trend hesaplama"""
    if len(values) < 2:
        return 0
    
    n = len(values)
    x_values = list(range(n))
    
    # Linear regression coefficients
    x_mean = sum(x_values) / n
    y_mean = sum(values) / n
    
    numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0
    
    slope = numerator / denominator
    return slope

def analyze_seasonal_pattern(months_data):
    """Sezonsal pattern analizi"""
    try:
        current_month = datetime.now().month
        
        # Aynı ay verilerini bul (geçen yıl vs)
        same_month_amounts = []
        for month_data in months_data:
            month_date = datetime.strptime(month_data['month'], '%Y-%m')
            if month_date.month == current_month and month_data['total'] > 0:
                same_month_amounts.append(month_data['total'])
        
        if len(same_month_amounts) >= 2:
            # Sezonsal ortalama
            seasonal_avg = sum(same_month_amounts) / len(same_month_amounts)
            
            # Genel ortalama
            all_amounts = [m['total'] for m in months_data if m['total'] > 0]
            general_avg = sum(all_amounts) / len(all_amounts) if all_amounts else 0
            
            if general_avg > 0:
                return seasonal_avg / general_avg
        
        return 1.0  # Nötr faktör
        
    except:
        return 1.0

# Anormal Harcama Tespiti Fonksiyonları
def detect_anomalous_expenses():
    """Anormal harcamaları tespit et"""
    try:
        conn = sqlite3.connect('data/neofinx.db', timeout=30)
        cursor = conn.cursor()
        
        # Son 90 günün harcamalarını al
        ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT e.amount, e.description, c.name, e.date, e.created_at
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.date >= ?
            ORDER BY e.amount DESC
        """, (ninety_days_ago,))
        
        all_expenses = cursor.fetchall()
        conn.close()
        
        if len(all_expenses) < 10:
            return {'anomalies': [], 'stats': {}}
        
        amounts = [exp[0] for exp in all_expenses]
        
        # İstatistiksel analiz
        mean_amount = statistics.mean(amounts)
        median_amount = statistics.median(amounts)
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        # Z-score ile anomali tespiti
        anomalies = []
        z_threshold = 2.5  # 2.5 sigma üzeri anormal kabul
        
        for expense in all_expenses:
            amount, description, category, date, created_at = expense
            
            if std_dev > 0:
                z_score = abs((amount - mean_amount) / std_dev)
                
                if z_score > z_threshold:
                    anomaly_type = determine_anomaly_type(amount, mean_amount, median_amount)
                    
                    anomalies.append({
                        'amount': amount,
                        'description': description,
                        'category': category,
                        'date': date,
                        'created_at': created_at,
                        'z_score': z_score,
                        'type': anomaly_type,
                        'deviation_percent': ((amount - mean_amount) / mean_amount) * 100
                    })
        
        # Kategori bazlı anomali analizi
        category_anomalies = analyze_category_anomalies(all_expenses)
        
        # Zaman bazlı pattern analizi
        time_anomalies = analyze_time_patterns(all_expenses)
        
        stats = {
            'total_expenses': len(all_expenses),
            'mean_amount': mean_amount,
            'median_amount': median_amount,
            'std_dev': std_dev,
            'anomaly_count': len(anomalies),
            'anomaly_percentage': (len(anomalies) / len(all_expenses)) * 100
        }
        
        return {
            'anomalies': sorted(anomalies, key=lambda x: x['z_score'], reverse=True)[:10],
            'category_anomalies': category_anomalies,
            'time_anomalies': time_anomalies,
            'stats': stats
        }
        
    except Exception as e:
        return {'anomalies': [], 'stats': {}}

def determine_anomaly_type(amount, mean_amount, median_amount):
    """Anomali tipini belirle"""
    if amount > mean_amount * 3:
        return "🚨 Kritik Yüksek"
    elif amount > mean_amount * 2:
        return "⚠️ Yüksek"
    elif amount > mean_amount * 1.5:
        return "📈 Ortalamanın Üzeri"
    else:
        return "🔍 Şüpheli Pattern"

def analyze_category_anomalies(expenses):
    """Kategori bazlı anomali analizi"""
    category_stats = {}
    
    # Kategori bazlı istatistikler
    for amount, description, category, date, created_at in expenses:
        if category not in category_stats:
            category_stats[category] = []
        category_stats[category].append(amount)
    
    category_anomalies = []
    
    for category, amounts in category_stats.items():
        if len(amounts) >= 5:  # En az 5 veri noktası
            mean_cat = statistics.mean(amounts)
            std_cat = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            if std_cat > 0:
                for expense in expenses:
                    if expense[2] == category:  # category match
                        amount = expense[0]
                        z_score = abs((amount - mean_cat) / std_cat)
                        
                        if z_score > 2.0:  # Kategori içinde anomali
                            category_anomalies.append({
                                'category': category,
                                'amount': amount,
                                'description': expense[1],
                                'date': expense[3],
                                'z_score': z_score,
                                'category_mean': mean_cat
                            })
    
    return sorted(category_anomalies, key=lambda x: x['z_score'], reverse=True)[:5]

def analyze_time_patterns(expenses):
    """Zaman bazlı pattern analizi"""
    time_anomalies = []
    
    # Hafta içi vs hafta sonu analizi
    weekday_amounts = []
    weekend_amounts = []
    
    for expense in expenses:
        try:
            date_obj = datetime.strptime(expense[3], '%Y-%m-%d')
            weekday = date_obj.weekday()
            
            if weekday < 5:  # Hafta içi (0-4)
                weekday_amounts.append(expense[0])
            else:  # Hafta sonu (5-6)
                weekend_amounts.append(expense[0])
        except:
            continue
    
    # Pattern analizleri
    if len(weekday_amounts) > 5 and len(weekend_amounts) > 2:
        weekday_avg = statistics.mean(weekday_amounts)
        weekend_avg = statistics.mean(weekend_amounts)
        
        if weekend_avg > weekday_avg * 1.5:
            time_anomalies.append({
                'type': 'weekend_spike',
                'message': f'Hafta sonu harcamalarınız hafta içinin {weekend_avg/weekday_avg:.1f} katı',
                'weekday_avg': weekday_avg,
                'weekend_avg': weekend_avg
            })
    
    return time_anomalies

# Veritabanını başlat
init_database()

# Modern ana başlık 
st.markdown("""
<div class="main-header">
    <h1>🏦 NeoFinX</h1>
    <p>Yapay Zeka Destekli Akıllı Bütçe ve Harcama Asistanı</p>
</div>
""", unsafe_allow_html=True)

# Sidebar menu
st.sidebar.title("📋 Menu")
page = st.sidebar.selectbox(
    "Sayfa Secin:",
    ["🏠 Ana Sayfa", "➕ Harcama Ekle", "📤 CSV Import", "📊 Harcama Analizi", "🎭 Kişilik Profili", "📈 Butce Planlama", "💰 Yatırım Takibi", "🎯 Akıllı Hedefler", "📋 Vergi Hesaplamaları", "📄 PDF Rapor", "🔮 Harcama Tahmini", "⚠️ Anormal Harcama Tespiti", "🤖 AI Asistan"]
)

# Veri kaynağı seçimi
data_source = st.sidebar.radio(
    "Veri Kaynagi:",
    ["📊 Gerçek Veriler", "🎭 Demo Veriler"]
)

# Güncel kur bilgileri
st.sidebar.markdown("---")
st.sidebar.markdown("### 💱 Güncel Kurlar")

# Kurları getir ve göster
try:
    exchange_rates = get_exchange_rates()
    
    # Popüler kurları göster
    popular_currencies = ['USD', 'EUR', 'GBP']
    
    for currency in popular_currencies:
        if currency in exchange_rates:
            rate = exchange_rates[currency]
            currency_symbols = {'USD': '🇺🇸 $', 'EUR': '🇪🇺 €', 'GBP': '🇬🇧 £'}
            symbol = currency_symbols.get(currency, currency)
            
            st.sidebar.metric(
                label=f"{symbol}",
                value=f"{rate:.4f} ₺",
                help=f"1 {currency} = {rate:.4f} TRY"
            )
    
    # Küçük yazı ile son güncelleme
    st.sidebar.caption("🕐 Kurlar saatlik güncellenir")
    
except Exception as e:
    st.sidebar.error("❌ Kur bilgileri alınamadı")

# Geliştirici bilgileri - Sidebar'da modern card
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 12px;
    border-radius: 10px;
    margin: 10px 0;
    text-align: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
">
    <div style="color: white; font-size: 13px; font-weight: 600; margin-bottom: 8px;">
        👨‍💻 Proje Geliştiricileri
    </div>
    <div style="color: rgba(255, 255, 255, 0.9); font-size: 12px; line-height: 1.4;">
        <div style="margin-bottom: 3px;">🎯 Erkan Tan</div>
        <div>🎯 Raziyegül Kahraman</div>
    </div>
</div>
""", unsafe_allow_html=True)

def import_csv_data(uploaded_file):
    """CSV dosyasından veri import et"""
    try:
        # CSV içeriğini oku
        content = uploaded_file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        imported_count = 0
        categories = get_categories()
        category_map = {cat[1].lower(): cat[0] for cat in categories}
        
        # Kategori eşleştirme haritası
        category_mapping = {
            'yemek & içecek': 'yemek',
            'yemek': 'yemek',
            'ulaşım': 'ulaşım',
            'ulasim': 'ulaşım',
            'eğlence': 'eğlence',
            'eglence': 'eğlence',
            'sağlık': 'sağlık',
            'saglik': 'sağlık',
            'alışveriş': 'alışveriş',
            'alisveris': 'alışveriş',
            'faturalar': 'faturalar',
            'eğitim': 'eğlence',  # Eğitim -> Eğlence
            'egitim': 'eğlence',
            'spor': 'eğlence',    # Spor -> Eğlence
            'kişisel bakım': 'alışveriş',  # Kişisel Bakım -> Alışveriş
            'kisisel bakim': 'alışveriş',
            'diğer': 'diğer',
            'diger': 'diğer'
        }
        
        # İlk satır başlık mı kontrol et
        header = lines[0].lower()
        start_line = 1 if 'date' in header or 'tarih' in header else 0
        
        for line in lines[start_line:]:
            parts = line.split(',')
            if len(parts) >= 3:
                try:
                    # Format 1: date,amount,category,description
                    # Format 2: tarih,tutar,aciklama,kategori
                    if len(parts) >= 4:
                        if 'date' in lines[0] or parts[0].count('-') == 2:
                            # Format 1: date,amount,category,description
                            date_str = parts[0].strip()
                            amount = float(parts[1].strip())
                            category_name = parts[2].strip().lower()
                            description = parts[3].strip()
                        else:
                            # Format 2: tarih,tutar,aciklama,kategori
                            date_str = parts[0].strip()
                            amount = float(parts[1].strip())
                            description = parts[2].strip()
                            category_name = parts[3].strip().lower()
                    else:
                        # Sadece 3 alan: date,amount,category
                        date_str = parts[0].strip()
                        amount = float(parts[1].strip())
                        category_name = parts[2].strip().lower()
                        description = f"{category_name.title()} harcaması"
                    
                    # Kategori eşleştir
                    mapped_category = category_mapping.get(category_name, category_name)
                    category_id = category_map.get(mapped_category, category_map.get('diğer', 1))
                    
                    # Tarihi parse et
                    try:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        try:
                            parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
                        except:
                            try:
                                parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
                            except:
                                parsed_date = datetime.now()
                    
                    add_expense(amount, description, category_id, parsed_date.strftime('%Y-%m-%d'))
                    imported_count += 1
                    
                except Exception as e:
                    st.warning(f"Satır atlandı: {line[:50]}... Hata: {str(e)}")
                    continue
        
        return imported_count
        
    except Exception as e:
        st.error(f"CSV işlenirken hata: {str(e)}")
        return 0

if page == "➕ Harcama Ekle":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">➕ Yeni Harcama Ekle</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Harcamalarınızı hızlı ve kolay bir şekilde kaydedin</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("expense_form"):
        # Form için özel stil
        st.markdown("""
        <style>
        .expense-form {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("### 💰 Finansal Bilgiler")
            
            # Para birimi seçimi ve kur gösterimi
            col_curr1, col_curr2 = st.columns([1, 1])
            
            with col_curr1:
                currencies = ['TRY', 'USD', 'EUR', 'GBP', 'CHF', 'CAD', 'AUD', 'JPY', 'CNY', 'RUB']
                selected_currency = st.selectbox(
                    "💱 Para Birimi",
                    currencies,
                    help="Harcama para birimini seçin"
                )
            
            with col_curr2:
                # Güncel kurları getir
                exchange_rates = get_exchange_rates()
                
                if selected_currency != 'TRY':
                    current_rate = exchange_rates.get(selected_currency, 1.0)
                    st.info(f"📊 {selected_currency}/TRY: {current_rate:.4f}")
                else:
                    st.info("🇹🇷 Türk Lirası seçildi")
            
            # Tutar girişi
            amount = st.number_input(
                f"Tutar ({selected_currency})", 
                min_value=0.01, 
                value=50.0 if selected_currency == 'TRY' else 10.0,
                step=0.01,
                help=f"Harcama tutarınızı {selected_currency} cinsinden girin"
            )
            
            # TL karşılığını göster
            if selected_currency != 'TRY':
                tl_equivalent = convert_to_try(amount, selected_currency, exchange_rates)
                st.caption(f"💰 TL Karşılığı: {tl_equivalent:,.2f} ₺")
            
            categories = get_categories()
            category_options = {cat[1]: cat[0] for cat in categories}  # name: id
            selected_category = st.selectbox(
                "📂 Kategori", 
                list(category_options.keys()),
                help="Harcamanın hangi kategoriye ait olduğunu seçin"
            )
            
        with col2:
            st.markdown("### 📝 Detay Bilgileri")
            description = st.text_input(
                "Açıklama", 
                placeholder="Örn: Akşam yemeği, Market alışverişi",
                help="Harcamanızla ilgili kısa bir açıklama yazın"
            )
            expense_date = st.date_input(
                "Tarih", 
                value=datetime.now().date(),
                help="Harcama tarihinizi seçin"
            )
        
        st.markdown("---")
        
        # Özelleştirilmiş submit butonu
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button(
                "🚀 Harcama Kaydet", 
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            if amount > 0:
                category_id = category_options[selected_category]
                
                # Kur hesaplama
                exchange_rate = exchange_rates.get(selected_currency, 1.0)
                
                success = add_expense(
                    amount=amount, 
                    description=description, 
                    category_id=category_id, 
                    date=expense_date.strftime('%Y-%m-%d'),
                    currency=selected_currency,
                    exchange_rate=exchange_rate
                )
                
                if success:
                    if selected_currency != 'TRY':
                        tl_amount = convert_to_try(amount, selected_currency, exchange_rates)
                        st.success(f"✅ {format_currency_display(amount, selected_currency)} ({tl_amount:,.2f} ₺) tutarında harcama başarıyla eklendi!")
                    else:
                        st.success(f"✅ {amount:,.2f} ₺ tutarında harcama başarıyla eklendi!")
                    
                    st.balloons()
                    # Balon efekti için kısa bir gecikme
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Harcama eklenirken bir hata oluştu!")
            else:
                st.error("❌ Lütfen geçerli bir tutar girin!")

elif page == "📤 CSV Import":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe, #00f2fe); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">📤 CSV Dosyası ile Toplu Veri İçe Aktarma</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Mevcut harcama verilerinizi toplu olarak sisteme aktarın</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mevcut sample CSV'yi import et
    st.markdown("### 🎯 Hızlı Başlangıç")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Örnek Verileri Yükle", type="primary"):
            if os.path.exists("data/sample_expenses.csv"):
                with open("data/sample_expenses.csv", 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Fake uploaded file object oluştur
                class FakeFile:
                    def __init__(self, content):
                        self.content = content.encode('utf-8')
                        self.pos = 0
                    
                    def read(self):
                        return self.content
                    
                    def seek(self, pos):
                        self.pos = pos
                
                fake_file = FakeFile(content)
                
                with st.spinner("Örnek veriler yükleniyor..."):
                    imported_count = import_csv_data(fake_file)
                
                if imported_count > 0:
                    st.success(f"✅ {imported_count} örnek harcama kaydı eklendi!")
                    st.balloons()
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Örnek veriler yüklenemedi!")
            else:
                st.error("❌ sample_expenses.csv dosyası bulunamadı!")
    
    with col2:
        # Mevcut veritabanı durumu
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM expenses')
            current_count = cursor.fetchone()[0]
            conn.close()
        except:
            current_count = 0
        
        st.info(f"""
        **📊 Mevcut Durum:**
        - Veritabanında {current_count} harcama kaydı var
        - Örnek dosyada ~400 kayıt var
        - Kategoriler: Yemek, Ulaşım, Eğlence, Sağlık, vb.
        """)
    
    st.markdown("---")
    
    st.info("""
    **📋 CSV Format Örneği:**
    ```
    tarih,tutar,aciklama,kategori
    2024-01-15,50.0,Akşam yemeği,yemek
    2024-01-16,25.0,Otobüs bileti,ulaşım
    2024-01-17,120.0,Market alışverişi,alışveriş
    ```
    
    **📌 Format Kuralları:**
    - Tarih formatı: YYYY-MM-DD veya DD.MM.YYYY
    - Tutar: Sayısal değer (nokta ile ondalık)
    - Kategori: yemek, ulaşım, eğlence, sağlık, alışveriş, faturalar, diğer
    """)
    
    # Örnek CSV dosyası oluştur
    if st.button("📋 Örnek CSV İndir"):
        sample_csv = """tarih,tutar,aciklama,kategori
2024-01-15,50.0,Akşam yemeği,yemek
2024-01-16,25.0,Otobüs bileti,ulaşım
2024-01-17,120.0,Market alışverişi,alışveriş
2024-01-18,75.0,Sinema bileti,eğlence
2024-01-19,200.0,Elektrik faturası,faturalar"""
        
        st.download_button(
            label="💾 orneg_harcamalar.csv",
            data=sample_csv,
            file_name="orneg_harcamalar.csv",
            mime="text/csv"
        )
    
    # CSV upload
    uploaded_file = st.file_uploader(
        "📁 CSV Dosyası Seçin",
        type=['csv'],
        help="Yukarıdaki formatta hazırlanmış CSV dosyasını yükleyin"
    )
    
    if uploaded_file is not None:
        st.write("📊 **Dosya Bilgileri:**")
        st.write(f"- Dosya adı: {uploaded_file.name}")
        st.write(f"- Dosya boyutu: {uploaded_file.size} bytes")
        
        # Dosya önizlemesi
        preview_content = uploaded_file.read().decode('utf-8')
        uploaded_file.seek(0)  # Reset file pointer
        
        lines = preview_content.strip().split('\n')
        st.write(f"- Toplam satır: {len(lines)}")
        st.write(f"- Veri satırı: {len(lines)-1}")
        
        st.subheader("🔍 Dosya Önizlemesi")
        preview_lines = lines[:6]  # İlk 5 satır + başlık
        for i, line in enumerate(preview_lines):
            if i == 0:
                st.write(f"**Başlık:** {line}")
            else:
                st.write(f"**{i}.** {line}")
        
        if len(lines) > 6:
            st.write(f"... ve {len(lines)-6} satır daha")
        
        # Import butonu
        if st.button("📤 Verileri İçe Aktar", type="primary"):
            with st.spinner("İçe aktarılıyor..."):
                imported_count = import_csv_data(uploaded_file)
                
            if imported_count > 0:
                st.success(f"✅ {imported_count} harcama kaydı başarıyla eklendi!")
                st.balloons()
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Hiçbir veri içe aktarılamadı. Format kontrolü yapın.")

# Veri kaynağına göre data seç
if data_source == "📊 Gerçek Veriler":
    data = get_real_data()
    if not data:
        st.sidebar.warning("⚠️ Henüz veri yok! Önce harcama ekleyin.")
        data = create_demo_data()
else:
    data = create_demo_data()

# Ana Sayfa
if page == "🏠 Ana Sayfa":
    col1, col2, col3 = st.columns(3)
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month_data = [
        item for item in data 
        if item['date'].month == current_month and item['date'].year == current_year
    ]
    
    total_spending = sum(item['amount'] for item in this_month_data)
    
    with col1:
        st.metric("💳 Bu Ay Toplam Harcama", f"{total_spending:.0f} TL")
    
    with col2:
        avg_daily = total_spending / 30 if total_spending > 0 else 0
        st.metric("📊 Gunluk Ortalama", f"{avg_daily:.0f} TL")
    
    with col3:
        expense_count = len(this_month_data)
        st.metric("📈 Bu Ay Harcama Sayısı", f"{expense_count}")
    
    # Kişilik Profili Analizi
    st.markdown("---")
    st.markdown("### 🎭 Harcama Kişiliğiniz")
    
    try:
        # Kişilik analizi yap
        analyzer = PersonalityAnalyzer()
        personality_analysis = analyzer.analyze_user_personality(days=90)
        profile = personality_analysis['profile']
        patterns = personality_analysis['patterns']
        insights = personality_analysis['insights']
        
        # Kişilik profili kartı
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {profile['color']}, {profile['color']}aa);
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px solid {profile['color']};
        ">
            <div style="color: white; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 10px;">{profile['emoji']}</div>
                <h2 style="margin: 0; font-size: 24px; font-weight: bold;">{profile['name']}</h2>
                <p style="margin: 10px 0; font-size: 16px; opacity: 0.95;">{profile['description']}</p>
                <div style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; display: inline-block; margin-top: 10px;">
                    <span style="font-weight: bold;">Güven Skoru: %{profile['confidence']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Detaylar ve öneriler
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💡 Kişiselleştirilmiş İpuçları")
            for tip in profile.get('tips', []):
                st.markdown(f"• {tip}")
        
        with col2:
            st.markdown("#### 📊 Harcama İçgörüleri")
            for insight in insights[:3]:  # İlk 3 içgörüyü göster
                st.markdown(f"**{insight['icon']} {insight['title']}**")
                st.caption(insight['description'])
        
        # Profil gelişimi
        if st.expander("📈 Kişilik Profili Gelişimi", expanded=False):
            evolution = analyzer.get_personality_evolution([30, 60, 90])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("##### 📅 Son 30 Gün")
                profile_30 = evolution.get('30_days', {})
                if profile_30:
                    st.write(f"**{profile_30['profile_name']}**")
                    st.caption(f"Güven: %{profile_30['confidence']}")
                    st.caption(f"Harcama: {profile_30['total_spending']:,.0f} ₺")
            
            with col2:
                st.markdown("##### 📅 Son 60 Gün")
                profile_60 = evolution.get('60_days', {})
                if profile_60:
                    st.write(f"**{profile_60['profile_name']}**")
                    st.caption(f"Güven: %{profile_60['confidence']}")
                    st.caption(f"Harcama: {profile_60['total_spending']:,.0f} ₺")
            
            with col3:
                st.markdown("##### 📅 Son 90 Gün")
                profile_90 = evolution.get('90_days', {})
                if profile_90:
                    st.write(f"**{profile_90['profile_name']}**")
                    st.caption(f"Güven: %{profile_90['confidence']}")
                    st.caption(f"Harcama: {profile_90['total_spending']:,.0f} ₺")
        
        # Kategori analizi
        if patterns.get('category_percentages'):
            st.markdown("#### 🎯 Harcama Dağılımı")
            
            categories = list(patterns['category_percentages'].keys())
            percentages = list(patterns['category_percentages'].values())
            
            # Donut chart oluştur
            fig_donut = go.Figure(data=[go.Pie(
                labels=[cat.title() for cat in categories],
                values=percentages,
                hole=.4,
                textinfo='label+percent',
                textposition='outside',
                marker=dict(
                    colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'],
                    line=dict(color='#FFFFFF', width=2)
                )
            )])
            
            fig_donut.update_layout(
                title="Kategori Bazlı Harcama Dağılımı (%)",
                title_x=0.5,
                font=dict(size=12),
                showlegend=True,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig_donut, use_container_width=True)
        
    except Exception as e:
        st.info(f"""
        🌟 **Kişilik Profili Henüz Hazır Değil**
        
        Harcama kişiliğinizi belirleyebilmek için daha fazla veriye ihtiyacımız var.
        
        💡 **Ne yapmalısınız:**
        • En az 5-10 harcama kaydı ekleyin
        • Farklı kategorilerde harcamalar yapın
        • Düzenli kayıt tutun
        
        📊 **Şu anda:** {expense_count} harcama kaydınız var
        """)
    
    # Veri kaynağı göstergesi
    if data_source == "📊 Gerçek Veriler":
        st.info("📊 Gerçek verileriniz gösteriliyor")
    else:
        st.warning("🎭 Demo veriler gösteriliyor - Gerçek veri için 'Harcama Ekle' sayfasını kullanın")
    
    # Son harcamalar - Dinamik güncelleme
    st.subheader("💳 Son 10 Harcama (Canlı)")
    
    # Her zaman en güncel verileri getir (cache yok)
    @st.cache_data(ttl=0)  # Cache'siz
    def get_latest_expenses():
        return get_expenses(limit=10)
    
    # Güncel verileri getir
    latest_expenses_raw = get_latest_expenses()
    
    if latest_expenses_raw:
        # Başlık satırı
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2.5, 1.5, 1.5, 1.5, 1])
        with col1:
            st.write("**📅 Tarih**")
        with col2:
            st.write("**📝 Açıklama**")
        with col3:
            st.write("**📁 Kategori**")
        with col4:
            st.write("**💱 Orijinal**")
        with col5:
            st.write("**💰 TL Karşılığı**")
        with col6:
            st.write("**🕐 Zaman**")
        
        st.markdown("---")
        
        # Son 10 harcamayı işle
        for i, row in enumerate(latest_expenses_raw[:10], 1):
            try:
                # Row parsing
                if len(row) >= 9:
                    amount, original_amount, currency, exchange_rate, description, category_name, date_str, color, created_at = row
                elif len(row) >= 8:
                    amount, original_amount, currency, exchange_rate, description, category_name, date_str, color = row
                    created_at = None
                else:
                    continue
                
                # NULL değer kontrolü
                original_amount = original_amount if original_amount is not None else amount
                currency = currency if currency is not None else 'TRY'
                description = description if description else 'Açıklama yok'
                
                # Tarih işleme
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    display_date = date_obj.strftime('%d.%m.%Y')
                except:
                    display_date = date_str
                
                # Zaman işleme
                try:
                    if created_at:
                        time_obj = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        display_time = time_obj.strftime('%H:%M')
                    else:
                        display_time = "—"
                except:
                    display_time = "—"
                
                col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2.5, 1.5, 1.5, 1.5, 1])
                
                with col1:
                    st.write(f"**{i}.** {display_date}")
                
                with col2:
                    if description and description != f"{category_name.title()} harcaması":
                        st.write(f"📋 {description[:25]}..." if len(description) > 25 else f"📋 {description}")
                    else:
                        st.write("📝 *Genel harcama*")
                
                with col3:
                    # Kategori ikonları
                    category_icons = {
                        'yemek': '🍽️',
                        'ulaşım': '🚗', 
                        'eğlence': '🎮',
                        'sağlık': '🏥',
                        'alışveriş': '🛒',
                        'faturalar': '💡',
                        'diğer': '📦'
                    }
                    icon = category_icons.get(category_name.lower(), '📦')
                    st.write(f"{icon} {category_name.title()}")
                
                with col4:
                    # Orijinal para birimi
                    if currency != 'TRY':
                        st.write(f"**{format_currency_display(original_amount, currency)}**")
                    else:
                        st.write(f"**{original_amount:.0f} ₺**")
                
                with col5:
                    # TL karşılığı ve renk kodlaması
                    if currency != 'TRY':
                        if amount > 1000:
                            st.write(f"🔴 **{amount:.0f} ₺**")
                        elif amount > 500:
                            st.write(f"🟡 **{amount:.0f} ₺**")
                        else:
                            st.write(f"🟢 **{amount:.0f} ₺**")
                    else:
                        # TRY için de renk kodlaması
                        if amount > 1000:
                            st.write(f"🔴 **{amount:.0f} ₺**")
                        elif amount > 500:
                            st.write(f"🟡 **{amount:.0f} ₺**")
                        else:
                            st.write(f"🟢 **{amount:.0f} ₺**")
                
                with col6:
                    if display_time != "—":
                        st.write(f"🕐 {display_time}")
                    else:
                        st.write("—")
                        
            except Exception as e:
                continue
                
        # Güncelleme butonu
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Listeyi Yenile", key="refresh_recent", type="secondary"):
                st.cache_data.clear()
                st.rerun()
                
        st.caption("💡 Liste otomatik olarak en son eklenen 10 harcamayı gösterir")
        
    else:
        st.info("📝 Henüz harcama kaydı bulunmuyor. Harcama eklemek için ➕ Harcama Ekle sayfasını kullanın.")
    
    st.subheader("📈 İnteraktif Harcama Trendi")
    
    # Tarih aralığı seçimi
    col_period1, col_period2 = st.columns(2)
    with col_period1:
        period_options = {
            "Son 7 Gün": 7,
            "Son 15 Gün": 15,
            "Son 30 Gün": 30,
            "Son 60 Gün": 60,
            "Son 90 Gün": 90
        }
        selected_period = st.selectbox("📅 Zaman Aralığı:", list(period_options.keys()), index=2)
        days = period_options[selected_period]
    
    with col_period2:
        chart_type = st.selectbox("📊 Grafik Tipi:", ["Çizgi Grafik", "Alan Grafik", "Bar Grafik"])
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_data = [item for item in data if item['date'] >= cutoff_date]
    
    if recent_data:
        # Günlük toplam hesaplama
        daily_totals = {}
        daily_counts = {}
        daily_details = {}
        
        for item in recent_data:
            date_str = item['date'].strftime('%Y-%m-%d')
            daily_totals[date_str] = daily_totals.get(date_str, 0) + item['amount']
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            
            if date_str not in daily_details:
                daily_details[date_str] = []
            daily_details[date_str].append(item)
        
        # Eksik günleri sıfır ile doldur
        start_date = cutoff_date.date()
        end_date = datetime.now().date()
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in daily_totals:
                daily_totals[date_str] = 0
                daily_counts[date_str] = 0
            current_date += timedelta(days=1)
        
        # Sıralı liste oluştur
        sorted_dates = sorted(daily_totals.keys())
        sorted_amounts = [daily_totals[date] for date in sorted_dates]
        sorted_counts = [daily_counts[date] for date in sorted_dates]
        
        # Hover bilgileri hazırla
        hover_text = []
        for i, date in enumerate(sorted_dates):
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d %B %Y')
            count = sorted_counts[i]
            amount = sorted_amounts[i]
            
            hover_info = f"<b>{formatted_date}</b><br>"
            hover_info += f"💰 Toplam: {amount:,.0f} TL<br>"
            hover_info += f"📊 İşlem Sayısı: {count}<br>"
            
            if date in daily_details and daily_details[date]:
                hover_info += "<br><b>🏷️ Kategoriler:</b><br>"
                category_amounts = {}
                for item in daily_details[date]:
                    cat = item['category_name'].title()
                    category_amounts[cat] = category_amounts.get(cat, 0) + item['amount']
                
                for cat, cat_amount in sorted(category_amounts.items(), key=lambda x: x[1], reverse=True)[:3]:
                    hover_info += f"• {cat}: {cat_amount:,.0f} TL<br>"
            
            hover_text.append(hover_info)
        
        # Grafik oluştur
        if chart_type == "Çizgi Grafik":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sorted_dates,
                y=sorted_amounts,
                mode='lines+markers',
                name='Günlük Harcama',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#667eea'),
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.1)',
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            ))
        
        elif chart_type == "Alan Grafik":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sorted_dates,
                y=sorted_amounts,
                mode='lines',
                name='Günlük Harcama',
                line=dict(color='#667eea', width=2),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.3)',
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            ))
        
        else:  # Bar Grafik
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sorted_dates,
                y=sorted_amounts,
                name='Günlük Harcama',
                marker_color='#667eea',
                opacity=0.8,
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            ))
        
        # Dark mode'a göre grafik düzenleme
        title_color = '#f1f5f9' if dark_mode else '#1e293b'
        font_color = '#94a3b8' if dark_mode else '#64748b'
        grid_color = 'rgba(100,116,139,0.3)' if dark_mode else 'rgba(0,0,0,0.1)'
        
        fig.update_layout(
            title=dict(
                text=f"📈 {selected_period} Harcama Trendi ({chart_type})",
                font=dict(size=20, color=title_color),
                x=0.5
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=font_color),
            showlegend=False,
            margin=dict(l=0, r=0, t=60, b=0),
            hovermode='x unified'
        )
        
        fig.update_xaxes(
            title="📅 Tarih",
            gridcolor=grid_color,
            showgrid=True,
            zeroline=False,
            tickformat='%d.%m',
            title_font=dict(color=font_color),
            tickfont=dict(color=font_color)
        )
        
        fig.update_yaxes(
            title="💰 Tutar (TL)",
            gridcolor=grid_color,
            showgrid=True,
            zeroline=False,
            tickformat=',.0f',
            title_font=dict(color=font_color),
            tickfont=dict(color=font_color)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # İstatistik özeti
        col1, col2, col3, col4 = st.columns(4)
        
        total_amount = sum(sorted_amounts)
        avg_daily = total_amount / len(sorted_amounts) if sorted_amounts else 0
        max_day = max(sorted_amounts) if sorted_amounts else 0
        total_transactions = sum(sorted_counts)
        
        with col1:
            st.metric("💳 Toplam Harcama", f"{total_amount:,.0f} TL")
        with col2:
            st.metric("📊 Günlük Ortalama", f"{avg_daily:,.0f} TL")
        with col3:
            st.metric("🔝 En Yüksek Gün", f"{max_day:,.0f} TL")
        with col4:
            st.metric("🧾 Toplam İşlem", f"{total_transactions}")
    
    else:
        st.info(f"📅 Son {days} günde harcama kaydı bulunamadı.")
    
    # Akıllı Öneriler Bölümü
    st.markdown("---")
    st.subheader("🤖 Akıllı Finansal Öneriler")
    
    # Harcama pattern analizini çalıştır
    insights = analyze_spending_patterns()
    
    if insights:
        # Önerileri priority'ye göre grupla
        high_priority = [i for i in insights if i['priority'] == 'high']
        medium_priority = [i for i in insights if i['priority'] == 'medium']
        low_priority = [i for i in insights if i['priority'] == 'low']
        
        # Yüksek öncelikli uyarılar
        if high_priority:
            st.markdown("### ⚠️ Önemli Uyarılar")
            for insight in high_priority:
                with st.container():
                    # Dark mode'a göre alert renkleri
                    if insight['type'] == 'warning':
                        bg_color = 'linear-gradient(90deg, #dc2626, #ef4444)' if dark_mode else 'linear-gradient(90deg, #fef2f2, #fee2e2)'
                        text_color = '#fecaca' if dark_mode else '#dc2626'
                    else:
                        bg_color = 'linear-gradient(90deg, #1e40af, #3b82f6)' if dark_mode else 'linear-gradient(90deg, #eff6ff, #dbeafe)'
                        text_color = '#dbeafe' if dark_mode else '#1e40af'
                    
                    st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        padding: 1rem; 
                        border-radius: 12px; 
                        margin: 0.5rem 0;
                        border-left: 4px solid {text_color.replace('#', '').replace('fecaca', '#dc2626').replace('dbeafe', '#1e40af')};
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{insight['icon']}</span>
                            <strong style="color: {text_color}; font-size: 1.1rem;">{insight['title']}</strong>
                        </div>
                        <p style="color: {text_color}; margin: 0.3rem 0; font-size: 0.95rem;">{insight['message']}</p>
                        <p style="color: {text_color.replace('#dc2626', '#b91c1c').replace('#1e40af', '#1e3a8a')}; margin: 0; font-size: 0.85rem; font-style: italic;">
                            💡 {insight['suggestion']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Orta ve düşük öncelikli öneriler
        other_insights = medium_priority + low_priority
        if other_insights:
            st.markdown("### 💡 Diğer Öneriler")
            
            # 2 sütunlu layout
            col1, col2 = st.columns(2)
            
            for i, insight in enumerate(other_insights[:6]):  # En fazla 6 öneri göster
                target_col = col1 if i % 2 == 0 else col2
                
                with target_col:
                    # Öneri tipine göre renk seçimi
                    if insight['type'] == 'success':
                        bg_color = 'linear-gradient(90deg, #065f46, #10b981)' if dark_mode else 'linear-gradient(90deg, #f0fdf4, #dcfce7)'
                        text_color = '#d1fae5' if dark_mode else '#065f46'
                        border_color = '#10b981'
                    elif insight['type'] == 'warning':
                        bg_color = 'linear-gradient(90deg, #92400e, #f59e0b)' if dark_mode else 'linear-gradient(90deg, #fffbeb, #fef3c7)'
                        text_color = '#fed7aa' if dark_mode else '#92400e'
                        border_color = '#f59e0b'
                    else:  # info
                        bg_color = 'linear-gradient(90deg, #1e40af, #3b82f6)' if dark_mode else 'linear-gradient(90deg, #eff6ff, #dbeafe)'
                        text_color = '#dbeafe' if dark_mode else '#1e40af'
                        border_color = '#3b82f6'
                    
                    st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        padding: 1rem; 
                        border-radius: 10px; 
                        margin: 0.5rem 0;
                        border: 1px solid {border_color};
                        min-height: 120px;
                        transition: transform 0.2s ease;
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.1rem; margin-right: 0.5rem;">{insight['icon']}</span>
                            <strong style="color: {text_color}; font-size: 1rem;">{insight['title']}</strong>
                        </div>
                        <p style="color: {text_color}; margin: 0.3rem 0; font-size: 0.9rem; line-height: 1.3;">{insight['message']}</p>
                        <p style="color: {text_color}; margin: 0; font-size: 0.8rem; font-style: italic; opacity: 0.9;">
                            {insight['suggestion']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        # Veri yoksa genel öneriler göster
        st.info("📊 Detaylı analiz için daha fazla harcama verisi gerekiyor.")
        
        st.markdown("### 📚 Genel Finansal İpuçları")
        recommendations = get_spending_recommendations()
        
        col1, col2 = st.columns(2)
        for i, rec in enumerate(recommendations[:4]):  # İlk 4 öneriyi göster
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                bg_color = 'linear-gradient(90deg, #1e293b, #334155)' if dark_mode else 'linear-gradient(90deg, #f8fafc, #f1f5f9)'
                text_color = '#f1f5f9' if dark_mode else '#1e293b'
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    padding: 1rem; 
                    border-radius: 10px; 
                    margin: 0.5rem 0;
                    border: 1px solid {'#475569' if dark_mode else '#e2e8f0'};
                    min-height: 120px;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.1rem; margin-right: 0.5rem;">{rec['icon']}</span>
                        <strong style="color: {text_color}; font-size: 1rem;">{rec['title']}</strong>
                    </div>
                    <p style="color: {text_color}; margin: 0.3rem 0; font-size: 0.9rem; line-height: 1.3;">{rec['description']}</p>
                    <p style="color: {'#94a3b8' if dark_mode else '#64748b'}; margin: 0; font-size: 0.8rem; font-style: italic;">
                        ⚡ {rec['action']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

elif page == "📊 Harcama Analizi":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb, #f5576c); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">📊 Detaylı Harcama Analizi</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Harcama alışkanlıklarınızı detaylı analiz edin</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not data:
        st.warning("📊 Analiz için veri bulunamadı!")
        st.stop()
    
    category_totals = {}
    for item in data:
        cat = item['category_name']
        category_totals[cat] = category_totals.get(cat, 0) + item['amount']
    
    if category_totals:
        # İnteraktif kontroller
        col1, col2 = st.columns(2)
        with col1:
            pie_type = st.selectbox("📊 Grafik Türü:", ["Pasta Grafik", "Donut Grafik", "Bar Grafik"])
        with col2:
            show_values = st.checkbox("💰 Değerleri Göster", value=True)
        
        # Modern renk paleti
        modern_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#a8edea', '#fed6e3']
        
        # Veriyi hazırla
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        labels = [cat.title() for cat, _ in sorted_categories]
        values = [amount for _, amount in sorted_categories]
        
        # Detaylı hover bilgileri hazırla
        total_amount = sum(values)
        hover_text = []
        for i, (label, value) in enumerate(zip(labels, values)):
            percentage = (value / total_amount * 100) if total_amount > 0 else 0
            
            # Bu kategorideki işlem sayısını hesapla
            cat_transactions = len([item for item in data if item['category_name'].lower() == label.lower()])
            avg_transaction = value / cat_transactions if cat_transactions > 0 else 0
            
            hover_info = f"<b>{label}</b><br>"
            hover_info += f"💰 Tutar: {value:,.0f} TL<br>"
            hover_info += f"📊 Oran: {percentage:.1f}%<br>"
            hover_info += f"🧾 İşlem Sayısı: {cat_transactions}<br>"
            hover_info += f"💳 Ortalama İşlem: {avg_transaction:,.0f} TL"
            
            hover_text.append(hover_info)
        
        if pie_type == "Pasta Grafik":
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text,
                textinfo='label+percent' if show_values else 'label',
                textposition='inside',
                marker=dict(
                    colors=modern_colors[:len(labels)],
                    line=dict(color='#FFFFFF', width=2)
                ),
                pull=[0.05 if i == 0 else 0 for i in range(len(labels))]  # En büyük dilimi çıkar
            )])
            
        elif pie_type == "Donut Grafik":
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text,
                textinfo='label+percent' if show_values else 'label',
                textposition='inside',
                marker=dict(
                    colors=modern_colors[:len(labels)],
                    line=dict(color='#FFFFFF', width=2)
                )
            )])
            
        else:  # Bar Grafik
            fig_pie = go.Figure(data=[go.Bar(
                x=values,
                y=labels,
                orientation='h',
                marker=dict(
                    color=modern_colors[:len(labels)],
                    opacity=0.8
                ),
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            )])
        
        # Layout düzenlemesi - Dark mode desteği
        title_color = '#f1f5f9' if dark_mode else '#1e293b'
        font_color = '#94a3b8' if dark_mode else '#64748b'
        grid_color = 'rgba(100,116,139,0.3)' if dark_mode else 'rgba(0,0,0,0.1)'
        
        if pie_type in ["Pasta Grafik", "Donut Grafik"]:
            fig_pie.update_layout(
                title=dict(
                    text="🎯 Harcama Kategorileri Dağılımı",
                    font=dict(size=20, color=title_color),
                    x=0.5
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=font_color, size=12),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(color=font_color)
                ),
                margin=dict(l=0, r=0, t=60, b=0)
            )
            
            # Donut grafiği için merkez yazı
            if pie_type == "Donut Grafik":
                fig_pie.add_annotation(
                    text=f"<b>Toplam</b><br>{total_amount:,.0f} TL",
                    showarrow=False,
                    font_size=16,
                    font_color=title_color
                )
        else:
            fig_pie.update_layout(
                title=dict(
                    text="🎯 Harcama Kategorileri Dağılımı",
                    font=dict(size=20, color=title_color),
                    x=0.5
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=font_color),
                showlegend=False,
                margin=dict(l=0, r=0, t=60, b=0),
                xaxis_title="💰 Tutar (TL)",
                yaxis_title="📂 Kategoriler"
            )
            
            fig_pie.update_xaxes(
                gridcolor=grid_color,
                showgrid=True,
                tickformat=',.0f',
                title_font=dict(color=font_color),
                tickfont=dict(color=font_color)
            )
            
            fig_pie.update_yaxes(
                title_font=dict(color=font_color),
                tickfont=dict(color=font_color)
            )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # En çok harcama yapılan kategoriler detayları ile
        st.subheader("🏆 Top Kategoriler ve Harcama Detayları")
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        for i, (category, amount) in enumerate(sorted_categories[:5], 1):
            st.write(f"**{i}. {category.title()}: {amount:.0f} TL**")
            
            # Bu kategorideki harcamaları getir
            category_expenses = [
                item for item in data 
                if item['category_name'].lower() == category.lower()
            ]
            
            # Son 10 harcamayı göster
            recent_category_expenses = sorted(category_expenses, key=lambda x: x['date'], reverse=True)[:10]
            
            # Harcama detaylarını göster
            if recent_category_expenses:
                with st.expander(f"📋 {category.title()} kategorisindeki son harcamalar"):
                    # Başlık satırı
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                    with col1:
                        st.write("**📅 Tarih**")
                    with col2:
                        st.write("**📝 Açıklama**")
                    with col3:
                        st.write("**💱 Orijinal**")
                    with col4:
                        st.write("**💰 TL Karşılığı**")
                    
                    st.markdown("---")
                    
                    for expense in recent_category_expenses:
                        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                        with col1:
                            st.write(expense['date'].strftime('%d.%m.%Y'))
                        with col2:
                            description = expense.get('description', 'Açıklama yok')
                            if description and description != f"{category.title()} harcaması":
                                st.write(f"📝 {description}")
                            else:
                                st.write("📝 Açıklama yok")
                        with col3:
                            # Orijinal para birimi gösterimi
                            original_amount = expense.get('original_amount', expense['amount'])
                            currency = expense.get('currency', 'TRY')
                            
                            if currency != 'TRY':
                                st.write(f"**{format_currency_display(original_amount, currency)}**")
                            else:
                                st.write(f"**{original_amount:.0f} ₺**")
                        with col4:
                            # TL karşılığı
                            tl_amount = expense['amount']
                            if currency != 'TRY':
                                st.write(f"**{tl_amount:.0f} ₺**")
                            else:
                                st.write("—")
                    
                    # Kategori istatistikleri
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Toplam İşlem", f"{len(category_expenses)}")
                    with col2:
                        avg_amount = sum(exp['amount'] for exp in category_expenses) / len(category_expenses)
                        st.metric("💰 Ortalama (TL)", f"{avg_amount:.0f} ₺")
                    with col3:
                        max_expense = max(category_expenses, key=lambda x: x['amount'])
                        st.metric("🔝 En Yüksek (TL)", f"{max_expense['amount']:.0f} ₺")
                    with col4:
                        # Farklı para birimlerini say
                        currencies_used = set(exp.get('currency', 'TRY') for exp in category_expenses)
                        st.metric("💱 Para Birimi", f"{len(currencies_used)} çeşit")
                    
                    # Para birimi dağılımı
                    if len(currencies_used) > 1:
                        st.markdown("**💱 Para Birimi Dağılımı:**")
                        currency_breakdown = {}
                        for exp in category_expenses:
                            currency = exp.get('currency', 'TRY')
                            original_amount = exp.get('original_amount', exp['amount'])
                            currency_breakdown[currency] = currency_breakdown.get(currency, 0) + original_amount
                        
                        for curr, total in currency_breakdown.items():
                            if curr != 'TRY':
                                tl_equiv = sum(exp['amount'] for exp in category_expenses if exp.get('currency', 'TRY') == curr)
                                st.caption(f"• {curr}: {format_currency_display(total, curr)} = {tl_equiv:.0f} ₺")
                            else:
                                st.caption(f"• TRY: {total:.0f} ₺")
            
            st.markdown("---")

elif page == "🎭 Kişilik Profili":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">🎭 Harcama Kişiliğiniz</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Harcama alışkanlıklarınıza göre kişilik analiziniz</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Kişilik analizi yap
        analyzer = PersonalityAnalyzer()
        
        # Tab menü
        tab1, tab2, tab3, tab4 = st.tabs(["🎭 Profil Analizim", "📊 Detaylı İstatistikler", "📈 Kişilik Gelişimi", "🎯 Tüm Profiller"])
        
        with tab1:
            st.markdown("### 🎭 Mevcut Kişilik Profiliniz")
            
            # Analiz periyodu seçimi
            col1, col2 = st.columns(2)
            with col1:
                analysis_period = st.selectbox(
                    "📅 Analiz Periyodu:",
                    [("Son 30 Gün", 30), ("Son 60 Gün", 60), ("Son 90 Gün", 90), ("Son 6 Ay", 180)],
                    index=2,
                    format_func=lambda x: x[0]
                )
                days = analysis_period[1]
            
            with col2:
                if st.button("🔄 Analizi Yenile", type="secondary"):
                    st.cache_data.clear()
                    st.rerun()
            
            # Kişilik analizi
            personality_analysis = analyzer.analyze_user_personality(days=days)
            profile = personality_analysis['profile']
            patterns = personality_analysis['patterns']
            insights = personality_analysis['insights']
            
            if profile['profile'] != 'yeni_kullanıcı':
                # Ana profil kartı
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {profile['color']}, {profile['color']}aa);
                    padding: 30px;
                    border-radius: 20px;
                    margin: 20px 0;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                    border: 3px solid {profile['color']};
                ">
                    <div style="color: white; text-align: center;">
                        <div style="font-size: 64px; margin-bottom: 15px;">{profile['emoji']}</div>
                        <h1 style="margin: 0; font-size: 32px; font-weight: bold;">{profile['name']}</h1>
                        <p style="margin: 15px 0; font-size: 18px; opacity: 0.95; line-height: 1.4;">{profile['description']}</p>
                        <div style="background: rgba(255,255,255,0.25); padding: 12px 24px; border-radius: 25px; display: inline-block; margin-top: 15px;">
                            <span style="font-weight: bold; font-size: 16px;">Güven Skoru: %{profile['confidence']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Öneriler ve içgörüler
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 💡 Size Özel İpuçları")
                    for i, tip in enumerate(profile.get('tips', []), 1):
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(90deg, {profile['color']}22, {profile['color']}11);
                            padding: 12px;
                            border-radius: 10px;
                            margin: 8px 0;
                            border-left: 4px solid {profile['color']};
                        ">
                            <strong>{i}.</strong> {tip}
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### 📊 Harcama İçgörüleri")
                    for insight in insights:
                        st.markdown(f"""
                        <div style="
                            background: #f8fafc;
                            padding: 12px;
                            border-radius: 10px;
                            margin: 8px 0;
                            border-left: 4px solid #64748b;
                        ">
                            <strong>{insight['icon']} {insight['title']}</strong><br>
                            <span style="color: #64748b;">{insight['description']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Harcama dağılımı grafiği
                if patterns.get('category_percentages'):
                    st.markdown("#### 🎯 Harcama Kategorisi Dağılımı")
                    
                    categories = list(patterns['category_percentages'].keys())
                    percentages = list(patterns['category_percentages'].values())
                    
                    # Kişiliğe uygun renkler
                    colors = [profile['color'] + str(hex(50 + i*30))[2:] for i in range(len(categories))]
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=[cat.title() for cat in categories],
                        values=percentages,
                        hole=.4,
                        textinfo='label+percent',
                        textposition='outside',
                        marker=dict(
                            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD'],
                            line=dict(color='#FFFFFF', width=3)
                        )
                    )])
                    
                    fig_pie.update_layout(
                        title=f"{profile['emoji']} {profile['name']} - Harcama Dağılımı",
                        title_x=0.5,
                        font=dict(size=14),
                        showlegend=True,
                        height=500,
                        margin=dict(t=70, b=50, l=50, r=50)
                    )
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            else:
                # Yeni kullanıcı için özel mesaj
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #A0A0A0, #888888);
                    padding: 30px;
                    border-radius: 20px;
                    margin: 20px 0;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                    border: 3px solid #A0A0A0;
                ">
                    <div style="color: white; text-align: center;">
                        <div style="font-size: 64px; margin-bottom: 15px;">🌟</div>
                        <h1 style="margin: 0; font-size: 32px; font-weight: bold;">Yeni Kullanıcı</h1>
                        <p style="margin: 15px 0; font-size: 18px; opacity: 0.95; line-height: 1.4;">Henüz yeni başlıyorsunuz! Daha fazla veri toplandıkça kişiliğinizi keşfedeceğiz.</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                progress_info = patterns.get('expense_count', 0)
                progress = min(100, (progress_info / 10) * 100)
                
                st.progress(progress / 100)
                st.info(f"""
                **Kişilik profili için gereken minimum veri:**
                - Mevcut harcama sayınız: {progress_info} 
                - Hedef: 10 harcama kaydı
                - İlerleme: %{progress:.0f}
                
                💡 **Yapılacaklar:**
                • Farklı kategorilerde harcamalar ekleyin
                • Düzenli kayıt tutmaya devam edin
                • En az 5-10 harcama kaydı oluşturun
                """)
        
        with tab2:
            st.markdown("### 📊 Detaylı Harcama İstatistikleri")
            
            if patterns.get('expense_count', 0) > 0:
                # İstatistik kartları
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "💳 Toplam Harcama",
                        f"{patterns.get('total_spending', 0):,.0f} ₺"
                    )
                
                with col2:
                    st.metric(
                        "📈 Harcama Sayısı", 
                        f"{patterns.get('expense_count', 0)}"
                    )
                
                with col3:
                    avg_spending = patterns.get('spending_behavior', {}).get('average_spending', 0)
                    st.metric(
                        "📊 Ortalama Harcama",
                        f"{avg_spending:.0f} ₺"
                    )
                
                with col4:
                    weekend_pct = patterns.get('weekend_vs_weekday', {}).get('weekend_percentage', 0)
                    st.metric(
                        "🎉 Hafta Sonu Oranı",
                        f"%{weekend_pct:.1f}"
                    )
                
                # Davranış analizi
                st.markdown("#### 🔍 Harcama Davranışı Analizi")
                
                behavior = patterns.get('spending_behavior', {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**💰 Harcama Büyüklüğü Dağılımı**")
                    
                    high_ratio = behavior.get('high_amount_ratio', 0)
                    small_ratio = behavior.get('small_amount_ratio', 0)
                    medium_ratio = 100 - high_ratio - small_ratio
                    
                    fig_behavior = go.Figure(data=[go.Bar(
                        x=['Küçük (≤100₺)', 'Orta (100-1000₺)', 'Büyük (≥1000₺)'],
                        y=[small_ratio, medium_ratio, high_ratio],
                        marker_color=['#4ECDC4', '#FECA57', '#FF6B6B']
                    )])
                    
                    fig_behavior.update_layout(
                        title="Harcama Büyüklüğü Oranları (%)",
                        yaxis_title="Yüzde (%)",
                        height=300
                    )
                    
                    st.plotly_chart(fig_behavior, use_container_width=True)
                
                with col2:
                    st.markdown("**📅 Hafta İçi vs Hafta Sonu**")
                    
                    weekend_data = patterns.get('weekend_vs_weekday', {})
                    weekday_pct = weekend_data.get('weekday_percentage', 0)
                    weekend_pct = weekend_data.get('weekend_percentage', 0)
                    
                    fig_weekend = go.Figure(data=[go.Pie(
                        labels=['Hafta İçi', 'Hafta Sonu'],
                        values=[weekday_pct, weekend_pct],
                        hole=.3,
                        marker_colors=['#45B7D1', '#FF9FF3']
                    )])
                    
                    fig_weekend.update_layout(
                        title="Hafta İçi vs Hafta Sonu Harcama",
                        height=300
                    )
                    
                    st.plotly_chart(fig_weekend, use_container_width=True)
                
                # Kategori detayları
                if patterns.get('category_spending'):
                    st.markdown("#### 📋 Kategori Bazlı Detaylar")
                    
                    category_data = []
                    for category, amount in patterns['category_spending'].items():
                        frequency = patterns.get('category_frequency', {}).get(category, 0)
                        percentage = patterns.get('category_percentages', {}).get(category, 0)
                        avg_per_transaction = amount / frequency if frequency > 0 else 0
                        
                        category_data.append({
                            'Kategori': category.title(),
                            'Toplam Harcama': f"{amount:,.0f} ₺",
                            'İşlem Sayısı': frequency,
                            'Ortalama/İşlem': f"{avg_per_transaction:.0f} ₺",
                            'Oran': f"%{percentage:.1f}"
                        })
                    
                    # Dataframe oluştur ve göster
                    df_categories = pd.DataFrame(category_data)
                    st.dataframe(df_categories, use_container_width=True)
            
            else:
                st.info("📊 Detaylı istatistikler için daha fazla harcama verisi gerekli.")
        
        with tab3:
            st.markdown("### 📈 Kişilik Profili Gelişimi")
            
            evolution = analyzer.get_personality_evolution([30, 60, 90, 180])
            
            if len(evolution) > 1:
                # Gelişim grafiği
                periods = list(evolution.keys())
                profile_names = [evolution[p]['profile_name'] for p in periods]
                confidences = [evolution[p]['confidence'] for p in periods]
                spendings = [evolution[p]['total_spending'] for p in periods]
                
                # Zaman serisini oluştur
                fig_evolution = go.Figure()
                
                # Güven skoru çizgisi
                fig_evolution.add_trace(go.Scatter(
                    x=[p.replace('_days', ' Gün') for p in periods],
                    y=confidences,
                    mode='lines+markers',
                    name='Güven Skoru (%)',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ))
                
                fig_evolution.update_layout(
                    title="Kişilik Profili Güven Skoru Gelişimi",
                    xaxis_title="Zaman Periyodu", 
                    yaxis_title="Güven Skoru (%)",
                    height=400
                )
                
                st.plotly_chart(fig_evolution, use_container_width=True)
                
                # Profil değişimleri
                st.markdown("#### 🔄 Profil Değişim Geçmişi")
                
                for i, (period, data) in enumerate(evolution.items()):
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**{period.replace('_days', ' Gün')}**")
                    
                    with col2:
                        st.write(data['profile_name'])
                    
                    with col3:
                        st.write(f"%{data['confidence']}")
                    
                    with col4:
                        st.write(f"{data['total_spending']:,.0f} ₺")
                
            else:
                st.info("📈 Kişilik gelişimi için daha uzun süre veri gerekli.")
        
        with tab4:
            st.markdown("### 🎯 Tüm Kişilik Profilleri")
            
            # Tüm profilleri göster
            all_profiles = analyzer.personality_profiles
            
            for profile_key, profile_data in all_profiles.items():
                with st.expander(f"{profile_data['emoji']} {profile_data['name']}", expanded=False):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="
                            background: {profile_data['color']};
                            color: white;
                            padding: 20px;
                            border-radius: 15px;
                            text-align: center;
                        ">
                            <div style="font-size: 48px; margin-bottom: 10px;">{profile_data['emoji']}</div>
                            <h3 style="margin: 0;">{profile_data['name']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"**Açıklama:** {profile_data['description']}")
                        
                        st.markdown("**💡 İpuçları:**")
                        for tip in profile_data.get('tips', []):
                            st.markdown(f"• {tip}")
    
    except Exception as e:
        st.error(f"Kişilik analizi yapılırken hata oluştu: {str(e)}")
        st.info("""
        **Kişilik Profili için Gereken Koşullar:**
        - En az 5-10 harcama kaydı
        - Farklı kategorilerde harcamalar
        - Son 30 gün içinde düzenli kayıt
        
        Lütfen önce bazı harcamalar ekleyip tekrar deneyin.
        """)

elif page == "📈 Butce Planlama":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea, #fed6e3); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: #1e293b; margin: 0; text-align: center;">📈 Akıllı Bütçe Planlama</h2>
        <p style="color: #64748b; margin: 0.5rem 0 0 0; text-align: center;">50/30/20 kuralı ile ideal bütçenizi oluşturun</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💰 Gelir Bilgileri")
    
    # Gelir girişi - iki kolonlu düzen
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_income = st.number_input("💼 Aylık Maaş/Asıl Gelir (TL):", value=15000, step=500, min_value=0)
        st.caption("Düzenli maaş, emekli maaşı vb.")
    
    with col2:
        extra_income = st.number_input("💰 Ekstra Gelir (TL):", value=0, step=250, min_value=0)
        st.caption("Freelance, kira geliri, bonus vb.")
    
    # Toplam gelir hesaplama
    total_income = monthly_income + extra_income
    
    if total_income > 0:
        # Gelir özeti
        st.markdown("### 📊 Gelir Özeti")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💼 Asıl Gelir", f"{monthly_income:,.0f} TL")
        with col2:
            st.metric("💰 Ekstra Gelir", f"{extra_income:,.0f} TL")
        with col3:
            st.metric("💎 Toplam Gelir", f"{total_income:,.0f} TL")
        
        st.markdown("---")
        
        # 50/30/20 kuralı - toplam gelir üzerinden
        st.subheader("💰 50/30/20 Bütçe Kuralı")
        needs = total_income * 0.5
        wants = total_income * 0.3
        savings = total_income * 0.2
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏠 İhtiyaçlar (50%)", f"{needs:.0f} TL")
            st.caption("Kira, faturalar, market")
        with col2:
            st.metric("🎮 İstekler (30%)", f"{wants:.0f} TL")
            st.caption("Eğlence, restoran")
        with col3:
            st.metric("💎 Tasarruf (20%)", f"{savings:.0f} TL")
            st.caption("Acil durum, yatırım")
        
        # Ekstra gelir önerileri
        if extra_income > 0:
            st.markdown("---")
            st.subheader("💡 Ekstra Gelir Önerileri")
            
            extra_percent = (extra_income / total_income) * 100
            
            if extra_percent > 20:
                st.success(f"🎉 Harika! Ekstra geliriniz toplam gelirinizin %{extra_percent:.1f}'ini oluşturuyor!")
                st.info("💡 **Öneri**: Bu ekstra gelirin büyük kısmını tasarrufa ve yatırıma yönlendirmeyi düşünün.")
            elif extra_percent > 10:
                st.info(f"👍 Güzel! Ekstra geliriniz toplam gelirinizin %{extra_percent:.1f}'ini oluşturuyor.")
                st.info("💡 **Öneri**: Bu geliri acil durum fonu oluşturmak için kullanabilirsiniz.")
            else:
                st.info(f"📈 Ekstra geliriniz toplam gelirinizin %{extra_percent:.1f}'ini oluşturuyor.")
                st.info("💡 **Öneri**: Ekstra gelir kaynaklarınızı artırmaya odaklanın.")
        
        # Mevcut harcamalarla karşılaştırma
        if data:
            current_month = datetime.now().month
            current_year = datetime.now().year
            this_month_data = [
                item for item in data 
                if item['date'].month == current_month and item['date'].year == current_year
            ]
            
            total_spending = sum(item['amount'] for item in this_month_data)
            remaining_budget = total_income - total_spending
            
            st.markdown("---")
            st.subheader("📊 Bu Ay Durum")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💳 Bu Ay Harcama", f"{total_spending:.0f} TL")
            with col2:
                st.metric("💰 Kalan Bütçe", f"{remaining_budget:.0f} TL")
            with col3:
                usage_pct = (total_spending / total_income * 100) if total_income > 0 else 0
                st.metric("📈 Bütçe Kullanımı", f"{usage_pct:.1f}%")
    else:
        st.warning("⚠️ Bütçe planlaması için gelir bilgilerinizi girin.")

elif page == "💰 Yatırım Takibi":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">💰 Yatırım Takibi</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Portföyünüzü yönetin ve performansınızı takip edin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab menü
    tab1, tab2, tab3 = st.tabs(["📊 Güncel Fiyatlar", "➕ Yatırım Ekle", "📈 Portföyüm"])
    
    with tab1:
        st.subheader("📊 Güncel Yatırım Fiyatları")
        
        with st.spinner("📈 Güncel fiyatlar yükleniyor..."):
            current_prices = get_all_investment_prices()
        
        if current_prices:
            # Filtreleme seçenekleri
            col1, col2 = st.columns(2)
            with col1:
                filter_type = st.selectbox("🎯 Tür Filtresi:", 
                    ["Tümü", "Döviz", "Kripto", "Değerli Metal", "Hisse/Endeks"],
                    key="price_filter")
            with col2:
                sort_by = st.selectbox("🔄 Sırala:", 
                    ["Fiyat (Yüksek→Düşük)", "Fiyat (Düşük→Yüksek)", "Değişim %"],
                    key="price_sort")
            
            # Fiyat tablosu
            filtered_prices = {}
            type_mapping = {
                "Döviz": "currency",
                "Kripto": "crypto", 
                "Değerli Metal": "precious_metal",
                "Hisse/Endeks": "stock_index"
            }
            
            for symbol, data in current_prices.items():
                if filter_type == "Tümü" or data['type'] == type_mapping.get(filter_type, ''):
                    filtered_prices[symbol] = data
            
            # Sıralama
            if sort_by == "Fiyat (Yüksek→Düşük)":
                sorted_prices = sorted(filtered_prices.items(), key=lambda x: x[1]['price_try'], reverse=True)
            elif sort_by == "Fiyat (Düşük→Yüksek)":
                sorted_prices = sorted(filtered_prices.items(), key=lambda x: x[1]['price_try'])
            else:
                sorted_prices = sorted(filtered_prices.items(), key=lambda x: x[1].get('change_percent', 0), reverse=True)
            
            # Tablo gösterimi
            for symbol, data in sorted_prices:
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                    
                    with col1:
                        # Tip ikonları
                        type_icons = {
                            'currency': '💱',
                            'crypto': '₿',
                            'precious_metal': '🥇',
                            'stock_index': '📊'
                        }
                        icon = type_icons.get(data['type'], '📈')
                        st.write(f"**{icon}**")
                    
                    with col2:
                        st.write(f"**{data['name']}** ({symbol})")
                    
                    with col3:
                        st.write(f"**{data['price_try']:,.2f} ₺**")
                        if 'price_usd' in data:
                            st.caption(f"${data['price_usd']:,.2f}")
                    
                    with col4:
                        change = data.get('change_percent', 0)
                        if change > 0:
                            st.write(f"📈 **+%{change:.2f}**")
                        elif change < 0:
                            st.write(f"📉 **%{change:.2f}**")
                        else:
                            st.write("➡️ **%0.00**")
                    
                    st.markdown("---")
            
            st.caption("🕐 Fiyatlar saatlik güncellenir")
    
    with tab2:
        st.subheader("➕ Yeni Yatırım Ekle")
        
        investment_types = get_investment_types()
        
        if investment_types:
            # Güncel fiyatları al
            current_prices = get_all_investment_prices()
            
            # Form dışında seçimler (real-time güncellenebilir)
            col1, col2 = st.columns(2)
            
            with col1:
                # Yatırım türü seçimi
                type_options = {}
                type_symbols = {}
                for inv_type in investment_types:
                    display_name = f"{inv_type[5]} {inv_type[1]} ({inv_type[2]})"
                    type_options[display_name] = inv_type[0]
                    type_symbols[display_name] = inv_type[2]  # symbol
                
                selected_type_display = st.selectbox("🎯 Yatırım Türü:", list(type_options.keys()), key="inv_type_select")
                selected_type_id = type_options[selected_type_display]
                selected_symbol = type_symbols[selected_type_display]
                
                # Seçilen türün bilgilerini getir
                selected_type_info = next((t for t in investment_types if t[0] == selected_type_id), None)
                
                # Güncel fiyatı göster
                current_price_data = current_prices.get(selected_symbol, {})
                current_price = current_price_data.get('price_try', 0)
                
                if current_price > 0:
                    st.success(f"📈 **Güncel Fiyat**: {current_price:,.2f} ₺")
                else:
                    st.warning("⚠️ Güncel fiyat alınamadı")
                    current_price = 1  # Sıfıra bölme hatası için
            
            with col2:
                amount = st.number_input("💰 Yatırım Tutarı (TL):", min_value=0.01, step=100.0, key="investment_amount")
                
                # Tutar girildiğinde otomatik miktar hesaplama (real-time)
                if amount > 0 and current_price > 0:
                    suggested_quantity = amount / current_price
                    st.info(f"💡 **Bu tutar ile alınabilir**: {suggested_quantity:,.6f} adet")
                    
                    # Hesaplama modu seçimi
                    calc_mode = st.radio(
                        "📊 Hesaplama Modu:",
                        ["🎯 Tutara göre hesapla", "✏️ Manuel miktar gir"],
                        key="calc_mode"
                    )
                    
                    if calc_mode == "🎯 Tutara göre hesapla":
                        # Otomatik hesaplanan miktarı kullan
                        quantity = suggested_quantity
                        st.success(f"📊 **Hesaplanan Miktar**: {quantity:,.6f} adet")
                    else:
                        # Manuel miktar girişi
                        quantity = st.number_input("📊 Miktar/Adet:", 
                                                 min_value=0.000001, 
                                                 step=0.000001,
                                                 format="%.6f",
                                                 key="investment_quantity_manual")
                else:
                    quantity = st.number_input("📊 Miktar/Adet:", min_value=0.000001, step=0.000001, format="%.6f")
            
            # Gerçek zamanlı hesaplamalar ve bilgiler
            if amount > 0 and quantity > 0:
                purchase_price = amount / quantity
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 Hesaplanan Birim Fiyat", f"{purchase_price:,.2f} ₺")
                with col2:
                    st.metric("📊 Toplam Yatırım", f"{amount:,.2f} ₺")
                
                # Güncel fiyat ile karşılaştırma
                if current_price > 0:
                    price_diff = purchase_price - current_price
                    price_diff_percent = (price_diff / current_price) * 100
                    
                    if abs(price_diff_percent) > 5:  # %5'ten fazla fark varsa uyar
                        if price_diff > 0:
                            st.warning(f"⚠️ Girilen fiyat güncel fiyattan **%{price_diff_percent:.1f}** daha yüksek!")
                        else:
                            st.success(f"🎯 Girilen fiyat güncel fiyattan **%{abs(price_diff_percent):.1f}** daha düşük!")
                    else:
                        st.success("✅ Fiyat güncel piyasa değerine yakın")
            
            st.markdown("---")
            
            # Form sadece son bilgiler ve submit için
            with st.form("investment_form"):
                st.write("📝 **Son Bilgiler:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    purchase_date = st.date_input("📅 Alış Tarihi:", value=datetime.now().date())
                with col2:
                    description = st.text_area("📝 Açıklama (Opsiyonel):", height=100)
                
                # Özet bilgi
                if amount > 0 and quantity > 0:
                    st.info(f"""
                    📋 **Yatırım Özeti:**
                    - 🎯 **Araç**: {selected_type_display}
                    - 💰 **Tutar**: {amount:,.2f} ₺
                    - 📊 **Miktar**: {quantity:,.6f} adet
                    - 💵 **Birim Fiyat**: {purchase_price:,.2f} ₺
                    """)
                
                submitted = st.form_submit_button("➕ Yatırım Ekle", type="primary", use_container_width=True)
                
                if submitted:
                    if amount > 0 and quantity > 0:
                        purchase_price = amount / quantity
                        success = add_investment(
                            selected_type_id, amount, quantity, 
                            purchase_price, purchase_date.isoformat(), description
                        )
                        
                        if success:
                            st.success("✅ Yatırım başarıyla eklendi!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Yatırım eklenirken hata oluştu!")
                    else:
                        st.error("❌ Lütfen geçerli tutar ve miktar girin!")
        else:
            st.warning("⚠️ Yatırım türleri yüklenemedi. Veritabanını kontrol edin.")
    
    with tab3:
        st.subheader("📈 Yatırım Portföyüm")
        
        with st.spinner("📊 Portföy analiz ediliyor..."):
            portfolio_data = calculate_portfolio_performance()
        
        if portfolio_data['investments']:
            # Genel özet
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Toplam Yatırım", f"{portfolio_data['total_investment']:,.0f} ₺")
            with col2:
                st.metric("📊 Güncel Değer", f"{portfolio_data['total_current_value']:,.0f} ₺")
            with col3:
                profit_loss = portfolio_data['total_profit_loss']
                delta_color = "normal" if profit_loss >= 0 else "inverse"
                st.metric("📈 Kar/Zarar", f"{profit_loss:,.0f} ₺", 
                         delta=f"{portfolio_data['total_profit_loss_percent']:.1f}%")
            with col4:
                investment_count = len(portfolio_data['investments'])
                st.metric("🎯 Yatırım Sayısı", f"{investment_count}")
            
            st.markdown("---")
            
            # Portföy dağılımı grafiği
            if len(portfolio_data['investments']) > 1:
                st.subheader("🥧 Portföy Dağılımı")
                
                # Pasta grafik için veri hazırla
                labels = [inv['name'] for inv in portfolio_data['investments']]
                values = [inv['current_value'] for inv in portfolio_data['investments']]
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Değer: %{value:,.0f} ₺<br>Oran: %{percent}<extra></extra>'
                )])
                
                fig.update_layout(
                    title="Portföy Dağılımı",
                    showlegend=True,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Detaylı yatırım listesi
            st.subheader("📋 Detaylı Yatırım Listesi")
            
            for inv in portfolio_data['investments']:
                with st.expander(f"{inv['icon']} {inv['name']} - {inv['quantity']:,.2f} {inv['symbol']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**📊 Alış Bilgileri**")
                        st.write(f"📅 Tarih: {inv['purchase_date']}")
                        st.write(f"💰 Birim Fiyat: {inv['purchase_price']:,.2f} ₺")
                        st.write(f"💎 Toplam Tutar: {inv['purchase_amount']:,.2f} ₺")
                    
                    with col2:
                        st.write("**📈 Güncel Durum**")
                        st.write(f"💹 Güncel Fiyat: {inv['current_price']:,.2f} ₺")
                        st.write(f"💰 Toplam Değer: {inv['current_value']:,.2f} ₺")
                        
                        # Kar/zarar gösterimi
                        if inv['profit_loss'] >= 0:
                            st.write(f"📈 **Kar: +{inv['profit_loss']:,.2f} ₺ (+%{inv['profit_loss_percent']:.1f})**")
                        else:
                            st.write(f"📉 **Zarar: {inv['profit_loss']:,.2f} ₺ (%{inv['profit_loss_percent']:.1f})**")
                    
                    with col3:
                        st.write("**📝 Detaylar**")
                        if inv['description']:
                            st.write(f"📄 Açıklama: {inv['description']}")
                        else:
                            st.write("📄 Açıklama: Yok")
                        
                        # Performans değerlendirme
                        if inv['profit_loss_percent'] > 10:
                            st.success("🎉 Mükemmel performans!")
                        elif inv['profit_loss_percent'] > 0:
                            st.info("👍 Pozitif getiri")
                        elif inv['profit_loss_percent'] > -10:
                            st.warning("⚠️ Düşük performans")
                        else:
                            st.error("📉 Dikkat edilmeli")
            
        else:
            st.info("📊 Henüz yatırım kaydınız bulunmuyor. 'Yatırım Ekle' sekmesinden ilk yatırımınızı ekleyebilirsiniz.")

elif page == "📄 PDF Rapor":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">📄 Aylık PDF Rapor</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Detaylı harcama raporlarınızı PDF olarak indirin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ay seçimi
    col1, col2 = st.columns(2)
    with col1:
        current_year = datetime.now().year
        year = st.selectbox("📅 Yıl Seçin:", range(current_year-2, current_year+1), index=2)
    
    with col2:
        current_month = datetime.now().month
        months = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
            7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
        month = st.selectbox("📅 Ay Seçin:", list(months.keys()), 
                           format_func=lambda x: months[x], index=current_month-1)
    
    selected_month = f"{year}-{month:02d}"
    
    # Rapor önizlemesi
    st.subheader(f"📊 {months[month]} {year} Rapor Önizlemesi")
    
    try:
        conn = sqlite3.connect('data/neofinx.db', timeout=30)
        cursor = conn.cursor()
        
        # Seçilen ay için veri al
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total, COUNT(e.id) as count
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y-%m', e.date) = ?
            GROUP BY c.name
            ORDER BY total DESC
        """, (selected_month,))
        preview_data = cursor.fetchall()
        conn.close()
        
        if preview_data:
            total_spending = sum(item[1] for item in preview_data)
            total_transactions = sum(item[2] for item in preview_data)
            
            # Özet kartları
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Toplam Harcama", f"{total_spending:,.0f} ₺")
            with col2:
                st.metric("🧾 İşlem Sayısı", f"{total_transactions}")
            with col3:
                st.metric("📊 Ortalama İşlem", f"{total_spending/total_transactions:,.0f} ₺")
            with col4:
                st.metric("📁 Kategori Sayısı", f"{len(preview_data)}")
            
            # Kategori tablosu
            st.markdown("### 📋 Kategori Detayları")
            for i, (category, total, count) in enumerate(preview_data, 1):
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                with col1:
                    st.write(f"**{i}.**")
                with col2:
                    st.write(f"📁 **{category.title()}**")
                with col3:
                    st.write(f"💰 {total:,.0f} ₺")
                with col4:
                    st.write(f"🧾 {count} işlem")
            
            # PDF oluştur butonu
            st.markdown("---")
            if st.button("📄 PDF Raporu Oluştur ve İndir", type="primary", use_container_width=True):
                with st.spinner("📄 PDF oluşturuluyor..."):
                    pdf_data = generate_monthly_pdf_report(selected_month)
                    
                    if pdf_data:
                        # Base64 encode
                        b64_pdf = base64.b64encode(pdf_data).decode()
                        
                        # Download link
                        filename = f"NeoFinX_Rapor_{months[month]}_{year}.pdf"
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">📥 {filename} İndir</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        st.success("✅ PDF raporu başarıyla oluşturuldu!")
                        st.balloons()
                    else:
                        st.error("❌ PDF oluşturulurken hata oluştu!")
            
        else:
            st.warning(f"⚠️ {months[month]} {year} ayında harcama kaydı bulunamadı!")
            
    except Exception as e:
        st.error(f"❌ Veri yüklenirken hata: {e}")

elif page == "🔮 Harcama Tahmini":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea, #fed6e3); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: #1e293b; margin: 0; text-align: center;">🔮 Gelecek Ay Harcama Tahmini</h2>
        <p style="color: #64748b; margin: 0.5rem 0 0 0; text-align: center;">Yapay zeka ile harcama trendlerinizi analiz edin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tahmin yap
    with st.spinner("🔮 Yapay zeka harcamalarınızı analiz ediyor..."):
        predictions = predict_next_month_spending()
    
    if predictions:
        next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1)
        next_month_name = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
            7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }[next_month.month]
        
        st.subheader(f"📊 {next_month_name} {next_month.year} Tahmini")
        
        # Ana tahmin
        if 'total' in predictions:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🎯 Tahmini Toplam", f"{predictions['total']:,.0f} ₺")
            
            with col2:
                if 'confidence_range' in predictions:
                    lower = predictions['confidence_range']['lower']
                    upper = predictions['confidence_range']['upper']
                    st.metric("📊 Güven Aralığı", f"{lower:,.0f} - {upper:,.0f} ₺")
                else:
                    st.metric("📊 Güven Durumu", "Hesaplanıyor...")
            
            with col3:
                if 'seasonal_adjustment' in predictions:
                    seasonal = predictions['seasonal_adjustment']
                    if seasonal > 1.1:
                        st.metric("🌟 Sezonsal Faktör", "↗️ Yüksek dönem")
                    elif seasonal < 0.9:
                        st.metric("🌟 Sezonsal Faktör", "↘️ Düşük dönem")
                    else:
                        st.metric("🌟 Sezonsal Faktör", "➡️ Normal dönem")
        
        # Kategori tahminleri
        if 'categories' in predictions and predictions['categories']:
            st.markdown("---")
            st.subheader("📁 Kategori Bazlı Tahminler")
            
            # Tahminleri sırala
            sorted_predictions = sorted(predictions['categories'].items(), 
                                      key=lambda x: x[1], reverse=True)
            
            col1, col2 = st.columns(2)
            
            for i, (category, predicted_amount) in enumerate(sorted_predictions):
                target_col = col1 if i % 2 == 0 else col2
                
                with target_col:
                    # Kategori ikonları
                    category_icons = {
                        'yemek': '🍽️', 'ulaşım': '🚗', 'eğlence': '🎮',
                        'sağlık': '🏥', 'alışveriş': '🛒', 'faturalar': '💡',
                        'diğer': '📦'
                    }
                    icon = category_icons.get(category.lower(), '📦')
                    
                    # Card style
                    bg_color = 'linear-gradient(90deg, #1e293b, #334155)' if dark_mode else 'linear-gradient(90deg, #f8fafc, #f1f5f9)'
                    text_color = '#f1f5f9' if dark_mode else '#1e293b'
                    
                    st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        padding: 1rem; 
                        border-radius: 10px; 
                        margin: 0.5rem 0;
                        border: 1px solid {'#475569' if dark_mode else '#e2e8f0'};
                    ">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                                <strong style="color: {text_color}; font-size: 1rem;">{category.title()}</strong>
                            </div>
                            <div style="color: {text_color}; font-size: 1.1rem; font-weight: bold;">
                                {predicted_amount:,.0f} ₺
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Trend analizi
        st.markdown("---")
        st.subheader("📈 Trend Analizi ve Öneriler")
        
        # Geçmiş verilerle karşılaştırma
        try:
            conn = sqlite3.connect('data/neofinx.db', timeout=30)
            cursor = conn.cursor()
            
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute("""
                SELECT SUM(e.amount) as total
                FROM expenses e
                WHERE strftime('%Y-%m', e.date) = ?
            """, (current_month,))
            current_total = cursor.fetchone()[0] or 0
            
            conn.close()
            
            if current_total > 0 and 'total' in predictions:
                change = predictions['total'] - current_total
                change_percent = (change / current_total) * 100
                
                col1, col2 = st.columns(2)
                with col1:
                    if change > 0:
                        st.warning(f"📈 **Artış Bekleniyor**: {change:,.0f} ₺ (%{change_percent:.1f})")
                        st.write("💡 **Öneri**: Harcamalarınızı gözden geçirin")
                    else:
                        st.success(f"📉 **Azalma Bekleniyor**: {abs(change):,.0f} ₺ (%{abs(change_percent):.1f})")
                        st.write("🎉 **Tebrikler**: Tasarruf trend devam ediyor")
                
                with col2:
                    if change_percent > 10:
                        st.error("🚨 **Dikkat**: %10'dan fazla artış")
                    elif change_percent > 5:
                        st.warning("⚠️ **Uyarı**: %5'ten fazla artış")
                    else:
                        st.info("✅ **Normal**: Makul seviyede değişim")
        
        except:
            pass
            
    else:
        st.warning("⚠️ Tahmin yapabilmek için en az 3 aylık veri gerekiyor!")
        st.info("💡 Daha fazla harcama kaydı ekleyerek tahmin kalitesini artırabilirsiniz.")

elif page == "⚠️ Anormal Harcama Tespiti":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">⚠️ Anormal Harcama Tespiti</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Şüpheli ve olağandışı harcamalarınızı tespit edin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analiz yap
    with st.spinner("🔍 Harcamalarınız analiz ediliyor..."):
        anomaly_data = detect_anomalous_expenses()
    
    if anomaly_data and anomaly_data['stats']:
        stats = anomaly_data['stats']
        
        # Genel istatistikler
        st.subheader("📊 Genel İstatistikler")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🧾 Toplam Harcama", f"{stats['total_expenses']}")
        with col2:
            st.metric("📊 Ortalama Tutar", f"{stats['mean_amount']:,.0f} ₺")
        with col3:
            st.metric("⚠️ Anormal Harcama", f"{stats['anomaly_count']}")
        with col4:
            st.metric("📈 Anormal Oranı", f"{stats['anomaly_percentage']:.1f}%")
        
        # Ana anomaliler
        if anomaly_data['anomalies']:
            st.markdown("---")
            st.subheader("🚨 Tespit Edilen Anormal Harcamalar")
            
            for i, anomaly in enumerate(anomaly_data['anomalies'][:5], 1):
                # Anomali tipine göre renk seçimi
                if "Kritik" in anomaly['type']:
                    bg_color = 'linear-gradient(90deg, #dc2626, #ef4444)'
                    text_color = '#fecaca'
                    border_color = '#dc2626'
                elif "Yüksek" in anomaly['type']:
                    bg_color = 'linear-gradient(90deg, #ea580c, #f97316)'
                    text_color = '#fed7aa'
                    border_color = '#ea580c'
                else:
                    bg_color = 'linear-gradient(90deg, #0891b2, #06b6d4)'
                    text_color = '#cffafe'
                    border_color = '#0891b2'
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    padding: 1rem; 
                    border-radius: 12px; 
                    margin: 0.5rem 0;
                    border-left: 4px solid {border_color};
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.2rem; margin-right: 0.5rem;">🚨</span>
                            <strong style="color: {text_color}; font-size: 1.1rem;">{anomaly['type']}</strong>
                        </div>
                        <div style="color: {text_color}; font-size: 1.2rem; font-weight: bold;">
                            {anomaly['amount']:,.0f} ₺
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: {text_color}; font-size: 0.9rem;">
                        <span>📁 {anomaly['category'].title()}</span>
                        <span>📅 {anomaly['date']}</span>
                    </div>
                    <div style="color: {text_color}; margin-top: 0.5rem; font-size: 0.85rem;">
                        📝 {anomaly['description'] if anomaly['description'] else 'Açıklama yok'}
                    </div>
                    <div style="color: {text_color}; margin-top: 0.5rem; font-size: 0.8rem; opacity: 0.9;">
                        📊 Ortalamadan %{anomaly['deviation_percent']:,.0f} sapma • Z-score: {anomaly['z_score']:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Kategori anomalileri
        if anomaly_data.get('category_anomalies'):
            st.markdown("---")
            st.subheader("📁 Kategori Bazlı Anomaliler")
            
            for anomaly in anomaly_data['category_anomalies'][:3]:
                col1, col2, col3 = st.columns([2, 2, 3])
                
                with col1:
                    st.write(f"📁 **{anomaly['category'].title()}**")
                with col2:
                    st.write(f"💰 **{anomaly['amount']:,.0f} ₺**")
                with col3:
                    st.write(f"📊 Kategori ortalaması: {anomaly['category_mean']:,.0f} ₺")
        
        # Zaman bazlı anomaliler
        if anomaly_data.get('time_anomalies'):
            st.markdown("---")
            st.subheader("⏰ Zaman Bazlı Pattern Analizi")
            
            for time_anomaly in anomaly_data['time_anomalies']:
                if time_anomaly['type'] == 'weekend_spike':
                    st.warning(f"📅 **Hafta Sonu Anomalisi**: {time_anomaly['message']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📅 Hafta İçi Ort.", f"{time_anomaly['weekday_avg']:,.0f} ₺")
                    with col2:
                        st.metric("🏖️ Hafta Sonu Ort.", f"{time_anomaly['weekend_avg']:,.0f} ₺")
        
        # Güvenlik önerileri
        st.markdown("---")
        st.subheader("🛡️ Güvenlik Önerileri")
        
        if stats['anomaly_percentage'] > 15:
            st.error("🚨 **Yüksek Risk**: Anormal harcama oranınız %15'ten yüksek!")
            st.write("💡 **Öneriler**:")
            st.write("• Büyük harcamalarınızı gözden geçirin")
            st.write("• Banka hesap hareketlerinizi kontrol edin")
            st.write("• Düzenli harcama alışkanlıklarınızı belirleyin")
        elif stats['anomaly_percentage'] > 5:
            st.warning("⚠️ **Orta Risk**: Bazı anormal harcamalar tespit edildi")
            st.write("💡 **Öneriler**:")
            st.write("• Büyük harcamalarınızı kategorize edin")
            st.write("• Harcama nedenlerini not almayı düşünün")
        else:
            st.success("✅ **Düşük Risk**: Harcama davranışlarınız normal görünüyor")
            st.write("🎉 **Tebrikler**: Tutarlı bir harcama pattern'iniz var")
    
    else:
        st.warning("⚠️ Anomali analizi için en az 10 harcama kaydı gerekiyor!")
        st.info("💡 Daha fazla harcama kaydı ekleyerek analiz kalitesini artırabilirsiniz.")

elif page == "🎯 Akıllı Hedefler":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">🎯 Akıllı Hedef Belirleme</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Finansal hedeflerinizi belirleyin ve takip edin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab sistemi oluştur
    tab1, tab2, tab3 = st.tabs(["🎯 Hedeflerim", "➕ Hedef Ekle", "💡 Akıllı Öneriler"])
    
    with tab1:  # Hedeflerim
        st.markdown("### 📊 Mevcut Hedeflerim")
        
        # Kullanıcının hedeflerini getir
        user_goals = get_user_goals()
        
        if user_goals:
            # Hedef özet kartları
            col1, col2, col3 = st.columns(3)
            
            # Toplam istatistikler
            total_goals = len(user_goals)
            completed_goals = sum(1 for goal in user_goals if (goal[4] / goal[3] * 100) >= 100)
            total_target_amount = sum(goal[3] for goal in user_goals)
            total_saved_amount = sum(goal[4] for goal in user_goals)
            
            with col1:
                st.metric(
                    label="📈 Toplam Hedef",
                    value=f"{total_goals}",
                    delta=f"{completed_goals} tamamlandı"
                )
            
            with col2:
                st.metric(
                    label="🎯 Hedef Tutar",
                    value=f"{total_target_amount:,.0f} ₺",
                    help="Tüm hedeflerin toplam tutarı"
                )
            
            with col3:
                overall_progress = (total_saved_amount / total_target_amount * 100) if total_target_amount > 0 else 0
                st.metric(
                    label="💰 Biriken Tutar",
                    value=f"{total_saved_amount:,.0f} ₺",
                    delta=f"%{overall_progress:.1f} tamamlandı"
                )
            
            st.markdown("---")
            
            # Her hedef için detaylı kart
            for goal in user_goals:
                analytics = calculate_goal_analytics(goal)
                
                # Durum rengi belirleme
                status_colors = {
                    'completed': '#2ecc71',
                    'on_track': '#3498db', 
                    'slightly_behind': '#f39c12',
                    'behind': '#e74c3c',
                    'expired': '#95a5a6'
                }
                
                status_messages = {
                    'completed': '🎉 Tamamlandı!',
                    'on_track': '✅ Yolunda gidiyor',
                    'slightly_behind': '⚠️ Biraz geride',
                    'behind': '🚨 Geride kalıyor',
                    'expired': '⏰ Süresi dolmuş'
                }
                
                color = status_colors.get(analytics['status'], '#95a5a6')
                status_text = status_messages.get(analytics['status'], 'Bilinmiyor')
                
                # Hedef kart tasarımı
                with st.expander(f"🎯 {analytics['title']} - {status_text}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # İlerleme çubuğu
                        progress_value = min(analytics['progress_percent'] / 100, 1.0)
                        
                        st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="font-weight: 600;">İlerleme Durumu</span>
                                <span style="color: {color}; font-weight: 600;">{analytics['progress_percent']:.1f}%</span>
                            </div>
                            <div style="background-color: #f0f2f6; border-radius: 10px; height: 10px; overflow: hidden;">
                                <div style="
                                    background: linear-gradient(90deg, {color}, {color}aa);
                                    height: 100%;
                                    width: {progress_value * 100}%;
                                    border-radius: 10px;
                                    transition: width 0.3s ease;
                                "></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Hedef detayları
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.info(f"🎯 **Hedef:** {analytics['target_amount']:,.0f} ₺")
                            st.success(f"💰 **Biriken:** {analytics['current_amount']:,.0f} ₺")
                            
                        with col_b:
                            st.warning(f"⏳ **Kalan Süre:** {analytics['remaining_days']} gün")
                            st.error(f"📅 **Hedef Tarih:** {analytics['target_date'].strftime('%d.%m.%Y')}")
                        
                        # Aylık gereksinim analizi
                        if analytics['remaining_days'] > 0:
                            st.markdown(f"""
                            **💡 Akıllı Öneri:**
                            - Hedefinize ulaşmak için aylık **{analytics['required_monthly']:,.0f} ₺** biriktirmelisiniz
                            - Orijinal plan: **{analytics['monthly_target']:,.0f} ₺/ay**
                            - Fark: **{analytics['required_monthly'] - analytics['monthly_target']:+,.0f} ₺**
                            """)
                    
                    with col2:
                        # Katkı ekleme formu
                        st.markdown("### 💰 Katkı Ekle")
                        
                        with st.form(f"contribution_form_{analytics['goal_id']}"):
                            contribution_amount = st.number_input(
                                "Miktar (₺)",
                                min_value=0.0,
                                value=0.0,
                                step=10.0,
                                key=f"contrib_{analytics['goal_id']}"
                            )
                            
                            contribution_date = st.date_input(
                                "Tarih",
                                value=datetime.now().date(),
                                key=f"date_{analytics['goal_id']}"
                            )
                            
                            contribution_description = st.text_input(
                                "Açıklama (opsiyonel)",
                                placeholder="Örn: Maaş tasarrufu",
                                key=f"desc_{analytics['goal_id']}"
                            )
                            
                            if st.form_submit_button("💰 Katkı Ekle", type="primary"):
                                if contribution_amount > 0:
                                    if add_goal_contribution(
                                        analytics['goal_id'], 
                                        contribution_amount, 
                                        contribution_date.strftime('%Y-%m-%d'),
                                        contribution_description
                                    ):
                                        st.success(f"✅ {contribution_amount:,.0f} ₺ katkı eklendi!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Katkı eklenirken hata oluştu!")
                                else:
                                    st.warning("⚠️ Katkı miktarı 0'dan büyük olmalıdır!")
        
        else:
            # Henüz hedef yok mesajı
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 15px; border: 2px dashed #cbd5e1;">
                <h3 style="color: #64748b; margin-bottom: 1rem;">🎯 Henüz hedef belirlenmemiş</h3>
                <p style="color: #94a3b8; margin-bottom: 2rem;">Finansal hedeflerinizi belirleyerek tasarruf planınızı oluşturun</p>
                <p style="color: #6366f1; font-weight: 600;">➡️ "Hedef Ekle" sekmesinden başlayabilirsiniz</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:  # Hedef Ekle
        st.markdown("### ➕ Yeni Hedef Oluştur")
        
        # Şablon seçimi
        st.markdown("#### 📋 Hedef Şablonları")
        
        templates = get_goal_templates()
        
        # Şablonları kategorize et
        template_categories = {}
        for template in templates:
            category = template[2]  # category sütunu
            if category not in template_categories:
                template_categories[category] = []
            template_categories[category].append(template)
        
        # Şablon kartları
        for category, items in template_categories.items():
            with st.expander(f"📂 {category.title()}", expanded=True):
                cols = st.columns(min(len(items), 4))
                
                for i, template in enumerate(items):
                    template_id, name, category, icon, description = template
                    
                    with cols[i % 4]:
                        if st.button(
                            f"{icon} {name}", 
                            key=f"template_{template_id}",
                            help=description,
                            use_container_width=True
                        ):
                            st.session_state.selected_template = template
                            st.session_state.goal_title = name
                            st.session_state.goal_type = category
        
        st.markdown("---")
        
        # Hedef oluşturma formu
        st.markdown("#### 🎯 Hedef Detayları")
        
        with st.form("new_goal_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                goal_title = st.text_input(
                    "📝 Hedef Başlığı",
                    value=st.session_state.get('goal_title', ''),
                    placeholder="Örn: Ev alma hedefi"
                )
                
                goal_type = st.selectbox(
                    "📂 Hedef Kategorisi",
                    options=['housing', 'retirement', 'emergency', 'vehicle', 'education', 'vacation', 'investment', 'wedding', 'other'],
                    format_func=lambda x: {
                        'housing': '🏠 Konut',
                        'retirement': '👴 Emeklilik', 
                        'emergency': '🛡️ Acil Durum',
                        'vehicle': '🚗 Araç',
                        'education': '🎓 Eğitim',
                        'vacation': '✈️ Tatil',
                        'investment': '📈 Yatırım',
                        'wedding': '💍 Düğün',
                        'other': '📋 Diğer'
                    }[x],
                    index=['housing', 'retirement', 'emergency', 'vehicle', 'education', 'vacation', 'investment', 'wedding', 'other'].index(st.session_state.get('goal_type', 'housing'))
                )
                
                target_amount = st.number_input(
                    "💰 Hedef Tutar (₺)",
                    min_value=100.0,
                    value=500000.0,
                    step=1000.0,
                    format="%.0f"
                )
            
            with col2:
                target_date = st.date_input(
                    "📅 Hedef Tarihi",
                    value=datetime.now().date() + timedelta(days=730),  # 2 yıl sonra
                    min_value=datetime.now().date() + timedelta(days=30)  # En az 1 ay sonra
                )
                
                description = st.text_area(
                    "📄 Açıklama",
                    placeholder="Hedefiniz hakkında detaylı bilgi...",
                    height=100
                )
                
                # Hesaplamalar gösterimi
                if target_amount > 0 and target_date:
                    days_remaining = (target_date - datetime.now().date()).days
                    months_remaining = max(1, days_remaining / 30)
                    monthly_target = target_amount / months_remaining
                    
                    st.markdown(f"""
                    **📊 Hesaplanan Değerler:**
                    - ⏳ Kalan süre: {days_remaining} gün ({months_remaining:.0f} ay)
                    - 💰 Aylık hedef: {monthly_target:,.0f} ₺
                    - 📅 Günlük hedef: {target_amount/days_remaining:,.0f} ₺
                    """)
            
            # Form gönder butonu
            if st.form_submit_button("🎯 Hedef Oluştur", type="primary", use_container_width=True):
                if goal_title and target_amount > 0:
                    if add_financial_goal(
                        goal_title, 
                        goal_type, 
                        target_amount, 
                        target_date.strftime('%Y-%m-%d'),
                        description
                    ):
                        st.success(f"✅ '{goal_title}' hedefi başarıyla oluşturuldu!")
                        # Form alanlarını temizle
                        for key in ['goal_title', 'goal_type', 'selected_template']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                    else:
                        st.error("❌ Hedef oluşturulurken hata oluştu!")
                else:
                    st.warning("⚠️ Lütfen tüm zorunlu alanları doldurun!")
    
    with tab3:  # Akıllı Öneriler
        st.markdown("### 💡 Akıllı Hedef Önerileri")
        
        # Mevcut mali durum analizi
        try:
            expenses = get_expenses(limit=100)
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Bu ay harcamaları
            this_month_expenses = [
                exp for exp in expenses 
                if datetime.strptime(exp[4], '%Y-%m-%d').month == current_month and 
                   datetime.strptime(exp[4], '%Y-%m-%d').year == current_year
            ]
            
            monthly_spending = sum(exp[1] for exp in this_month_expenses)
            
            # Genel öneriler
            st.markdown("#### 🎯 Kişiselleştirilmiş Hedef Önerileri")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🏠 Ev Alma Hedefi**
                - 2 yılda 500.000 ₺ biriktir
                - Aylık hedef: 20.833 ₺
                - Günlük hedef: 685 ₺
                """)
                
                if st.button("🏠 Bu hedefi oluştur", key="house_goal"):
                    if add_financial_goal(
                        "2 yılda 500.000 ₺ ev alma hedefi",
                        "housing",
                        500000,
                        (datetime.now().date() + timedelta(days=730)).strftime('%Y-%m-%d'),
                        "Ev peşinatı veya tam ödeme için 2 yıllık tasarruf planı"
                    ):
                        st.success("✅ Ev alma hedefi oluşturuldu!")
                        st.rerun()
                
                st.markdown("""
                **🛡️ Acil Durum Fonu**
                - 6 aylık gelirin %100'ü
                - Önerilen: 150.000 ₺
                - 12 ayda tamamla: 12.500 ₺/ay
                """)
                
                if st.button("🛡️ Bu hedefi oluştur", key="emergency_goal"):
                    if add_financial_goal(
                        "6 aylık gelirin %100'ü acil durum fonu",
                        "emergency",
                        150000,
                        (datetime.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
                        "Beklenmedik durumlar için güvenlik fonu"
                    ):
                        st.success("✅ Acil durum fonu hedefi oluşturuldu!")
                        st.rerun()
            
            with col2:
                st.markdown("""
                **👴 Emeklilik Planı**
                - 65 yaşında 2M ₺ biriktir
                - Uzun vadeli yatırım planı
                - Aylık katkı: değişken
                """)
                
                if st.button("👴 Bu hedefi oluştur", key="retirement_goal"):
                    # 65 yaşını 30 yıl sonra varsayalım
                    retirement_date = datetime.now().date() + timedelta(days=365*30)
                    if add_financial_goal(
                        "65 yaşında 2M ₺ emeklilik planı",
                        "retirement",
                        2000000,
                        retirement_date.strftime('%Y-%m-%d'),
                        "Rahat bir emeklilik için uzun vadeli tasarruf"
                    ):
                        st.success("✅ Emeklilik planı hedefi oluşturuldu!")
                        st.rerun()
                
                st.markdown("""
                **🚗 Otomobil Hedefi**
                - 18 ayda araba için 300.000 ₺
                - Aylık hedef: 16.667 ₺
                - Günlük hedef: 548 ₺
                """)
                
                if st.button("🚗 Bu hedefi oluştur", key="car_goal"):
                    if add_financial_goal(
                        "18 ayda araba için 300.000 ₺",
                        "vehicle",
                        300000,
                        (datetime.now().date() + timedelta(days=548)).strftime('%Y-%m-%d'),  # 18 ay
                        "Araba alımı için 18 aylık tasarruf planı"
                    ):
                        st.success("✅ Otomobil hedefi oluşturuldu!")
                        st.rerun()
            
            # Mali durum analizi
            st.markdown("---")
            st.markdown("#### 📊 Mali Durum Analizi")
            
            if monthly_spending > 0:
                # Tasarruf kapasitesi tahmini (basit hesaplama)
                estimated_income = monthly_spending * 1.5  # Basit tahmin
                potential_savings = estimated_income - monthly_spending
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "💰 Aylık Harcama",
                        f"{monthly_spending:,.0f} ₺"
                    )
                
                with col2:
                    st.metric(
                        "📈 Tahmini Gelir",
                        f"{estimated_income:,.0f} ₺"
                    )
                
                with col3:
                    st.metric(
                        "💎 Tasarruf Potansiyeli",
                        f"{potential_savings:,.0f} ₺"
                    )
                
                # Hedef önerileri
                st.markdown("#### 🎯 Size Özel Hedef Önerileri")
                
                # Potansiyel tasarrufa göre öneriler
                if potential_savings > 0:
                    recommendations = []
                    
                    # Acil durum fonu
                    emergency_months = max(3, min(6, int(potential_savings * 6 / monthly_spending)))
                    emergency_amount = monthly_spending * emergency_months
                    recommendations.append({
                        'title': f'{emergency_months} Aylık Acil Durum Fonu',
                        'amount': emergency_amount,
                        'months': max(6, emergency_months * 2),
                        'type': 'emergency',
                        'icon': '🛡️'
                    })
                    
                    # Yatırım hedefi
                    investment_amount = potential_savings * 12  # 1 yıllık tasarruf
                    recommendations.append({
                        'title': 'Yatırım Başlangıç Sermayesi',
                        'amount': investment_amount,
                        'months': 12,
                        'type': 'investment',
                        'icon': '📈'
                    })
                    
                    # Tatil fonu
                    vacation_amount = potential_savings * 6  # 6 aylık tatil fonu
                    recommendations.append({
                        'title': 'Premium Tatil Fonu',
                        'amount': vacation_amount,
                        'months': 8,
                        'type': 'vacation',
                        'icon': '✈️'
                    })
                    
                    for rec in recommendations:
                        monthly_target = rec['amount'] / rec['months']
                        
                        with st.container():
                            st.markdown(f"""
                            **{rec['icon']} {rec['title']}**
                            - 🎯 Hedef: {rec['amount']:,.0f} ₺
                            - ⏳ Süre: {rec['months']} ay
                            - 💰 Aylık: {monthly_target:,.0f} ₺
                            """)
                            
                            if st.button(f"{rec['icon']} Oluştur", key=f"rec_{rec['type']}"):
                                target_date = (datetime.now().date() + timedelta(days=rec['months']*30)).strftime('%Y-%m-%d')
                                if add_financial_goal(
                                    rec['title'],
                                    rec['type'],
                                    rec['amount'],
                                    target_date,
                                    f"Aylık {monthly_target:,.0f} ₺ tasarruf ile {rec['months']} ayda ulaşılabilir hedef"
                                ):
                                    st.success(f"✅ {rec['title']} hedefi oluşturuldu!")
                                    st.rerun()
                            
                            st.markdown("---")
                
                else:
                    st.warning("⚠️ Mevcut harcama seviyenizde tasarruf kapasitesi sınırlı görünüyor. Önce harcamalarınızı optimize etmeyi düşünün.")
            
            else:
                st.info("💡 Hedef önerileri için önce birkaç harcama kaydı eklemeniz gerekiyor.")
                
        except Exception as e:
            st.error(f"Analiz sırasında hata: {str(e)}")

elif page == "📋 Vergi Hesaplamaları":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">📋 Vergi Hesaplamaları</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Gelir vergisi, KDV ve yatırım kazançları vergi hesaplamaları</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Vergi modülü seçimi
    tax_module = st.selectbox(
        "📊 Vergi Hesaplama Türü Seçin:",
        ["💰 Gelir Vergisi", "📄 KDV İade Takibi", "📈 Yatırım Kazançları Vergisi", "💡 Vergi Optimizasyon Önerileri"],
        help="Hesaplamak istediğiniz vergi türünü seçin"
    )
    
    # Gelir Vergisi Hesaplama
    if tax_module == "💰 Gelir Vergisi":
        st.markdown("### 💰 Gelir Vergisi Hesaplama")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📊 Gelir Bilgileri")
            
            with st.form("income_tax_form"):
                annual_income = st.number_input(
                    "Yıllık Brüt Gelir (TL)",
                    min_value=0.0,
                    value=500000.0,
                    step=10000.0,
                    help="Yıllık brüt gelirinizi TL olarak girin"
                )
                
                tax_year = st.selectbox("Vergi Yılı", [2024, 2023], index=0)
                
                # İlave kesintiler
                st.markdown("##### 📋 İlave Kesintiler (İsteğe Bağlı)")
                pension_contribution = st.number_input(
                    "Bireysel Emeklilik Katkısı (TL/Yıl)",
                    min_value=0.0,
                    value=0.0,
                    help="Bireysel emeklilik sistemi katkı payı"
                )
                
                other_deductions = st.number_input(
                    "Diğer İndirimler (TL)",
                    min_value=0.0,
                    value=0.0,
                    help="Eğitim, sağlık, bağış vb. indirilebilir giderler"
                )
                
                calculate_btn = st.form_submit_button("🧮 Vergi Hesapla", type="primary")
        
        with col2:
            st.markdown("#### 📌 2024 Vergi Dilimleri")
            st.markdown("""
            **Türkiye Gelir Vergisi Dilimleri:**
            
            🟢 **0 - 110.000 TL** → %15
            🟡 **110.000 - 230.000 TL** → %20  
            🟠 **230.000 - 580.000 TL** → %27
            🔴 **580.000 - 3.000.000 TL** → %35
            ⚫ **3.000.000 TL +** → %40
            
            ℹ️ *Vergi hesaplamasında matrah esası kullanılır*
            """)
        
        if calculate_btn:
            # Vergi hesaplama işlemi
            try:
                # Basit vergi hesaplama (gerçek hesaplama için tax_calculator.py kullanılacak)
                taxable_income = annual_income - pension_contribution - other_deductions
                
                # Vergi dilimi hesaplama
                if taxable_income <= 110000:
                    tax = taxable_income * 0.15
                elif taxable_income <= 230000:
                    tax = 110000 * 0.15 + (taxable_income - 110000) * 0.20 - 5500
                elif taxable_income <= 580000:
                    tax = 110000 * 0.15 + 120000 * 0.20 + (taxable_income - 230000) * 0.27 - 21600
                elif taxable_income <= 3000000:
                    tax = 110000 * 0.15 + 120000 * 0.20 + 350000 * 0.27 + (taxable_income - 580000) * 0.35 - 68000
                else:
                    tax = 110000 * 0.15 + 120000 * 0.20 + 350000 * 0.27 + 2420000 * 0.35 + (taxable_income - 3000000) * 0.40 - 218000
                
                tax = max(0, tax)
                net_income = annual_income - tax
                effective_rate = (tax / annual_income * 100) if annual_income > 0 else 0
                
                # Sonuçları göster
                st.success("✅ Vergi hesaplaması tamamlandı!")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💰 Brüt Gelir", f"{annual_income:,.0f} ₺")
                
                with col2:
                    st.metric("💸 Hesaplanan Vergi", f"{tax:,.0f} ₺")
                
                with col3:
                    st.metric("💚 Net Gelir", f"{net_income:,.0f} ₺")
                
                with col4:
                    st.metric("📊 Efektif Vergi Oranı", f"%{effective_rate:.1f}")
                
                # Detaylı breakdown
                st.markdown("#### 📋 Hesaplama Detayları")
                
                breakdown_data = {
                    "Açıklama": [
                        "Yıllık Brüt Gelir",
                        "Bireysel Emeklilik Katkısı",
                        "Diğer İndirimler",
                        "Vergi Matrahı",
                        "Hesaplanan Gelir Vergisi",
                        "Net Yıllık Gelir",
                        "Aylık Net Gelir"
                    ],
                    "Tutar (TL)": [
                        f"{annual_income:,.0f}",
                        f"-{pension_contribution:,.0f}",
                        f"-{other_deductions:,.0f}",
                        f"{taxable_income:,.0f}",
                        f"-{tax:,.0f}",
                        f"{net_income:,.0f}",
                        f"{net_income/12:,.0f}"
                    ]
                }
                
                st.table(breakdown_data)
                
            except Exception as e:
                st.error(f"Hesaplama hatası: {str(e)}")
    
    # KDV İade Takibi
    elif tax_module == "📄 KDV İade Takibi":
        st.markdown("### 📄 KDV İade Takibi (Freelancer'lar İçin)")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("#### ➕ Yeni Fatura Ekle")
            
            with st.form("vat_invoice_form"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    invoice_number = st.text_input("Fatura No", placeholder="FT-2024-001")
                    client_name = st.text_input("Müşteri Adı", placeholder="ABC Şirketi")
                    invoice_date = st.date_input("Fatura Tarihi", value=datetime.now().date())
                
                with col_b:
                    invoice_amount = st.number_input("Fatura Tutarı (KDV Hariç)", min_value=0.0, step=100.0)
                    vat_rate = st.selectbox("KDV Oranı (%)", [18, 8, 1], index=0)
                    payment_status = st.selectbox("Ödeme Durumu", ["Beklemede", "Ödendi", "Gecikti"])
                
                vat_amount = invoice_amount * (vat_rate / 100)
                total_amount = invoice_amount + vat_amount
                
                st.info(f"💰 KDV Tutarı: {vat_amount:,.2f} ₺ | 💳 Toplam: {total_amount:,.2f} ₺")
                
                notes = st.text_area("Notlar", placeholder="İsteğe bağlı notlar...")
                
                add_invoice_btn = st.form_submit_button("📄 Fatura Ekle", type="primary")
        
        with col2:
            st.markdown("#### 📊 KDV Özeti")
            
            # Örnek veriler (gerçek uygulamada veritabanından gelecek)
            sample_invoices = [
                {"no": "FT-2024-001", "client": "ABC Şirketi", "amount": 10000, "vat": 1800, "status": "Ödendi"},
                {"no": "FT-2024-002", "client": "XYZ Ltd", "amount": 15000, "vat": 2700, "status": "Beklemede"},
                {"no": "FT-2024-003", "client": "DEF AŞ", "amount": 8000, "vat": 1440, "status": "Ödendi"},
            ]
            
            total_vat_paid = sum([inv["vat"] for inv in sample_invoices if inv["status"] == "Ödendi"])
            pending_vat = sum([inv["vat"] for inv in sample_invoices if inv["status"] == "Beklemede"])
            
            st.metric("💳 Ödenen KDV", f"{total_vat_paid:,.0f} ₺")
            st.metric("⏳ Bekleyen KDV", f"{pending_vat:,.0f} ₺")
            st.metric("📋 Toplam Fatura", f"{len(sample_invoices)} adet")
            
            if total_vat_paid >= 200:
                st.success("✅ İade için yeterli tutar!")
                st.button("🔄 İade Başvurusu Yap", type="primary")
            else:
                st.warning(f"⚠️ İade için en az 200 ₺ gerekli\n(Kalan: {200-total_vat_paid:,.0f} ₺)")
        
        # Fatura listesi
        st.markdown("#### 📋 Mevcut Faturalar")
        
        if sample_invoices:
            invoice_df = pd.DataFrame(sample_invoices)
            invoice_df.columns = ["Fatura No", "Müşteri", "Tutar (₺)", "KDV (₺)", "Durum"]
            st.dataframe(invoice_df, use_container_width=True)
        else:
            st.info("📝 Henüz fatura kaydı bulunmuyor. Yukarıdaki formu kullanarak fatura ekleyebilirsiniz.")
    
    # Yatırım Kazançları Vergisi
    elif tax_module == "📈 Yatırım Kazançları Vergisi":
        st.markdown("### 📈 Yatırım Kazançları Vergi Hesaplama")
        
        with st.form("investment_tax_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Yatırım Bilgileri")
                investment_type = st.selectbox(
                    "Yatırım Türü",
                    ["Hisse Senedi", "Tahvil", "Döviz", "Kripto Para", "Gayrimenkul", "Altın"],
                    help="Yatırım türünü seçin"
                )
                
                purchase_amount = st.number_input("Alış Tutarı (₺)", min_value=0.0, step=1000.0)
                sale_amount = st.number_input("Satış Tutarı (₺)", min_value=0.0, step=1000.0)
                
                purchase_date = st.date_input("Alış Tarihi", value=datetime.now().date() - timedelta(days=365))
                sale_date = st.date_input("Satış Tarihi", value=datetime.now().date())
            
            with col2:
                st.markdown("#### 📋 Vergi Kuralları")
                
                if investment_type == "Hisse Senedi":
                    st.info("""
                    **Hisse Senedi Vergi Kuralları:**
                    - 2 yıl üzeri elde tutma: Vergisiz
                    - 2 yıl altı: %0 (2024 muafiyeti)
                    """)
                elif investment_type == "Gayrimenkul":
                    st.info("""
                    **Gayrimenkul Vergi Kuralları:**
                    - 5 yıl üzeri elde tutma: Vergisiz
                    - 5 yıl altı: %20 vergi
                    """)
                elif investment_type == "Tahvil":
                    st.info("""
                    **Tahvil Vergi Kuralları:**
                    - Kazanç üzerinden %10 stopaj
                    """)
                else:
                    st.info("""
                    **Diğer Yatırımlar:**
                    - Mevzuat belirsizliği var
                    - Vergi danışmanına başvurun
                    """)
            
            calculate_investment_tax = st.form_submit_button("🧮 Vergi Hesapla", type="primary")
        
        if calculate_investment_tax and purchase_amount > 0:
            gain_loss = sale_amount - purchase_amount
            holding_period = (sale_date - purchase_date).days
            
            # Vergi hesaplama
            tax_rate = 0
            is_exempt = False
            exemption_reason = ""
            
            if investment_type == "Hisse Senedi":
                if holding_period >= 730:
                    is_exempt = True
                    exemption_reason = "2 yıl üzeri elde tutma muafiyeti"
                tax_rate = 0
            elif investment_type == "Gayrimenkul":
                if holding_period >= 1825:
                    is_exempt = True
                    exemption_reason = "5 yıl üzeri elde tutma muafiyeti"
                else:
                    tax_rate = 20
            elif investment_type == "Tahvil":
                tax_rate = 10
            
            if gain_loss <= 0:
                is_exempt = True
                exemption_reason = "Zarar nedeniyle vergi yükümlülüğü yok"
            
            tax_amount = 0 if is_exempt else max(0, gain_loss * tax_rate / 100)
            net_gain = gain_loss - tax_amount
            
            # Sonuçları göster
            st.success("✅ Yatırım vergisi hesaplaması tamamlandı!")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Alış Tutarı", f"{purchase_amount:,.0f} ₺")
            
            with col2:
                st.metric("💰 Satış Tutarı", f"{sale_amount:,.0f} ₺")
            
            with col3:
                color = "normal" if gain_loss >= 0 else "inverse"
                st.metric("📊 Kazanç/Zarar", f"{gain_loss:,.0f} ₺", delta=f"{gain_loss:,.0f} ₺")
            
            with col4:
                st.metric("📅 Elde Tutma", f"{holding_period} gün")
            
            # Vergi detayları
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Vergi Oranı", f"%{tax_rate}")
            
            with col2:
                st.metric("💸 Vergi Tutarı", f"{tax_amount:,.0f} ₺")
            
            with col3:
                st.metric("💚 Net Kazanç", f"{net_gain:,.0f} ₺")
            
            # Muafiyet durumu
            if is_exempt:
                st.success(f"🎉 Vergi Muafiyeti: {exemption_reason}")
            elif tax_amount > 0:
                st.warning(f"⚠️ {tax_amount:,.0f} ₺ vergi ödemeniz gerekiyor")
    
    # Vergi Optimizasyon Önerileri
    elif tax_module == "💡 Vergi Optimizasyon Önerileri":
        st.markdown("### 💡 Vergi Optimizasyon Önerileri")
        
        # Kullanıcı profili
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Kişisel Bilgiler")
            annual_income_opt = st.number_input("Yıllık Gelir (₺)", min_value=0.0, value=500000.0, step=10000.0)
            is_freelancer = st.checkbox("Freelancer/Serbest Meslek")
            has_investments = st.checkbox("Yatırımlarım var")
            has_real_estate = st.checkbox("Gayrimenkul yatırımım var")
        
        with col2:
            st.markdown("#### 🎯 İlgi Alanları")
            interested_pension = st.checkbox("Bireysel emeklilik sistemi", value=True)
            interested_education = st.checkbox("Eğitim harcamaları")
            interested_health = st.checkbox("Sağlık harcamaları")
            interested_donation = st.checkbox("Bağış ve yardımlar")
        
        if st.button("💡 Önerileri Getir", type="primary"):
            st.markdown("#### 🚀 Kişiselleştirilmiş Vergi Optimizasyon Önerileri")
            
            recommendations = []
            
            # Gelir seviyesine göre öneriler
            if annual_income_opt > 100000:
                if interested_pension:
                    max_pension = min(annual_income_opt * 0.1, 67200)  # 2024 limiti
                    tax_saving = max_pension * 0.2  # Ortalama vergi dilimi
                    recommendations.append({
                        "title": "🏦 Bireysel Emeklilik Sistemi",
                        "priority": "Yüksek",
                        "savings": tax_saving,
                        "description": f"Yıllık {max_pension:,.0f} ₺'ye kadar BES katkısı ile {tax_saving:,.0f} ₺ vergi tasarrufu",
                        "action": "BES planı araştırın ve otomatik ödeme başlatın"
                    })
            
            if has_investments:
                recommendations.append({
                    "title": "📈 Yatırım Vergi Planlaması",
                    "priority": "Orta",
                    "savings": 0,
                    "description": "Hisse senetlerini 2 yıl elde tutarak vergi muafiyeti sağlayın",
                    "action": "Satış zamanlamasını vergi muafiyet sürelerine göre planlayın"
                })
            
            if is_freelancer:
                recommendations.append({
                    "title": "📄 KDV İade Optimizasyonu",
                    "priority": "Yüksek",
                    "savings": 0,
                    "description": "Düzenli KDV iade başvurusu ile nakit akışını iyileştirin",
                    "action": "Aylık KDV iade takvimine uyun"
                })
            
            if interested_education:
                recommendations.append({
                    "title": "📚 Eğitim Harcama İndirimi",
                    "priority": "Orta",
                    "savings": 2000,
                    "description": "Eğitim harcamalarınızı belgelendirerek matrahtan düşürün",
                    "action": "Kurs, sertifika ve eğitim faturalarını saklayın"
                })
            
            if interested_health:
                recommendations.append({
                    "title": "🏥 Sağlık Harcama İndirimi",
                    "priority": "Orta",
                    "savings": 1500,
                    "description": "Sağlık giderlerinizi vergi beyannamesinde beyan edin",
                    "action": "Hastane, doktor ve ilaç faturalarını muhafaza edin"
                })
            
            # Önerileri görüntüle
            for i, rec in enumerate(recommendations):
                priority_color = {"Yüksek": "🔴", "Orta": "🟡", "Düşük": "🟢"}
                priority_icon = priority_color.get(rec["priority"], "🟢")
                
                with st.expander(f"{priority_icon} {rec['title']} - {rec['priority']} Öncelik"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(rec["description"])
                        st.info(f"💡 **Yapılacaklar:** {rec['action']}")
                    
                    with col2:
                        if rec["savings"] > 0:
                            st.metric("Tahmini Tasarruf", f"{rec['savings']:,.0f} ₺")
                        else:
                            st.metric("Fayda", "Nakit Akışı")
            
            # Genel tavsiyeler
            st.markdown("#### 📋 Genel Vergi Tavsiyeleri")
            
            general_tips = [
                "📅 Vergi ödemelerinizi zamanında yaparak gecikme faizi ödemekten kaçının",
                "📊 Yıllık vergi planlaması yaparak ani vergi yüklerini önleyin",
                "💼 Vergi danışmanı ile düzenli görüşmeler planlayın",
                "📱 E-beyanname sistemi ile işlemlerinizi dijital ortamda yürütün",
                "🧾 Tüm harcama belgelerinizi düzenli olarak kayıt altına alın",
                "⏰ Vergi takvimini takip ederek beyanname ve ödeme sürelerini kaçırmayın"
            ]
            
            for tip in general_tips:
                st.markdown(f"• {tip}")

elif page == "🤖 AI Asistan":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">🤖 NeoFinX AI Asistan</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; text-align: center;">Finansal sorularınızı sorun, akıllı öneriler alın</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat geçmişini session state'te sakla
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Kullanıcı verilerini al
    user_data = get_user_spending_summary()
    
    # Hoş geldin mesajı
    if not st.session_state.chat_history:
        welcome_msg = "🤖 Merhaba! Ben NeoFinX AI asistanınızım. Size finansal konularda yardımcı olabilirim."
        if user_data and user_data['total_expenses'] > 0:
            welcome_msg += f"\n\n📊 Hızlı bilgi: Bu ay {user_data['this_month_total']:,.0f} ₺ harcamanız var ve toplam {user_data['total_expenses']} adet kayıt bulunuyor."
        welcome_msg += "\n\n💡 **Örnek sorular:**\n• Harcamalarım nasıl?\n• Bütçe önerisi ver\n• Tasarruf ipuçları\n• NeoFinX özellikleri neler?"
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'message': welcome_msg,
            'timestamp': datetime.now()
        })
    
    # Chat konteyneri
    chat_container = st.container()
    
    with chat_container:
        # Chat geçmişini göster
        for i, chat in enumerate(st.session_state.chat_history):
            if chat['role'] == 'user':
                # Kullanıcı mesajı - sağ tarafta
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                    <div style="
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        padding: 12px 16px;
                        border-radius: 18px 18px 4px 18px;
                        max-width: 70%;
                        word-wrap: break-word;
                        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                    ">
                        <div style="font-size: 14px;">{chat['message']}</div>
                        <div style="font-size: 10px; opacity: 0.8; margin-top: 4px;">
                            {chat['timestamp'].strftime('%H:%M')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                # AI mesajı - sol tarafta
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 1rem 0;">
                    <div style="
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        color: #1e293b;
                        padding: 12px 16px;
                        border-radius: 18px 18px 18px 4px;
                        max-width: 70%;
                        word-wrap: break-word;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    ">
                        <div style="font-size: 14px; white-space: pre-line;">{chat['message']}</div>
                        <div style="font-size: 10px; opacity: 0.6; margin-top: 4px;">
                            🤖 AI • {chat['timestamp'].strftime('%H:%M')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Kullanıcı input alanı
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "💬 Mesajınızı yazın:",
            placeholder="Örn: Harcamalarım nasıl? Bütçe önerisi ver...",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("📤 Gönder", type="primary", use_container_width=True)
    
    # Mesaj gönderildiğinde
    if send_button and user_input.strip():
        # Kullanıcı mesajını ekle
        st.session_state.chat_history.append({
            'role': 'user',
            'message': user_input.strip(),
            'timestamp': datetime.now()
        })
        
        # AI yanıtını üret
        ai_response = generate_chatbot_response(user_input.strip(), user_data)
        
        # AI yanıtını ekle
        st.session_state.chat_history.append({
            'role': 'assistant',
            'message': ai_response,
            'timestamp': datetime.now()
        })
        
        # Sayfayı yenile
        st.rerun()
    
    # Hızlı sorular
    st.markdown("### 🚀 Hızlı Sorular")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Harcamalarım", use_container_width=True):
            st.session_state.chat_history.append({
                'role': 'user',
                'message': 'Harcamalarım nasıl?',
                'timestamp': datetime.now()
            })
            ai_response = generate_chatbot_response('harcama', user_data)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'message': ai_response,
                'timestamp': datetime.now()
            })
            st.rerun()
    
    with col2:
        if st.button("📊 Bütçe Önerisi", use_container_width=True):
            st.session_state.chat_history.append({
                'role': 'user',
                'message': 'Bütçe önerisi ver',
                'timestamp': datetime.now()
            })
            ai_response = generate_chatbot_response('bütçe', user_data)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'message': ai_response,
                'timestamp': datetime.now()
            })
            st.rerun()
    
    with col3:
        if st.button("💡 Tasarruf İpuçları", use_container_width=True):
            st.session_state.chat_history.append({
                'role': 'user',
                'message': 'Tasarruf ipuçları ver',
                'timestamp': datetime.now()
            })
            ai_response = generate_chatbot_response('tasarruf', user_data)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'message': ai_response,
                'timestamp': datetime.now()
            })
            st.rerun()
    
    # Chat'i temizle butonu
    st.markdown("---")
    if st.button("🗑️ Chat Geçmişini Temizle", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*NeoFinX 2024 - Yapay zeka destekli akilli butce asistani*")

# Veritabanı durumu




def get_expense_count():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM expenses')
        return cursor.fetchone()[0]
    except:
        return 0
    finally:
        if conn:
            conn.close()

expense_count = get_expense_count()
st.sidebar.markdown("---")
st.sidebar.info(f"📊 Veritabanında {expense_count} harcama kaydı var")
