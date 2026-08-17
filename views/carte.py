import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components import section_title, note_box, format_number
from data_loader import load_cantons_geojson, load_tde_points, load_coso_points
from theme import PLOTLY_TEMPLATE
from i18n import t, get_lang


def _layer_options():
    if get_lang() == "en":
        return {
            "Priority score (Priority Score)": ("priority_score", "OrRd", "Priority score"),
            "Flood risk (FRI)": ("FRI", "YlOrRd", "FRI (0-1)"),
            "Estimated population": ("total_pop", "Greens", "Population"),
            "Documented infrastructure / 10,000 inh.": ("ouvrages_pour_10000_hab", "Blues", "Infrastructure / 10,000 inh."),
            "Current demographic pressure": ("pression_actuelle", "PuRd", "Pressure (inh./infrastructure)"),
        }
    return {
        "Score de priorité (Priority Score)": ("priority_score", "OrRd", "Score de priorité"),
        "Risque d'inondation (FRI)": ("FRI", "YlOrRd", "FRI (0-1)"),
        "Population estimée": ("total_pop", "Greens", "Population"),
        "Ouvrages documentés / 10 000 hab.": ("ouvrages_pour_10000_hab", "Blues", "Ouvrages / 10 000 hab."),
        "Pression démographique actuelle": ("pression_actuelle", "PuRd", "Pression (hab./ouvrage)"),
    }


