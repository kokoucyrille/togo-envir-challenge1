import plotly.express as px
import streamlit as st

from components import section_title, note_box, warn_box, format_number
from data_loader import load_region_stats
from theme import PLOTLY_TEMPLATE, REGION_COLORS
from i18n import t, get_lang


def render(state):
    cantons_f = state["cantons"]

    st.write(t(
        "La pression démographique mesure, pour chaque canton, le nombre d'habitants estimés rapporté au "
        "nombre d'ouvrages documentés (TdE + COSO). Un canton sans ouvrage documenté est traité comme la "
        "situation la plus défavorable plutôt que comme une valeur infinie.",
        "Demographic pressure measures, for each canton, the estimated number of inhabitants relative to the "
        "number of documented infrastructure units (TdE + COSO). A canton with no documented infrastructure "
        "is treated as the least favorable situation rather than as an infinite value.",
    ))

    if len(cantons_f) == 0:
        st.warning(t("Aucun canton ne correspond aux filtres sélectionnés.",
                      "No canton matches the selected filters."))
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(t("Population totale (sélection)", "Total population (selection)"),
                   format_number(cantons_f["total_pop"].sum() / 1_000_000, 2) + (" M hab." if get_lang() == "fr" else " M inh."))
    with c2:
        sans_ouvrage = (cantons_f["nb_ouvrages_documentes"] == 0).mean() * 100
        st.metric(t("Cantons sans ouvrage documenté", "Cantons with no documented infrastructure"), f"{sans_ouvrage:.1f} %")
    with c3:
        st.metric(t("Pression médiane (hab./ouvrage)", "Median pressure (inh./infrastructure)"),
                   format_number(cantons_f["pression_actuelle"].median()))

    section_title(t("Population et ouvrages documentés par région", "Population and documented infrastructure by region"))
    region_stats = load_region_stats()
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(
            region_stats.sort_values("population_totale", ascending=True),
            x="population_totale", y="region", orientation="h",
            color="region", color_discrete_map=REGION_COLORS,
            labels={"population_totale": t("Population estimée", "Estimated population"), "region": ""},
            title=t("Population estimée par région (388 cantons)", "Estimated population by region (388 cantons)"),
        )
        fig1.update_layout(template=PLOTLY_TEMPLATE, showlegend=False, height=340, margin=dict(t=40))
        st.plotly_chart(fig1, width="stretch", key="pression_pop_region")
    with col2:
        fig2 = px.bar(
            region_stats.sort_values("nb_ouvrages_tde", ascending=True),
            x="nb_ouvrages_tde", y="region", orientation="h",
            color="region", color_discrete_map=REGION_COLORS,
            labels={"nb_ouvrages_tde": t("Ouvrages TdE recensés", "Recorded TdE infrastructure"), "region": ""},
            title=t("Ouvrages TdE recensés par région", "Recorded TdE infrastructure by region"),
        )
        fig2.update_layout(template=PLOTLY_TEMPLATE, showlegend=False, height=340, margin=dict(t=40))
        st.plotly_chart(fig2, width="stretch", key="pression_tde_region")

    warn_box(t(
        "Les ouvrages TdE se concentrent très majoritairement en région Maritime (agglomération de Lomé), "
        "alors que la population est plus répartie entre les cinq régions. Comparer les régions sur le seul "
        "nombre de points TdE sous-estime structurellement la couverture hors Maritime ; les sous-projets COSO "
        "(ci-dessous) sont complémentaires et concernent surtout les régions du Nord.",
        "TdE infrastructure is heavily concentrated in the Maritime region (Lome agglomeration), while "
        "population is more evenly spread across the five regions. Comparing regions on TdE point counts "
        "alone structurally underestimates coverage outside Maritime; COSO sub-projects (below) are "
        "complementary and mainly concern the northern regions.",
    ))

    section_title(t("Pression démographique par canton (sélection filtrée)",
                     "Demographic pressure by canton (filtered selection)"))
    col3, col4 = st.columns([1.3, 1])
    with col3:
        top_pression = cantons_f.sort_values("pression_actuelle", ascending=False).head(15)
        fig3 = px.bar(
            top_pression.sort_values("pression_actuelle"),
            x="pression_actuelle", y="canton", orientation="h",
            color="region", color_discrete_map=REGION_COLORS,
            hover_data=["prefecture", "total_pop", "nb_ouvrages_documentes"],
            labels={"pression_actuelle": t("Habitants par ouvrage documenté", "Inhabitants per documented infrastructure"), "canton": ""},
            title=t("15 cantons les plus sous pression (parmi la sélection)", "15 most pressured cantons (within the selection)"),
        )
        fig3.update_layout(template=PLOTLY_TEMPLATE, height=460, margin=dict(t=40))
        st.plotly_chart(fig3, width="stretch", key="pression_top_cantons")
    with col4:
        fig4 = px.scatter(
            cantons_f, x="nb_ouvrages_documentes", y="total_pop", color="segment",
            size="priority_score", hover_name="canton",
            hover_data=["region", "prefecture"],
            labels={"nb_ouvrages_documentes": t("Ouvrages documentés", "Documented infrastructure"),
                    "total_pop": t("Population estimée", "Estimated population")},
            title=t("Population vs ouvrages documentés par canton", "Population vs documented infrastructure by canton"),
        )
        fig4.update_layout(template=PLOTLY_TEMPLATE, height=460, margin=dict(t=40),
                            legend=dict(orientation="h", y=-0.3, font=dict(size=9)))
        st.plotly_chart(fig4, width="stretch", key="pression_scatter")

    note_box(t(
        "L'indicateur « ouvrages pour 10 000 habitants » mesure la densité d'ouvrages <b>documentés</b>, et non "
        "nécessairement la densité réelle d'ouvrages sur le terrain. Il doit être lu comme un indicateur combiné "
        "de couverture des données et d'équipement, à vérifier localement avant toute décision d'investissement.",
        "The 'infrastructure per 10,000 inhabitants' indicator measures the density of <b>documented</b> "
        "infrastructure, not necessarily the actual density of infrastructure on the ground. It should be read "
        "as a combined indicator of data coverage and equipment, to be verified locally before any investment "
        "decision.",
    ))

    section_title(t("Table détaillée", "Detailed table"))
    cols = ["region", "prefecture", "commune", "canton", "total_pop", "nb_ouvrages_documentes",
            "ouvrages_pour_10000_hab", "pression_actuelle", "segment"]
    if get_lang() == "en":
        rename_map = {
            "total_pop": "Population", "nb_ouvrages_documentes": "Documented infrastructure",
            "ouvrages_pour_10000_hab": "Infrastructure / 10,000 inh.", "pression_actuelle": "Pressure (inh./infrastructure)",
            "segment": "Action category", "region": "Region", "prefecture": "Prefecture",
            "commune": "Commune", "canton": "Canton",
        }
    else:
        rename_map = {
            "total_pop": "Population", "nb_ouvrages_documentes": "Ouvrages documentés",
            "ouvrages_pour_10000_hab": "Ouvrages / 10 000 hab.", "pression_actuelle": "Pression (hab./ouvrage)",
            "segment": "Catégorie d'action", "region": "Région", "prefecture": "Préfecture",
            "commune": "Commune", "canton": "Canton",
        }
    st.dataframe(
        cantons_f[cols].sort_values("pression_actuelle", ascending=False).rename(columns=rename_map),
        width="stretch", height=320, hide_index=True,
    )
