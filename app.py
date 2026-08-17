import streamlit as st

from components import inject_base_style, page_header, breadcrumb, footer_note, sidebar_brand, sidebar_nav
from filters import render_global_filters, get_default_state
from data_loader import logo_path
from i18n import t

st.set_page_config(
    page_title="Eau Potable Togo — Tableau de bord",
    page_icon=logo_path(),
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_base_style()

from views import accueil, carte, pression, inondation, coso, priorisation, territoires, methodologie, apropos

# La langue doit être sélectionnée avant de construire les libellés traduits ci-dessous.
with st.sidebar:
    sidebar_brand()

# (clé interne, module, titre affiché, sous-titre, a_besoin_de_filtres, icône Material)
PAGE_DEFS = [
    ("overview", accueil,
     t("Vue d'ensemble", "Overview"),
     t("Indicateurs clés et carte de synthèse", "Key indicators and summary map"),
     True, "dashboard"),
    ("map", carte,
     t("Cartographie", "Map"),
     t("Risque d'inondation, population et ouvrages hydrauliques", "Flood risk, population and water infrastructure"),
     True, "map"),
    ("pressure", pression,
     t("Pression démographique", "Demographic pressure"),
     t("Population rapportée aux ouvrages documentés", "Population relative to documented infrastructure"),
     True, "groups"),
    ("flood", inondation,
     t("Risque d'inondation", "Flood risk"),
     t("Exposition des ouvrages au risque d'inondation", "Infrastructure exposure to flood risk"),
     True, "warning"),
    ("coso", coso,
     t("Projets COSO", "COSO projects"),
     t("Suivi des sous-projets et risque de retard", "Sub-project monitoring and delay risk"),
     True, "construction"),
    ("priority", priorisation,
     t("Priorisation", "Prioritization"),
     t("Water Infrastructure Priority Score et plan d'action", "Water Infrastructure Priority Score and action plan"),
     True, "flag"),
    ("territories", territoires,
     t("Territoires", "Territories"),
     t("Regroupement territorial complémentaire", "Complementary territorial clustering"),
     True, "layers"),
    ("methodology", methodologie,
     t("Méthodologie", "Methodology"),
     t("Sources, méthode et limites du diagnostic", "Sources, method and limitations of the diagnosis"),
     False, "menu_book"),
    ("about", apropos,
     t("À propos", "About"),
     t("Auteur et contexte du projet", "Author and project context"),
     False, "info"),
]
PAGES = {key: (module, subtitle, needs_filters) for key, module, _, subtitle, needs_filters, _ in PAGE_DEFS}
LABELS = {key: label for key, _, label, _, _, _ in PAGE_DEFS}
ICONS = {key: icon for key, _, _, _, _, icon in PAGE_DEFS}

NAV_GROUPS = [
    (t("Diagnostic", "Diagnosis"), ["overview", "map", "pressure", "flood", "coso"]),
    (t("Décision", "Decision"), ["priority", "territories"]),
    (t("Ressources", "Resources"), ["methodology", "about"]),
]
GROUP_OF_PAGE = {key: group_title for group_title, keys in NAV_GROUPS for key in keys}

with st.sidebar:
    st.markdown('<hr class="sidebar-divider" />', unsafe_allow_html=True)
    default_page_key = st.session_state.get("page_key", PAGE_DEFS[0][0])
    page_key = sidebar_nav(
        [(title, [(k, LABELS[k], ICONS[k]) for k in keys]) for title, keys in NAV_GROUPS],
        default_page_key,
    )

module, subtitle, needs_filters = PAGES[page_key]

page_header(
    t(
        "Diagnostic et priorisation de l'accès à l'eau potable au Togo",
        "Diagnosis and prioritization of drinking water access in Togo",
    ),
    subtitle,
)
breadcrumb(GROUP_OF_PAGE.get(page_key, ""), LABELS[page_key])

if needs_filters:
    state = render_global_filters()
else:
    state = get_default_state()

module.render(state)

footer_note()
