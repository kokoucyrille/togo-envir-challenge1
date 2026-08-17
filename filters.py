"""Filtres globaux, affichés dans le corps de chaque page.

Version enrichie : résumé visuel des filtres actifs (chips), raccourcis de
filtrage en un clic (presets), état persistant via st.session_state (les
choix restent identiques quand on change de page), et export CSV de la
sélection courante.
"""
import streamlit as st

from components import filter_chips, format_number
from data_loader import load_cantons
from i18n import t


def get_default_state():
    """État non filtré, utilisé sur les pages qui n'ont pas besoin de filtres (À propos, Méthodologie)."""
    cantons = load_cantons()
    return {
        "cantons": cantons,
        "cantons_unfiltered": cantons,
        "regions": sorted(cantons["region"].dropna().unique().tolist()),
        "prefectures": [],
        "segments": sorted(cantons["segment"].dropna().unique().tolist()),
        "fri_range": (float(cantons["FRI"].min()), float(cantons["FRI"].max())),
        "pop_range": (0, int(cantons["total_pop"].max())),
        "only_undocumented": False,
    }


def _preset_state(preset: str, cantons, fri_min, fri_max, pop_max):
    """Recalcule l'état de session_state qu'un raccourci appliquerait, sans le déclencher.
    Sert uniquement à détecter si ce raccourci est déjà actif, pour le surligner."""
    regions_all = sorted(cantons["region"].dropna().unique().tolist())
    segments_all = sorted(cantons["segment"].dropna().unique().tolist())
    base = {
        "flt_regions": regions_all,
        "flt_prefectures": [],
        "flt_segments": segments_all,
        "flt_fri": (round(fri_min, 2), round(fri_max, 2)),
        "flt_pop": (0, int(pop_max)),
        "flt_undoc": False,
    }
    if preset == "critical":
        base["flt_segments"] = ["Nouveaux ouvrages prioritaires"]
    elif preset == "undocumented":
        base["flt_undoc"] = True
    elif preset == "flood":
        flood_threshold = round(fri_min + 0.7 * (fri_max - fri_min), 2)
        base["flt_fri"] = (flood_threshold, round(fri_max, 2))
    return base


def _preset_is_active(preset: str, cantons, fri_min, fri_max, pop_max) -> bool:
    target = _preset_state(preset, cantons, fri_min, fri_max, pop_max)
    return all(
        set(st.session_state.get(k, [])) == set(v) if isinstance(v, list) else st.session_state.get(k) == v
        for k, v in target.items()
    )


def _apply_preset(preset: str, cantons, fri_min, fri_max, pop_max):
    """Pré-remplit les clés de session_state AVANT instanciation des widgets, puis rerun."""
    regions_all = sorted(cantons["region"].dropna().unique().tolist())
    segments_all = sorted(cantons["segment"].dropna().unique().tolist())

    if preset == "reset":
        st.session_state["flt_regions"] = regions_all
        st.session_state["flt_prefectures"] = []
        st.session_state["flt_segments"] = segments_all
        st.session_state["flt_fri"] = (round(fri_min, 2), round(fri_max, 2))
        st.session_state["flt_pop"] = (0, int(pop_max))
        st.session_state["flt_undoc"] = False
    elif preset == "critical":
        st.session_state["flt_regions"] = regions_all
        st.session_state["flt_prefectures"] = []
        st.session_state["flt_segments"] = ["Nouveaux ouvrages prioritaires"]
        st.session_state["flt_fri"] = (round(fri_min, 2), round(fri_max, 2))
        st.session_state["flt_pop"] = (0, int(pop_max))
        st.session_state["flt_undoc"] = False
    elif preset == "undocumented":
        st.session_state["flt_regions"] = regions_all
        st.session_state["flt_prefectures"] = []
        st.session_state["flt_segments"] = segments_all
        st.session_state["flt_fri"] = (round(fri_min, 2), round(fri_max, 2))
        st.session_state["flt_pop"] = (0, int(pop_max))
        st.session_state["flt_undoc"] = True
    elif preset == "flood":
        flood_threshold = round(fri_min + 0.7 * (fri_max - fri_min), 2)
        st.session_state["flt_regions"] = regions_all
        st.session_state["flt_prefectures"] = []
        st.session_state["flt_segments"] = segments_all
        st.session_state["flt_fri"] = (flood_threshold, round(fri_max, 2))
        st.session_state["flt_pop"] = (0, int(pop_max))
        st.session_state["flt_undoc"] = False
    st.rerun()


