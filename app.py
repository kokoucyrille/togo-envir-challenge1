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

# (clé interne, module, titre affiché, sous-titre, a_besoin_de_filtres)
PAGE_DEFS = [
    ("overview", accueil,
     t("01 · Vue d'ensemble", "01 · Overview"),
     t("Indicateurs clés et carte de synthèse", "Key indicators and summary map"),
     True),
    ("map", carte,
     t("02 · Cartographie", "02 · Map"),
     t("Risque d'inondation, population et ouvrages hydrauliques", "Flood risk, population and water infrastructure"),
     True),
    ("pressure", pression,
     t("03 · Pression démographique", "03 · Demographic pressure"),
     t("Population rapportée aux ouvrages documentés", "Population relative to documented infrastructure"),
     True),
    ("flood", inondation,
     t("04 · Risque d'inondation", "04 · Flood risk"),
     t("Exposition des ouvrages au risque d'inondation", "Infrastructure exposure to flood risk"),
     True),
    ("coso", coso,
     t("05 · Projets COSO", "05 · COSO projects"),
     t("Suivi des sous-projets et risque de retard", "Sub-project monitoring and delay risk"),
     True),
    ("priority", priorisation,
     t("06 · Priorisation", "06 · Prioritization"),
     t("Water Infrastructure Priority Score et plan d'action", "Water Infrastructure Priority Score and action plan"),
     True),
    ("territories", territoires,
     t("07 · Territoires", "07 · Territories"),
     t("Regroupement territorial complémentaire", "Complementary territorial clustering"),
     True),
    ("methodology", methodologie,
     t("08 · Méthodologie", "08 · Methodology"),
     t("Sources, méthode et limites du diagnostic", "Sources, method and limitations of the diagnosis"),
     False),
    ("about", apropos,
     t("09 · À propos", "09 · About"),
     t("Auteur et contexte du projet", "Author and project context"),
     False),
]
PAGES = {key: (module, subtitle, needs_filters) for key, module, _, subtitle, needs_filters in PAGE_DEFS}
LABELS = {key: label for key, _, label, _, _ in PAGE_DEFS}

NAV_GROUPS = [
    (t("Diagnostic", "Diagnosis"), ["overview", "map", "pressure", "flood", "coso"]),
    (t("Décision", "Decision"), ["priority", "territories"]),
    (t("Ressources", "Resources"), ["methodology", "about"]),
]
GROUP_OF_PAGE = {key: group_title for group_title, keys in NAV_GROUPS for key in keys}

with st.sidebar:
    st.markdown("---")
    st.markdown(f"##### {t('Navigation', 'Navigation')}")
    default_page_key = st.session_state.get("page_key", PAGE_DEFS[0][0])
    page_key = sidebar_nav(
        [(title, [(k, LABELS[k]) for k in keys]) for title, keys in NAV_GROUPS],
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
