import plotly.express as px
import streamlit as st

from components import section_title, note_box, format_number
from data_loader import load_cantons_geojson, load_louvain_cantons, load_louvain_profil
from theme import PLOTLY_TEMPLATE
from i18n import t, get_lang


def render(state):
    st.write(t(
        "Analyse complémentaire : les 388 cantons sont reliés par un graphe de contiguïté territoriale "
        "(cantons limitrophes). L'algorithme de détection de communautés de Louvain regroupe ce graphe en "
        "communautés territoriales homogènes, utiles pour penser des stratégies d'intervention à l'échelle "
        "de bassins de cantons plutôt que canton par canton.",
        "Complementary analysis: the 388 cantons are connected by a territorial contiguity graph (neighboring "
        "cantons). The Louvain community detection algorithm groups this graph into homogeneous territorial "
        "communities, useful for designing intervention strategies at the scale of clusters of cantons rather "
        "than canton by canton.",
    ))

    louv = load_louvain_cantons()
    profil = load_louvain_profil()

    allowed_regions = set(state["regions"])
    louv_f = louv[louv["region"].isin(allowed_regions)] if allowed_regions else louv

    if len(louv_f) == 0:
        st.warning(t("Aucun canton ne correspond aux filtres sélectionnés.",
                      "No canton matches the selected filters."))
        return

    section_title(t("Carte des communautés territoriales", "Map of territorial communities"))
    geojson = load_cantons_geojson()
    cantons_all = state["cantons_unfiltered"]
    merged = cantons_all.merge(
        louv[["canton", "communaute_louvain"]], on="canton", how="left"
    )
    merged = merged[merged["region"].isin(allowed_regions)] if allowed_regions else merged
    merged["communaute_louvain"] = merged["communaute_louvain"].astype("Int64").astype(str)

    fig = px.choropleth_mapbox(
        merged, geojson=geojson, locations="canton_id", featureidkey="properties.canton_id",
        color="communaute_louvain", hover_name="canton",
        hover_data={"region": True, "priority_score": ":.1f", "canton_id": False},
        color_discrete_sequence=px.colors.qualitative.Set3,
        mapbox_style="carto-positron", center={"lat": 8.6, "lon": 1.0}, zoom=6.1, opacity=0.75,
        labels={"communaute_louvain": t("Communauté", "Community")},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=520, template=PLOTLY_TEMPLATE)
    st.plotly_chart(fig, width="stretch", key="territoires_map")

    section_title(t("Profil des communautés territoriales", "Profile of territorial communities"))
    if get_lang() == "en":
        profil_rename = {
            "communaute_louvain": "Community", "nb_cantons": "Nb. cantons",
            "population_totale": "Total population", "fri_moyen": "Average FRI",
            "priority_score_moyen": "Average priority score", "pression_moyenne": "Average pressure",
            "regions": "Regions covered",
        }
    else:
        profil_rename = {
            "communaute_louvain": "Communauté", "nb_cantons": "Nb cantons",
            "population_totale": "Population totale", "fri_moyen": "FRI moyen",
            "priority_score_moyen": "Score priorité moyen", "pression_moyenne": "Pression moyenne",
            "regions": "Régions couvertes",
        }
    st.dataframe(
        profil.rename(columns=profil_rename),
        width="stretch", hide_index=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.bar(
            profil.sort_values("priority_score_moyen"), x="priority_score_moyen", y="communaute_louvain",
            orientation="h", color="priority_score_moyen", color_continuous_scale="OrRd",
            labels={"priority_score_moyen": t("Score de priorité moyen", "Average priority score"),
                    "communaute_louvain": t("Communauté", "Community")},
            title=t("Score de priorité moyen par communauté", "Average priority score by community"),
        )
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(t=40), coloraxis_showscale=False)
        st.plotly_chart(fig2, width="stretch", key="territoires_bar_score")
    with col2:
        fig3 = px.scatter(
            profil, x="fri_moyen", y="pression_moyenne", size="population_totale",
            color="priority_score_moyen", color_continuous_scale="OrRd", hover_name="communaute_louvain",
            labels={"fri_moyen": t("FRI moyen", "Average FRI"),
                    "pression_moyenne": t("Pression moyenne (hab./ouvrage)", "Average pressure (inh./infrastructure)")},
            title=t("Risque et pression moyens par communauté", "Average risk and pressure by community"),
        )
        fig3.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(t=40))
        st.plotly_chart(fig3, width="stretch", key="territoires_scatter")

    note_box(t(
        "Cette lecture par communautés territoriales est une analyse exploratoire complémentaire au score de "
        "priorité par canton : elle permet d'identifier des groupes de cantons voisins partageant un profil de "
        "risque et de pression similaire, ce qui peut faciliter la planification d'interventions groupées "
        "(mutualisation logistique, marchés groupés de forage).",
        "This reading by territorial communities is an exploratory analysis complementary to the per-canton "
        "priority score: it helps identify groups of neighboring cantons sharing a similar risk and pressure "
        "profile, which can facilitate the planning of grouped interventions (shared logistics, bundled "
        "drilling contracts).",
    ))
