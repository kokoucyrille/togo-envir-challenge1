"""Constantes de thème et styles partagés par toutes les pages du tableau de bord."""

GREEN = "#145C43"
GREEN_DARK = "#0D3F2E"
GREEN_LIGHT = "#E7F1EC"
GOLD = "#F2B705"
GOLD_DARK = "#C99A04"
RED = "#C8102E"
RED_LIGHT = "#FBE6E9"
GREY = "#5B6660"
GREY_LIGHT = "#F4F6F5"
INK = "#182420"
BORDER = "#DEE5E1"

SEGMENT_COLORS = {
    "Nouveaux ouvrages prioritaires": RED,
    "Maintenance et renforcement urgents": GOLD_DARK,
    "Renforcement (vulnerabilite aux inondations)": "#2C6E8E",
    "Surveillance": GREEN,
}

SEGMENT_SHORT_LABELS = {
    "Nouveaux ouvrages prioritaires": "Nouveaux ouvrages",
    "Maintenance et renforcement urgents": "Maintenance urgente",
    "Renforcement (vulnerabilite aux inondations)": "Renforcement (inondation)",
    "Surveillance": "Surveillance",
}

REGION_COLORS = {
    "Maritime": "#145C43",
    "Plateaux": "#2C6E8E",
    "Centrale": "#C99A04",
    "Kara": "#A34A28",
    "Savanes": "#7A3B8C",
}

CONTINUOUS_SCALE_RISK = "YlOrRd"
CONTINUOUS_SCALE_POP = "Greens"
CONTINUOUS_SCALE_PRIORITY = "OrRd"

PLOTLY_TEMPLATE = "plotly_white"