def render(state):
    st.write(t(
        "Carte interactive croisant le risque d'inondation, la population estimée et la localisation des "
        "ouvrages hydrauliques documentés (TdE et COSO). Choisissez la couche de fond et les couches de points "
        "à afficher, puis survolez la carte pour consulter le détail de chaque canton ou ouvrage.",
        "Interactive map combining flood risk, estimated population and the location of documented water "
        "infrastructure (TdE and COSO). Choose the background layer and the point layers to display, then "
        "hover over the map to see details for each canton or facility.",
    ))

    cantons_f = state["cantons"]
    layer_options = _layer_options()

    ctrl1, ctrl2, ctrl3 = st.columns([1.4, 1, 1])
    with ctrl1:
        layer_label = st.selectbox(t("Couche de fond (choropleth par canton)", "Background layer (choropleth by canton)"),
                                    list(layer_options.keys()))
    with ctrl2:
        show_tde = st.checkbox(t("Afficher les ouvrages TdE", "Show TdE infrastructure"), value=True)
    with ctrl3:
        show_coso = st.checkbox(t("Afficher les sous-projets COSO", "Show COSO sub-projects"), value=True)

    only_exposed = st.checkbox(
        t("N'afficher que les ouvrages exposés à un risque d'inondation élevé",
          "Show only infrastructure exposed to high flood risk"),
        value=False,
    )

    column, scale, label = layer_options[layer_label]

    if len(cantons_f) == 0:
        st.warning(t("Aucun canton ne correspond aux filtres sélectionnés dans la barre latérale.",
                      "No canton matches the filters selected in the sidebar."))
        return

    geojson = load_cantons_geojson()
    fig = px.choropleth_mapbox(
        cantons_f,
        geojson=geojson,
        locations="canton_id",
        featureidkey="properties.canton_id",
        color=column,
        hover_name="canton",
        hover_data={"region": True, "priority_score": ":.1f", "FRI": ":.2f",
                     "total_pop": ":,.0f", "nb_ouvrages_documentes": True, "canton_id": False},
        color_continuous_scale=scale,
        mapbox_style="carto-positron",
        center={"lat": 8.6, "lon": 1.0},
        zoom=6.3,
        opacity=0.72,
        labels={column: label},
    )

    if show_tde:
        tde = load_tde_points()
        if only_exposed:
            tde = tde[tde["expose_risque_eleve"] == True]
        allowed_regions = set(state["regions"])
        if allowed_regions:
            tde = tde[tde["region"].isin(allowed_regions)]
        tde_name = t("Ouvrages TdE", "TdE infrastructure")
        canton_lbl = t("Canton", "Canton")
        type_lbl = t("Type", "Type")
        organisme_lbl = t("Organisme", "Organization")
        fig.add_trace(go.Scattermapbox(
            lon=tde["lon"], lat=tde["lat"], mode="markers",
            marker=dict(size=8, color="#1E3A8A", opacity=0.85),
            name=tde_name,
            customdata=tde[["canton", "type_ouvrage", "organisme"]].values,
            hovertemplate=f"<b>{tde_name}</b><br>{canton_lbl} : "
                          "%{customdata[0]}<br>" + type_lbl + " : %{customdata[1]}"
                          "<br>" + organisme_lbl + " : %{customdata[2]}<extra></extra>",
        ))

    if show_coso:
        coso = load_coso_points()
        if only_exposed:
            coso = coso[coso["expose_risque_eleve"] == True]
        allowed_regions = set(state["regions"])
        if allowed_regions:
            coso = coso[coso["region"].isin(allowed_regions)]
        coso_name = t("Sous-projets COSO", "COSO sub-projects")
        canton_lbl = t("Canton", "Canton")
        type_lbl = t("Type", "Type")
        stade_lbl = t("Stade", "Stage")
        non_renseigne = t("Non renseigné", "Not specified")
        fig.add_trace(go.Scattermapbox(
            lon=coso["lon"], lat=coso["lat"], mode="markers",
            marker=dict(size=7, color="#F2B705", opacity=0.85, symbol="circle"),
            name=coso_name,
            customdata=coso[["canton", "type", "stade_reception"]].fillna(non_renseigne).values,
            hovertemplate=f"<b>{coso_name}</b><br>{canton_lbl} : "
                          "%{customdata[0]}<br>" + type_lbl + " : %{customdata[1]}"
                          "<br>" + stade_lbl + " : %{customdata[2]}<extra></extra>",
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=600, template=PLOTLY_TEMPLATE,
        legend=dict(x=0.01, y=0.98, bgcolor="rgba(255,255,255,0.85)"),
    )
    st.plotly_chart(fig, width="stretch", key="carte_main")

    note_box(t(
        "Lecture de la carte : la couleur des cantons reflète la couche sélectionnée ; les marqueurs bleus "
        "sont les ouvrages TdE et les marqueurs jaunes les sous-projets COSO. Les cantons du Nord et du littoral "
        "combinant une couleur foncée (risque ou priorité élevés) et une absence de marqueurs sont ceux où "
        "l'écart entre besoin estimé et couverture documentée est le plus marqué.",
        "Reading the map: canton color reflects the selected layer; blue markers are TdE infrastructure and "
        "yellow markers are COSO sub-projects. Cantons in the North and along the coast combining a dark "
        "color (high risk or priority) with no markers are those where the gap between estimated need and "
        "documented coverage is widest.",
    ))

    section_title(t("Cantons affichés — détail", "Displayed cantons — detail"))
    display_cols = ["region", "prefecture", "commune", "canton", "total_pop", "FRI",
                     "nb_ouvrages_documentes", "priority_score", "segment"]
    if get_lang() == "en":
        rename_map = {
            "total_pop": "Population", "nb_ouvrages_documentes": "Documented infrastructure",
            "priority_score": "Priority score", "segment": "Action category",
            "region": "Region", "prefecture": "Prefecture", "commune": "Commune", "canton": "Canton",
            "FRI": "FRI",
        }
    else:
        rename_map = {
            "total_pop": "Population", "nb_ouvrages_documentes": "Ouvrages documentés",
            "priority_score": "Score de priorité", "segment": "Catégorie d'action",
            "region": "Région", "prefecture": "Préfecture", "commune": "Commune", "canton": "Canton",
            "FRI": "FRI",
        }
    st.dataframe(
        cantons_f[display_cols].sort_values("priority_score", ascending=False).rename(columns=rename_map),
        width="stretch", height=320, hide_index=True,
    )
    st.caption(t(
        f"{format_number(len(cantons_f))} cantons affichés sur la base des filtres actifs.",
        f"{format_number(len(cantons_f))} cantons displayed based on the active filters.",
    ))
