import streamlit as st

def apply_premium_style():
    """
    Applies custom CSS to create a premium, modern, and high-fidelity dashboard.
    Features:
    - Custom modern typography (Outfit and Inter from Google Fonts)
    - Dark-mode glassmorphic cards
    - Subtle transitions and hover animations
    - High contrast gradient text and headers
    - Sleek buttons and clean sidebars
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

        /* Global Font and Theme Overrides */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', sans-serif;
            background-color: #0f111a;
            color: #e2e8f0;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
        }

        /* Glassmorphism Containers */
        .glass-card {
            background: rgba(22, 28, 45, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
        }

        /* Gradient Text */
        .gradient-text {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Outfit', sans-serif;
        }

        .gradient-header {
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Metrics Widget Styling */
        .metric-container {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-container:hover {
            background: rgba(30, 41, 59, 0.7);
            border-color: rgba(99, 102, 241, 0.3);
        }

        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            color: #ffffff;
            margin: 4px 0;
        }

        .metric-label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .metric-delta {
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 4px;
        }
        
        .delta-up {
            color: #10b981;
        }
        
        .delta-down {
            color: #ef4444;
        }

        /* Custom Status Badge */
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-good {
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        .status-warning {
            background-color: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        
        .status-danger {
            background-color: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        /* Sidebar Styling Customizations */
        [data-testid="stSidebar"] {
            background-color: #0b0d14;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        [data-testid="stSidebar"] .stMarkdown h2 {
            color: #ffffff;
            font-size: 1.4rem;
            border-bottom: 2px solid rgba(99, 102, 241, 0.2);
            padding-bottom: 8px;
            margin-bottom: 20px;
        }

        /* Navigation Cards */
        .nav-card {
            background: linear-gradient(135deg, rgba(22, 28, 45, 0.6) 0%, rgba(15, 18, 30, 0.8) 100%);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }

        .nav-card:hover {
            transform: scale(1.02);
            border-color: rgba(168, 85, 247, 0.4);
            box-shadow: 0 10px 30px rgba(168, 85, 247, 0.1);
        }

        .nav-icon {
            font-size: 2.5rem;
            margin-bottom: 12px;
        }

        .nav-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 8px;
            font-family: 'Outfit', sans-serif;
        }

        .nav-desc {
            font-size: 0.9rem;
            color: #94a3b8;
            line-height: 1.4;
        }
        
        /* Tooltip and clean visual lines */
        hr {
            border: 0;
            height: 1px;
            background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0));
            margin: 2rem 0;
        }
        
        .footer-text {
            text-align: center;
            color: #64748b;
            font-size: 0.8rem;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header(title: str, subtitle: str = None):
    """
    Renders a premium visual header with gradient accenting.
    """
    apply_premium_style()
    st.markdown(f'<h1 class="gradient-header">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p style="color: #94a3b8; font-size: 1.15rem; margin-top: -10px; margin-bottom: 25px;">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def render_footer():
    """
    Renders the platform footer text.
    """
    st.markdown(
        '<div class="footer-text">🚦 Urban Traffic Analytics & Forecasting Platform • Deployed Environment • Priya Shah Capstone</div>',
        unsafe_allow_html=True
    )

def render_metric_card(label: str, value: str, delta: str = None, delta_direction: str = "up"):
    """
    Renders a custom styled metric card component.
    delta_direction can be "up" (green) or "down" (red).
    """
    delta_class = "delta-up" if delta_direction == "up" else "delta-down"
    delta_symbol = "▲" if delta_direction == "up" else "▼"
    
    delta_html = f'<div class="metric-delta {delta_class}">{delta_symbol} {delta}</div>' if delta else ''
    
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_glass_card(title: str, content: str, icon: str = "⚡"):
    """
    Renders a card with glassmorphism styles.
    """
    st.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size: 1.5rem; margin-bottom: 8px;">{icon} <span style="font-family: 'Outfit'; font-weight: 700; color: #ffffff; font-size: 1.25rem;">{title}</span></div>
            <div style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_navigation_card(title: str, description: str, icon: str, page_name: str):
    """
    Renders a navigation link card that guides users to another page.
    """
    st.markdown(
        f"""
        <div class="nav-card">
            <div>
                <div class="nav-icon">{icon}</div>
                <div class="nav-title">{title}</div>
                <div class="nav-desc">{description}</div>
            </div>
            <div style="margin-top: 15px; font-size: 0.85rem; font-weight: 600; color: #a855f7;">
                Navigate via Sidebar Menu →
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_status_badge(label: str, status_type: str = "good"):
    """
    Returns HTML string for a styled status badge.
    status_type: "good", "warning", "danger"
    """
    badge_class = f"status-{status_type}"
    return f'<span class="status-badge {badge_class}">{label}</span>'