BASE_CSS = f"""
<style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}

    html, body, [class*="css"] {{
        font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    }}

    .block-container {{
        padding-top: 1.1rem;
        padding-bottom: 2.5rem;
        max-width: 1250px;
    }}

    .block-container p, .block-container li {{
        line-height: 1.6;
    }}

    /* ---------- Repère de position (fil d'Ariane) ---------- */
    .breadcrumb {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {GREY};
        letter-spacing: 0.2px;
        margin: -14px 0 18px 2px;
    }}
    .breadcrumb-sep {{
        color: {GOLD_DARK};
        font-weight: 700;
        margin: 0 6px;
    }}

    /* ---------- Boîte « mode d'emploi » (navigation), distincte des constats ---------- */
    .guide-box {{
        background: #FFFBEF;
        border: 1px solid {GOLD};
        border-left: 4px solid {GOLD_DARK};
        border-radius: 8px;
        padding: 14px 18px;
        font-size: 0.86rem;
        color: {INK};
        margin: 10px 0 18px 0;
    }}
    .guide-box b {{ color: {GREEN_DARK}; }}
    .guide-box ol, .guide-box ul {{ margin: 6px 0 0 0; padding-left: 20px; }}
    .guide-box li {{ margin-bottom: 3px; }}

    /* ---------- Étiquette de sous-groupe de KPI ---------- */
    .kpi-group-label {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {GREY};
        margin: 4px 0 8px 2px;
    }}

    .app-header {{
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 14px 22px;
        background: linear-gradient(90deg, {GREEN_DARK} 0%, {GREEN} 100%);
        border-radius: 10px;
        margin-bottom: 22px;
    }}
    .app-header img {{
        height: 58px;
        background: white;
        border-radius: 50%;
        padding: 3px;
    }}
    .app-header .titles h1 {{
        color: white;
        font-size: 1.32rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 0.2px;
    }}
    .app-header .titles p {{
        color: {GOLD};
        margin: 2px 0 0 0;
        font-size: 0.85rem;
        font-weight: 500;
    }}

    .section-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {GREEN_DARK};
        border-left: 5px solid {GOLD};
        padding-left: 10px;
        margin: 6px 0 14px 0;
    }}

    .kpi-card {{
        background: white;
        border: 1px solid {BORDER};
        border-left: 4px solid {GREEN};
        border-radius: 8px;
        padding: 14px 16px;
        height: 100%;
    }}
    .kpi-top-row {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 8px;
    }}
    .kpi-card .kpi-label {{
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        color: {GREY};
        font-weight: 600;
        margin-bottom: 6px;
    }}
    .kpi-icon {{
        width: 20px;
        height: 20px;
        min-width: 20px;
        color: {GREEN};
        opacity: 0.55;
    }}
    .kpi-card.gold .kpi-icon {{ color: {GOLD_DARK}; }}
    .kpi-card.red .kpi-icon {{ color: {RED}; }}
    .kpi-card.grey .kpi-icon {{ color: {GREY}; }}
    .kpi-card .kpi-value {{
        font-size: 1.55rem;
        font-weight: 800;
        color: {INK};
        line-height: 1.1;
    }}
    .kpi-card .kpi-sub {{
        font-size: 0.75rem;
        color: {GREY};
        margin-top: 4px;
    }}
    .kpi-card.gold {{ border-left-color: {GOLD}; }}
    .kpi-card.red {{ border-left-color: {RED}; }}
    .kpi-card.grey {{ border-left-color: {GREY}; }}

    .note-box {{
        background: {GREEN_LIGHT};
        border: 1px solid {GREEN};
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.87rem;
        color: {GREEN_DARK};
        margin: 10px 0;
    }}
    .warn-box {{
        background: {RED_LIGHT};
        border: 1px solid {RED};
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.87rem;
        color: #7A0C1F;
        margin: 10px 0;
    }}

    .rec-card {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }}
    .rec-card .rec-title {{
        font-weight: 700;
        color: {GREEN_DARK};
        font-size: 0.98rem;
        margin-bottom: 4px;
    }}
    .rec-tag {{
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 2px 9px;
        border-radius: 12px;
        margin-bottom: 8px;
    }}
    .rec-tag.haute {{ background: {RED_LIGHT}; color: {RED}; }}
    .rec-tag.moyenne {{ background: #FFF4DC; color: {GOLD_DARK}; }}

    div[data-testid="stMetric"] {{
        background: white;
        border: 1px solid {BORDER};
        border-left: 4px solid {GREEN};
        border-radius: 8px;
        padding: 10px 14px;
    }}

    .footer-note {{
        text-align: center;
        color: {GREY};
        font-size: 0.75rem;
        margin-top: 30px;
        padding-top: 14px;
        border-top: 1px solid {BORDER};
    }}

    /* ---------- Navigation latérale ---------- */
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 0.9rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 0.8rem;
    }}
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
        gap: 0.3rem;
    }}
    section[data-testid="stSidebar"] hr.sidebar-divider {{
        margin: 0.7rem 0 0.6rem 0;
        border-color: {BORDER};
    }}

    /* Bloc identité (logo + nom), compact et sur une seule ligne */
    .sidebar-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 2px 2px 0 2px;
    }}
    .sidebar-brand-logo {{
        width: 42px;
        height: 42px;
        min-width: 42px;
        border-radius: 50%;
        background: white;
        padding: 3px;
        border: 1px solid {BORDER};
    }}
    .sidebar-brand-title {{
        font-weight: 700;
        color: {GREEN_DARK};
        font-size: 0.84rem;
        line-height: 1.2;
    }}
    .sidebar-brand-sub {{
        color: {GREY};
        font-size: 0.66rem;
        line-height: 1.25;
        margin-top: 1px;
    }}

    /* Bascule de langue : espacement net entre l'étiquette et les boutons */
    .lang-toggle-wrap {{
        margin-top: 10px;
    }}
    .lang-toggle-label {{
        text-align: center;
        font-size: 0.66rem;
        color: {GREY};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        margin-bottom: 8px;
    }}

    /* Bloc de navigation : groupes resserrés, tenant sans ascenseur */
    .nav-block {{
        margin-top: 4px;
    }}
    .nav-group-title {{
        font-size: 0.66rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: {GREY};
        margin: 0 4px 4px 4px;
        padding-left: 9px;
        border-left: 3px solid transparent;
        transition: color 0.15s ease-in-out, border-color 0.15s ease-in-out;
    }}
    .nav-group-title-spaced {{
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid {BORDER};
    }}
    .nav-group-title-active {{
        color: {GREEN_DARK};
        border-left-color: {GOLD};
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        text-align: left;
        justify-content: flex-start;
        border-radius: 7px;
        padding: 7px 12px;
        font-size: 0.82rem;
        font-weight: 600;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        transition: all 0.15s ease-in-out;
        border: 1px solid transparent;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button p {{
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: inherit;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button [data-testid="stIconMaterial"] {{
        font-size: 1.05rem;
        opacity: 0.85;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        border-color: {GOLD};
        transform: translateX(2px);
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"][kind="secondary"] > button {{
        background: transparent;
        color: {INK};
    }}
    .badge-count {{
        display: inline-block;
        background: {GOLD};
        color: {GREEN_DARK};
        font-size: 0.68rem;
        font-weight: 800;
        border-radius: 10px;
        padding: 1px 8px;
        margin-left: 6px;
    }}

    /* Filet de sécurité : sur les très petits écrans où le contenu de la barre
       latérale dépasserait malgré la mise en page compacte, l'ascenseur reste
       fin et discret plutôt que la barre épaisse par défaut du navigateur. */
    section[data-testid="stSidebar"] > div {{
        scrollbar-width: thin;
        scrollbar-color: {BORDER} transparent;
    }}
    section[data-testid="stSidebar"] > div::-webkit-scrollbar {{
        width: 5px;
    }}
    section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {{
        background: {BORDER};
        border-radius: 4px;
    }}

    /* ---------- Filtres ---------- */
    .filter-summary {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
        margin-bottom: 4px;
    }}
    .filter-chip {{
        display: inline-block;
        background: {GREEN_LIGHT};
        color: {GREEN_DARK};
        border: 1px solid {GREEN};
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 12px;
        padding: 3px 10px;
        white-space: nowrap;
    }}
    .filter-chip.neutral {{
        background: {GREY_LIGHT};
        color: {GREY};
        border-color: {BORDER};
    }}
    div[data-testid="stExpander"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 700;
        color: {GREEN_DARK};
    }}

    /* ---------- Boutons généraux ---------- */
    div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button {{
        border-radius: 8px;
        transition: all 0.15s ease-in-out;
    }}
    div[data-testid="stButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(20, 92, 67, 0.18);
    }}

    /* ---------- Cartes : léger relief au survol ---------- */
    .kpi-card, .rec-card {{
        transition: box-shadow 0.15s ease-in-out, transform 0.15s ease-in-out;
    }}
    .kpi-card:hover, .rec-card:hover {{
        box-shadow: 0 4px 12px rgba(24, 36, 32, 0.10);
        transform: translateY(-1px);
    }}

    /* ---------- Tableaux ---------- */
    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 8px;
        overflow: hidden;
    }}

    /* ---------- Accessibilité : focus clavier visible ---------- */
    div[data-testid="stButton"] > button:focus-visible,
    div[data-testid="stDownloadButton"] > button:focus-visible {{
        outline: 2px solid {GOLD_DARK};
        outline-offset: 1px;
    }}

    /* ---------- Responsive (mobile) ---------- */
    @media (max-width: 640px) {{
        .app-header {{ flex-direction: column; align-items: flex-start; gap: 8px; padding: 12px 16px; }}
        .app-header .titles h1 {{ font-size: 1.05rem; }}
        .kpi-card .kpi-value {{ font-size: 1.25rem; }}
        .breadcrumb {{ margin-top: -8px; }}
        div[data-testid="stHorizontalBlock"] {{ flex-wrap: wrap; }}
    }}
</style>
"""