def render_global_filters():
    cantons = load_cantons()
    fri_min, fri_max = float(cantons["FRI"].min()), float(cantons["FRI"].max())
    pop_max = float(cantons["total_pop"].max())
    regions_all = sorted(cantons["region"].dropna().unique().tolist())
    segments_all = sorted(cantons["segment"].dropna().unique().tolist())

    # Valeurs par défaut la première fois que l'app se charge.
    st.session_state.setdefault("flt_regions", regions_all)
    st.session_state.setdefault("flt_prefectures", [])
    st.session_state.setdefault("flt_segments", segments_all)
    st.session_state.setdefault("flt_fri", (round(fri_min, 2), round(fri_max, 2)))
    st.session_state.setdefault("flt_pop", (0, int(pop_max)))
    st.session_state.setdefault("flt_undoc", False)

    # --- Raccourcis rapides (presets), toujours visibles au-dessus du panneau ---
    # Le raccourci actuellement actif (le cas échéant) est surligné (bouton "primary"),
    # pour que l'utilisateur sache toujours quel filtrage rapide est appliqué.
    st.caption(t("Raccourcis de filtrage :", "Filter shortcuts:"))
    preset_cols = st.columns(4)
    with preset_cols[0]:
        active = _preset_is_active("critical", cantons, fri_min, fri_max, pop_max)
        if st.button(t("Cantons critiques", "Critical cantons"), key="preset_critical",
                      use_container_width=True, type="primary" if active else "secondary"):
            _apply_preset("critical", cantons, fri_min, fri_max, pop_max)
    with preset_cols[1]:
        active = _preset_is_active("undocumented", cantons, fri_min, fri_max, pop_max)
        if st.button(t("Sans ouvrage", "No infrastructure"), key="preset_undoc",
                      use_container_width=True, type="primary" if active else "secondary"):
            _apply_preset("undocumented", cantons, fri_min, fri_max, pop_max)
    with preset_cols[2]:
        active = _preset_is_active("flood", cantons, fri_min, fri_max, pop_max)
        if st.button(t("Risque inondation élevé", "High flood risk"), key="preset_flood",
                      use_container_width=True, type="primary" if active else "secondary"):
            _apply_preset("flood", cantons, fri_min, fri_max, pop_max)
    with preset_cols[3]:
        if st.button(t("Réinitialiser", "Reset"), key="preset_reset", use_container_width=True):
            _apply_preset("reset", cantons, fri_min, fri_max, pop_max)

    # --- Calcul du nombre de filtres actifs, pour l'étiquette du panneau ---
    active = 0
    if set(st.session_state["flt_regions"]) != set(regions_all):
        active += 1
    if st.session_state["flt_prefectures"]:
        active += 1
    if set(st.session_state["flt_segments"]) != set(segments_all):
        active += 1
    if st.session_state["flt_fri"] != (round(fri_min, 2), round(fri_max, 2)):
        active += 1
    if st.session_state["flt_pop"] != (0, int(pop_max)):
        active += 1
    if st.session_state["flt_undoc"]:
        active += 1

    label_base = t("Filtres du territoire", "Territory filters")
    expander_label = f"{label_base} — {active} " + t("actif(s)", "active") if active else \
        f"{label_base} ({t('aucun filtre actif', 'no active filter')})"

    with st.expander(expander_label, expanded=False):
        st.caption(t(
            "Ces filtres s'appliquent à l'ensemble des pages du tableau de bord et restent actifs "
            "quand vous changez de page.",
            "These filters apply to every page of the dashboard and stay active when you switch pages.",
        ))

        row1_c1, row1_c2, row1_c3 = st.columns(3)
        with row1_c1:
            sel_regions = st.multiselect(t("Région", "Region"), regions_all, key="flt_regions")
        with row1_c2:
            base = cantons[cantons["region"].isin(sel_regions)] if sel_regions else cantons.iloc[0:0]
            prefectures = sorted(base["prefecture"].dropna().unique().tolist())
            valid_prefs = [p for p in st.session_state["flt_prefectures"] if p in prefectures]
            if valid_prefs != st.session_state["flt_prefectures"]:
                st.session_state["flt_prefectures"] = valid_prefs
            sel_prefectures = st.multiselect(t("Préfecture", "Prefecture"), prefectures, key="flt_prefectures")
        with row1_c3:
            sel_segments = st.multiselect(
                t("Catégorie d'action (segment)", "Action category (segment)"), segments_all, key="flt_segments",
            )

        row2_c1, row2_c2, row2_c3 = st.columns(3)
        with row2_c1:
            sel_fri = st.slider(
                t("Indice de risque d'inondation (FRI)", "Flood risk index (FRI)"),
                min_value=round(fri_min, 2), max_value=round(fri_max, 2),
                key="flt_fri",
                help=t("0 = aucun risque, 1 = risque maximal", "0 = no risk, 1 = maximum risk"),
            )
        with row2_c2:
            sel_pop = st.slider(
                t("Population estimée du canton", "Estimated canton population"),
                min_value=0, max_value=int(pop_max), step=1000, format="%d",
                key="flt_pop",
            )
        with row2_c3:
            only_undocumented = st.checkbox(
                t("Cantons sans ouvrage documenté uniquement", "Cantons with no documented infrastructure only"),
                key="flt_undoc",
            )

    filtered = cantons[cantons["region"].isin(sel_regions)]
    if sel_prefectures:
        filtered = filtered[filtered["prefecture"].isin(sel_prefectures)]
    if sel_segments:
        filtered = filtered[filtered["segment"].isin(sel_segments)]
    filtered = filtered[(filtered["FRI"] >= sel_fri[0]) & (filtered["FRI"] <= sel_fri[1])]
    filtered = filtered[(filtered["total_pop"] >= sel_pop[0]) & (filtered["total_pop"] <= sel_pop[1])]
    if only_undocumented:
        filtered = filtered[filtered["nb_ouvrages_documentes"] == 0]

    # --- Résumé visuel (chips) + export, toujours visibles sous le panneau ---
    summary_col, export_col = st.columns([4, 1])
    with summary_col:
        chips = [f"{format_number(len(filtered))}/{format_number(len(cantons))} " + t("cantons", "cantons")]
        if set(sel_regions) != set(regions_all):
            chips.append(t("Régions : ", "Regions: ") + (", ".join(sel_regions) if len(sel_regions) <= 3
                          else f"{len(sel_regions)} " + t("sélectionnées", "selected")))
        if sel_prefectures:
            chips.append(t("Préfectures : ", "Prefectures: ") + str(len(sel_prefectures)))
        if set(sel_segments) != set(segments_all):
            chips.append(f"{len(sel_segments)} " + t("segment(s)", "segment(s)"))
        if sel_fri != (round(fri_min, 2), round(fri_max, 2)):
            chips.append(f"FRI {sel_fri[0]}–{sel_fri[1]}")
        if only_undocumented:
            chips.append(t("Sans ouvrage documenté", "No documented infrastructure"))
        filter_chips(chips)
    with export_col:
        st.download_button(
            t("Exporter (CSV)", "Export (CSV)"),
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="cantons_selection.csv",
            mime="text/csv",
            use_container_width=True,
        )

    return {
        "cantons": filtered,
        "cantons_unfiltered": cantons,
        "regions": sel_regions,
        "prefectures": sel_prefectures,
        "segments": sel_segments,
        "fri_range": sel_fri,
        "pop_range": sel_pop,
        "only_undocumented": only_undocumented,
    }
