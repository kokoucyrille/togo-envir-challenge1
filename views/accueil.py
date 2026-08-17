import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components import kpi_card, note_box, guide_box, kpi_group_label, section_title, format_number
from data_loader import (
    load_cantons, load_cantons_geojson, load_kpi_national, load_tde_points, load_coso_points,
)
from theme import PLOTLY_TEMPLATE, SEGMENT_COLORS, SEGMENT_SHORT_LABELS
from i18n import t, SEGMENT_SHORT_LABELS_EN, get_lang


def render(state):
    kpi = load_kpi_national()
    cantons_f = state["cantons"]
    cantons_all = state["cantons_unfiltered"]

    st.write(t(
        "Ce tableau de bord synthétise le diagnostic de l'accès à l'eau potable au Togo, construit à partir "
        "des ouvrages recensés par la Togolaise des Eaux (TdE), des sous-projets hydrauliques COSO, et de "
        "l'indice de risque d'inondation (FRI) disponible pour les 388 cantons du pays. Utilisez les filtres "
        "dans la barre latérale pour explorer les données par région, préfecture ou catégorie d'action.",
        "This dashboard summarizes the diagnosis of drinking water access in Togo, built from infrastructure "
        "recorded by Togolaise des Eaux (TdE), COSO water sub-projects, and the flood risk index (FRI) "
        "available for the country's 388 cantons. Use the filters in the sidebar to explore the data by "
        "region, prefecture or action category.",
    ))

    guide_box(t(
        "<b>Comment lire ce tableau de bord</b>"
        "<ol>"
        "<li>Le menu latéral regroupe les pages en trois familles : <b>Diagnostic</b> (constat), "
        "<b>Décision</b> (priorisation) et <b>Ressources</b> (méthode, contexte).</li>"
        "<li>Les <b>filtres du territoire</b>, sous chaque page, s'appliquent à l'ensemble du "
        "tableau de bord et restent actifs quand vous changez de page.</li>"
        "<li>La bascule <b>FR / EN</b> se trouve en haut du menu latéral.</li>"
        "</ol>",
        "<b>How to read this dashboard</b>"
        "<ol>"
        "<li>The sidebar groups pages into three families: <b>Diagnosis</b> (findings), "
        "<b>Decision</b> (prioritization) and <b>Resources</b> (method, context).</li>"
        "<li>The <b>territory filters</b>, under each page, apply to the whole dashboard and "
        "stay active when you switch pages.</li>"
        "<li>The <b>FR / EN</b> toggle is at the top of the sidebar.</li>"
        "</ol>",
    ))

    section_title(t("Indicateurs clés nationaux", "Key national indicators"))
    kpi_group_label(t("Couverture, population et ouvrages documentés",
                       "Coverage, population and documented infrastructure"))
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card(t("Cantons couverts (FRI)", "Cantons covered (FRI)"), format_number(kpi["cantons_couverts_fri"]),
                  t("Couverture territoriale complète", "Full territorial coverage"), icon="cantons")
    with c2:
        kpi_card(t("Population estimée", "Estimated population"),
                  format_number(kpi["population_totale_estimee"] / 1_000_000, 2) + " M",
                  t("Habitants, tous cantons", "Inhabitants, all cantons"), variant="gold", icon="population")
    with c3:
        kpi_card(t("Ouvrages documentés", "Documented infrastructure"),
                  format_number(kpi["nombre_ouvrages_documentes_total"]),
                  f"{kpi['nombre_points_tde']} TdE + {kpi['nombre_sous_projets_coso']} COSO", variant="grey",
                  icon="database")
    with c4:
        kpi_card(t("Cantons sans ouvrage documenté", "Cantons with no documented infrastructure"),
                  f"{kpi['part_cantons_sans_ouvrage_%']:.0f} %",
                  t("Sur l'ensemble des 388 cantons", "Out of all 388 cantons"), variant="red", icon="warning")

    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    kpi_group_label(t("Priorisation et exposition au risque", "Prioritization and risk exposure"))
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        kpi_card(t("Ouvrages / 10 000 hab.", "Infrastructure / 10,000 inh."),
                  f"{kpi['ouvrages_pour_10000_hab_national']:.3f}",
                  t("Moyenne nationale documentée", "Documented national average"), icon="gauge")
    with c6:
        kpi_card(t("Ouvrages exposés à un risque élevé", "Infrastructure exposed to high risk"),
                  f"{kpi['part_ouvrages_exposes_risque_eleve_%']:.1f} %",
                  t("FRI supérieur au seuil du 75e percentile", "FRI above the 75th percentile threshold"),
                  variant="red", icon="warning")
    with c7:
        kpi_card(t("Cantons à prioriser (nouveaux ouvrages)", "Cantons to prioritize (new infrastructure)"),
                  format_number(kpi["nombre_cantons_nouveaux_ouvrages_prioritaires"]),
                  t("Pression forte et 0 ouvrage documenté", "High pressure and 0 documented infrastructure"),
                  variant="gold", icon="flag")
    with c8:
        kpi_card(t("Score de priorité moyen", "Average priority score"), f"{kpi['score_priorite_moyen']:.1f} / 100",
                  "Water Infrastructure Priority Score", variant="grey", icon="target")

    st.markdown("<br>", unsafe_allow_html=True)
    section_title(t(
        f"Carte de synthèse ({len(cantons_f)} cantons sélectionnés sur {len(cantons_all)})",
        f"Summary map ({len(cantons_f)} cantons selected out of {len(cantons_all)})",
    ))

    geojson = load_cantons_geojson()
    map_col, side_col = st.columns([2.3, 1])

    with map_col:
        if len(cantons_f) == 0:
            st.warning(t("Aucun canton ne correspond aux filtres sélectionnés.",
                          "No canton matches the selected filters."))
        else:
            fig = px.choropleth_mapbox(
                cantons_f,
                geojson=geojson,
                locations="canton_id",
                featureidkey="properties.canton_id",
                color="priority_score",
                hover_name="canton",
                hover_data={"region": True, "priority_score": ":.1f", "FRI": ":.2f",
                            "total_pop": ":,.0f", "canton_id": False},
                color_continuous_scale="OrRd",
                mapbox_style="carto-positron",
                center={"lat": 8.6, "lon": 1.0},
                zoom=6,
                opacity=0.75,
                labels={"priority_score": t("Score de priorité", "Priority score")},
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=480,
                               template=PLOTLY_TEMPLATE)
            st.plotly_chart(fig, width="stretch", key="accueil_map")
            st.caption(t(
                "Couleur = Water Infrastructure Priority Score (rouge = priorité plus forte). "
                "Voir la page Cartographie pour les couches FRI, population et ouvrages.",
                "Color = Water Infrastructure Priority Score (red = higher priority). "
                "See the Map page for the FRI, population and infrastructure layers.",
            ))

    with side_col:
        repartition_title = t("Répartition des cantons par catégorie d'action", "Cantons by action category")
        st.markdown(f"**{repartition_title}**")
        seg_counts = cantons_f["segment"].value_counts().reset_index()
        seg_counts.columns = ["segment", "nb_cantons"]
        short_labels = SEGMENT_SHORT_LABELS_EN if get_lang() == "en" else SEGMENT_SHORT_LABELS
        seg_counts["segment_court"] = seg_counts["segment"].map(short_labels)
        color_map_short = {short_labels[k]: v for k, v in SEGMENT_COLORS.items()}
        fig_seg = px.pie(
            seg_counts, names="segment_court", values="nb_cantons", hole=0.55,
            color="segment_court", color_discrete_map=color_map_short,
        )
        fig_seg.update_layout(
            template=PLOTLY_TEMPLATE, margin=dict(l=0, r=0, t=10, b=0), height=300,
            legend=dict(orientation="h", yanchor="bottom", y=-0.65, font=dict(size=9), title=None),
        )
        fig_seg.update_traces(textinfo="percent", textfont_size=11)
        st.plotly_chart(fig_seg, width="stretch", key="accueil_pie")

        st.markdown(f"**{t('Ouvrages documentés par source', 'Documented infrastructure by source')}**")
        fig_src = go.Figure(go.Bar(
            x=[kpi["nombre_points_tde"], kpi["nombre_sous_projets_coso"]],
            y=["TdE", "COSO"], orientation="h",
            marker_color=["#145C43", "#F2B705"],
            text=[kpi["nombre_points_tde"], kpi["nombre_sous_projets_coso"]],
            textposition="outside",
        ))
        fig_src.update_layout(template=PLOTLY_TEMPLATE, height=170,
                               margin=dict(l=0, r=10, t=10, b=10), xaxis_title=None)
        st.plotly_chart(fig_src, width="stretch", key="accueil_bar_src")

    st.markdown("<br>", unsafe_allow_html=True)
    section_title(t("Constat principal", "Main finding"))
    note_box(t(
        "Deux jeux de données seulement documentent des ouvrages hydrauliques individuels géolocalisés : "
        f"{kpi['nombre_points_tde']} points TdE (concentrés autour de Lomé) et {kpi['nombre_sous_projets_coso']} "
        "sous-projets COSO (régions Centrale, Kara, Savanes). Près de "
        f"{kpi['part_cantons_sans_ouvrage_%']:.0f}% des 388 cantons ne comportent aucun ouvrage documenté dans "
        "ces bases : ce chiffre traduit à la fois un possible déficit réel d'infrastructure et une couverture "
        "partielle des données disponibles. Voir la page Méthodologie et limites pour le détail de cette réserve.",
        "Only two datasets document individually geolocated water infrastructure: "
        f"{kpi['nombre_points_tde']} TdE points (concentrated around Lome) and {kpi['nombre_sous_projets_coso']} "
        "COSO sub-projects (Centrale, Kara, Savanes regions). Nearly "
        f"{kpi['part_cantons_sans_ouvrage_%']:.0f}% of the 388 cantons have no documented infrastructure in "
        "these databases: this figure reflects both a possible real infrastructure deficit and partial data "
        "coverage. See the Methodology and limitations page for details on this caveat.",
    ))
