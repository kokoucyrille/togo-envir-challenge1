"""Composants d'interface réutilisables (en-tête, cartes KPI, etc.)."""
import base64
from pathlib import Path

import streamlit as st

from theme import BASE_CSS, GREEN_DARK, GREY, BORDER
from data_loader import logo_path
from i18n import t, get_lang, set_lang


def inject_base_style():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def _logo_b64() -> str:
    p = Path(logo_path())
    return base64.b64encode(p.read_bytes()).decode()


def _language_toggle():
    """Bascule FR / EN sous forme de deux boutons côte à côte (mêmes styles que la nav),
    parfaitement centrés et alignés avec le reste de la barre latérale."""
    current = get_lang()
    st.markdown(
        f"<div style='text-align:center; font-size:0.68rem; color:{GREY}; "
        f"text-transform:uppercase; letter-spacing:0.4px; margin-bottom:3px;'>"
        f"{t('Langue', 'Language')}</div>",
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("FR", key="lang_fr", use_container_width=True,
                      type="primary" if current == "fr" else "secondary"):
            if current != "fr":
                set_lang("fr")
                st.rerun()
    with col2:
        if st.button("EN", key="lang_en", use_container_width=True,
                      type="primary" if current == "en" else "secondary"):
            if current != "en":
                set_lang("en")
                st.rerun()


def sidebar_brand():
    b64 = _logo_b64()
    st.markdown(
        f"""
        <div style="text-align:center; padding: 2px 0 10px 0;">
            <img src="data:image/png;base64,{b64}"
                 style="width:76px; height:76px; border-radius:50%; background:white;
                        padding:4px; border:1px solid {BORDER}; margin:0 auto;" />
            <div style="font-weight:700; color:{GREEN_DARK}; margin-top:8px; font-size:0.9rem;">
                {t("République Togolaise", "Togolese Republic")}
            </div>
            <div style="color:{GREY}; font-size:0.7rem; margin-top:2px; line-height:1.25;">
                {t("Ministère de l'Eau, de l'Assainissement", "Ministry of Water, Sanitation")}<br>
                {t("et de l'Hydraulique Villageoise", "and Rural Water Engineering")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _language_toggle()


def sidebar_nav(groups, page_key: str) -> str:
    """Navigation latérale groupée, avec bouton actif surligné (thème primaire) et
    repère visuel (liseré) sur le titre du groupe contenant la page active, pour que
    l'utilisateur retrouve sa position même quand le bouton actif n'est plus visible.

    groups : liste de (titre_groupe, [(clé, libellé_affiché), ...])
    Retourne la clé de la page sélectionnée (met à jour st.session_state au besoin).
    """
    for i, (group_title, items) in enumerate(groups):
        is_active_group = any(key == page_key for key, _ in items)
        css_classes = ["nav-group-title"]
        if i != 0:
            css_classes.append("nav-group-title-spaced")
        if is_active_group:
            css_classes.append("nav-group-title-active")
        st.sidebar.markdown(
            f'<div class="{" ".join(css_classes)}">{group_title}</div>', unsafe_allow_html=True
        )
        for key, label in items:
            is_active = key == page_key
            if st.sidebar.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["page_key"] = key
                st.rerun()
    return st.session_state.get("page_key", page_key)


def page_header(title: str, subtitle: str):
    b64 = _logo_b64()
    st.markdown(
        f"""
        <div class="app-header">
            <img src="data:image/png;base64,{b64}" />
            <div class="titles">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def breadcrumb(section: str, page: str):
    """Repère de position (« fil d'Ariane ») affiché sous l'en-tête de chaque page,
    pour situer immédiatement la page courante dans la structure du tableau de bord."""
    st.markdown(
        f'<div class="breadcrumb">{section}<span class="breadcrumb-sep">›</span>{page}</div>',
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "", variant: str = ""):
    cls = f"kpi-card {variant}".strip()
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def note_box(text: str):
    st.markdown(f'<div class="note-box">{text}</div>', unsafe_allow_html=True)


def guide_box(html_body: str):
    """Encadré « mode d'emploi » (liseré doré), distinct des constats analytiques (note_box,
    liseré vert) et des alertes (warn_box, liseré rouge) : sert uniquement à orienter la
    navigation, jamais à porter un résultat d'analyse."""
    st.markdown(f'<div class="guide-box">{html_body}</div>', unsafe_allow_html=True)


def kpi_group_label(text: str):
    """Étiquette discrète regroupant un sous-ensemble d'indicateurs clés (KPI), pour scinder
    visuellement une longue rangée de cartes en blocs de sens homogène."""
    st.markdown(f'<div class="kpi-group-label">{text}</div>', unsafe_allow_html=True)


def warn_box(text: str):
    st.markdown(f'<div class="warn-box">{text}</div>', unsafe_allow_html=True)


def filter_chips(chips):
    """Affiche une rangée de pastilles résumant les filtres actifs (chips vides ignorées)."""
    chips = [c for c in chips if c]
    if not chips:
        return
    html = "".join(f'<span class="filter-chip">{c}</span>' for c in chips)
    st.markdown(f'<div class="filter-summary">{html}</div>', unsafe_allow_html=True)


def format_number(n, decimals=0):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    fmt = f"{{:,.{decimals}f}}"
    return fmt.format(n).replace(",", " ")


def footer_note():
    st.markdown(
        f"""
        <div class="footer-note">
            {t(
                "République Togolaise — Ministère de l'Eau, de l'Assainissement et de l'Hydraulique Villageoise",
                "Togolese Republic — Ministry of Water, Sanitation and Rural Water Engineering",
            )}<br>
            {t(
                "Tableau de bord de diagnostic et de priorisation de l'accès à l'eau potable — "
                "Données TdE, COSO, FRI (indice de risque d'inondation)",
                "Diagnostic and prioritization dashboard for drinking water access — "
                "TdE, COSO, FRI (flood risk index) data",
            )}
        </div>
        """,
        unsafe_allow_html=True,
    )
