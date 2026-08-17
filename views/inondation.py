import plotly.express as px
import streamlit as st

from components import section_title, note_box, format_number
from data_loader import load_kpi_national, load_tde_points, load_coso_points, load_region_stats
from theme import PLOTLY_TEMPLATE, REGION_COLORS
from i18n import t, get_lang


def render(state):
    kpi = load_kpi_national()
    cantons_f = state["cantons"]

    st.write(t(
        "L'indice de risque d'inondation (FRI) est un indice composite (0 à 1) calculé pour chaque canton à "
        "partir de la susceptibilité aux inondations (FSI), de la proximité aux bassins versants et d'autres "
        "variables de vulnérabilité. Le seuil de risque élevé retenu ici est le 75e percentile national.",
        "The flood risk index (FRI) is a composite index (0 to 1) calculated for each canton from flood "
        "susceptibility (FSI), proximity to watersheds and other vulnerability variables. The high-risk "
        "threshold used here is the national 75th percentile.",
    ))

    if len(cantons_f) == 0:
        st.warning(t("Aucun canton ne correspond aux filtres sélectionnés.",
                      "No canton matches the selected filters."))
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(t("Seuil FRI risque élevé (75e pct.)", "High-risk FRI threshold (75th pct.)"),
                   f"{kpi['seuil_fri_risque_eleve']:.3f}")
    with c2:
        part_eleve = (cantons_f["risque_eleve"]).mean() * 100
        st.metric(t("Cantons à risque élevé (sélection)", "High-risk cantons (selection)"), f"{part_eleve:.1f} %")
    with c3:
        st.metric(t("Ouvrages exposés (national)", "Exposed infrastructure (national)"),
                   f"{kpi['part_ouvrages_exposes_risque_eleve_%']:.1f} %")
    with c4:
        st.metric(t("FRI moyen national", "National average FRI"), f"{kpi['fri_moyen_national']:.3f}")

    section_title(t("Distribution du risque d'inondation", "Flood risk distribution"))
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.histogram(
            cantons_f, x="FRI", nbins=35, color_discrete_sequence=["#C8102E"],
            labels={"FRI": t("Indice de risque d'inondation (FRI)", "Flood risk index (FRI)")},
            title=t("Distribution du FRI par canton (sélection)", "FRI distribution by canton (selection)"),
        )
        fig1.add_vline(x=kpi["seuil_fri_risque_eleve"], line_dash="dash", line_color="black",
                        annotation_text=t("Seuil risque élevé", "High-risk threshold"))
        fig1.update_layout(template=PLOTLY_TEMPLATE, height=360, margin=dict(t=40))
        st.plotly_chart(fig1, width="stretch", key="inondation_hist")
    with col2:
        fig2 = px.box(
            cantons_f, x="region", y="FRI", color="region", color_discrete_map=REGION_COLORS,
            labels={"FRI": "FRI", "region": ""},
            title=t("Risque d'inondation (FRI) par région", "Flood risk (FRI) by region"),
        )
        fig2.update_layout(template=PLOTLY_TEMPLATE, showlegend=False, height=360, margin=dict(t=40))
        st.plotly_chart(fig2, width="stretch", key="inondation_box")

    section_title(t("Exposition des ouvrages documentés", "Exposure of documented infrastructure"))
    region_stats = load_region_stats()
    fig3 = px.bar(
        region_stats.sort_values("part_exposee_%", ascending=True),
        x="part_exposee_%", y="region", orientation="h", color="region", color_discrete_map=REGION_COLORS,
        labels={"part_exposee_%": t("Part des ouvrages exposés à un risque élevé (%)",
                                     "Share of infrastructure exposed to high risk (%)"), "region": ""},
        title=t("Part des ouvrages documentés exposés à un risque d'inondation élevé, par région",
                 "Share of documented infrastructure exposed to high flood risk, by region"),
    )
    fig3.update_layout(template=PLOTLY_TEMPLATE, showlegend=False, height=340, margin=dict(t=40))
    st.plotly_chart(fig3, width="stretch", key="inondation_expo_region")

    tde = load_tde_points()
    coso = load_coso_points()
    tde_exp = tde["expose_risque_eleve"].mean() * 100 if len(tde) else 0
    coso_exp = coso["expose_risque_eleve"].mean() * 100 if len(coso) else 0
    col3, col4 = st.columns(2)
    with col3:
        st.metric(t("Part des ouvrages TdE exposés", "Share of exposed TdE infrastructure"), f"{tde_exp:.1f} %")
    with col4:
        st.metric(t("Part des sous-projets COSO exposés", "Share of exposed COSO sub-projects"), f"{coso_exp:.1f} %")

    note_box(t(
        "La carte croisant risque d'inondation et infrastructures documentées (page Cartographie) montre que "
        "les ouvrages TdE se situent surtout dans des cantons à risque faible à modéré autour de Lomé, tandis "
        "que les cantons à FRI élevé du littoral et des zones basses restent peu couverts par les données "
        "d'infrastructures disponibles. Ce croisement alimente directement la recommandation d'inspection de "
        "résistance aux inondations (page Priorisation).",
        "The map combining flood risk and documented infrastructure (Map page) shows that TdE infrastructure "
        "is mostly located in low-to-moderate risk cantons around Lome, while high-FRI cantons along the coast "
        "and in low-lying areas remain poorly covered by the available infrastructure data. This overlap "
        "directly feeds the flood-resilience inspection recommendation (Prioritization page).",
    ))

    section_title(t("Cantons à risque élevé et vulnérabilité associée", "High-risk cantons and associated vulnerability"))
    high_risk = cantons_f[cantons_f["risque_eleve"]].sort_values("FRI", ascending=False)
    cols = ["region", "prefecture", "canton", "FRI", "max_fsi", "min_rwi", "urban_ratio",
            "total_pop", "nb_ouvrages_documentes"]
    if get_lang() == "en":
        rename_map = {
            "max_fsi": "Susceptibility (FSI)", "min_rwi": "Relative wealth (RWI)",
            "urban_ratio": "Urban rate", "total_pop": "Population", "nb_ouvrages_documentes": "Documented infrastructure",
            "region": "Region", "prefecture": "Prefecture", "canton": "Canton",
        }
    else:
        rename_map = {
            "max_fsi": "Susceptibilité (FSI)", "min_rwi": "Richesse relative (RWI)",
            "urban_ratio": "Taux urbain", "total_pop": "Population", "nb_ouvrages_documentes": "Ouvrages documentés",
            "region": "Région", "prefecture": "Préfecture", "canton": "Canton",
        }
    st.dataframe(
        high_risk[cols].rename(columns=rename_map),
        width="stretch", height=320, hide_index=True,
    )
    st.caption(t(
        f"{format_number(len(high_risk))} cantons à risque élevé dans la sélection courante.",
        f"{format_number(len(high_risk))} high-risk cantons in the current selection.",
    ))
