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
    avec un espacement net entre l'étiquette « Langue » et les boutons pour éviter tout
    effet de collage."""
    current = get_lang()
    st.markdown('<div class="lang-toggle-wrap">', unsafe_allow_html=True)
    st.markdown(
        f"<div class='lang-toggle-label'>{t('Langue', 'Language')}</div>",
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
    st.markdown('</div>', unsafe_allow_html=True)


def sidebar_brand():
    b64 = _logo_b64()
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <img src="data:image/png;base64,{b64}" class="sidebar-brand-logo" />
            <div class="sidebar-brand-text">
                <div class="sidebar-brand-title">{t("République Togolaise", "Togolese Republic")}</div>
                <div class="sidebar-brand-sub">
                    {t("Ministère de l'Eau, de l'Assainissement", "Ministry of Water, Sanitation")}<br>
                    {t("et de l'Hydraulique Villageoise", "and Rural Water Engineering")}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _language_toggle()


def sidebar_nav(groups, page_key: str) -> str:
    """Navigation latérale groupée et compacte, avec icône par page, bouton actif
    surligné (thème primaire), et repère visuel (liseré) sur le titre du groupe
    contenant la page active — pour que l'utilisateur retrouve sa position même quand
    le bouton actif n'est plus visible. L'ensemble tient sans ascenseur dans la
    barre latérale standard.

    groups : liste de (titre_groupe, [(clé, libellé_affiché, icône_material), ...])
    Retourne la clé de la page sélectionnée (met à jour st.session_state au besoin).
    """
    st.sidebar.markdown('<div class="nav-block">', unsafe_allow_html=True)
    for i, (group_title, items) in enumerate(groups):
        is_active_group = any(key == page_key for key, _, _ in items)
        css_classes = ["nav-group-title"]
        if i != 0:
            css_classes.append("nav-group-title-spaced")
        if is_active_group:
            css_classes.append("nav-group-title-active")
        st.sidebar.markdown(
            f'<div class="{" ".join(css_classes)}">{group_title}</div>', unsafe_allow_html=True
        )
        for key, label, icon in items:
            is_active = key == page_key
            if st.sidebar.button(
                label,
                key=f"nav_{key}",
                icon=f":material/{icon}:",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["page_key"] = key
                st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
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


KPI_ICONS = {
    # Petites icônes ligne (style Material), dessinées en interne pour un rendu garanti
    # et cohérent avec la charte, sans dépendance externe.
    "cantons": '<path d="M12 21c-4.2-3.6-7-7.4-7-11a7 7 0 0 1 14 0c0 3.6-2.8 7.4-7 11Z"/><circle cx="12" cy="10" r="2.6"/>',
    "population": '<path d="M17 20v-1.6a3.4 3.4 0 0 0-3.4-3.4H7.4A3.4 3.4 0 0 0 4 18.4V20"/><circle cx="10.5" cy="7.5" r="3.3"/><path d="M20 20v-1.6a3.4 3.4 0 0 0-2.3-3.2"/><path d="M14.8 4.3a3.3 3.3 0 0 1 0 6.4"/>',
    "database": '<ellipse cx="12" cy="6" rx="7.5" ry="2.6"/><path d="M4.5 6v6c0 1.4 3.4 2.6 7.5 2.6s7.5-1.2 7.5-2.6V6"/><path d="M4.5 12v6c0 1.4 3.4 2.6 7.5 2.6s7.5-1.2 7.5-2.6v-6"/>',
    "warning": '<path d="M12 3.5 21 19.5H3Z"/><path d="M12 10v4"/><circle cx="12" cy="17" r="0.15" fill="currentColor" stroke-width="2"/>',
    "gauge": '<path d="M4 15.5a8 8 0 1 1 16 0"/><path d="M12 15.5 15.5 10"/><circle cx="12" cy="15.5" r="1.1" fill="currentColor" stroke="none"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/>',
    "trend": '<path d="M3.5 17 10 10.5l4 4 6.5-7.5"/><path d="M15 6.5h5.5V12"/>',
    "flag": '<path d="M6 21V4"/><path d="M6 4.5c1.6-1.2 3.4-1.2 5 0s3.4 1.2 5 0v9c-1.6 1.2-3.4 1.2-5 0s-3.4-1.2-5 0Z"/>',
}


def kpi_card(label: str, value: str, sub: str = "", variant: str = "", icon: str = ""):
    cls = f"kpi-card {variant}".strip()
    icon_html = ""
    if icon and icon in KPI_ICONS:
        icon_html = (
            '<svg class="kpi-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{KPI_ICONS[icon]}</svg>'
        )
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="kpi-top-row">
                <div class="kpi-label">{label}</div>
                {icon_html}
            </div>
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
