import plotly.express as px
import streamlit as st

from components import section_title, note_box, format_number
from data_loader import load_scenarios, load_recommandations
from theme import PLOTLY_TEMPLATE, SEGMENT_COLORS
from i18n import t, get_lang, PRIORITE_LABELS_EN


def render(state):
    cantons_f = state["cantons"]

    st.write(t(
        "Le Water Infrastructure Priority Score combine, pour chaque canton, la pression démographique (30 %), "
        "le risque d'inondation (25 %), la vulnérabilité socio-économique (15 %), la faiblesse de la "
        "couverture en ouvrages documentés (20 %) et le poids démographique absolu (10 %). Ces pondérations "
        "sont un choix méthodologique explicite, modifiable et à valider avec les parties prenantes du secteur.",
        "The Water Infrastructure Priority Score combines, for each canton, demographic pressure (30%), "
        "flood risk (25%), socio-economic vulnerability (15%), weak documented infrastructure coverage (20%) "
        "and absolute demographic weight (10%). These weights are an explicit, adjustable methodological "
        "choice, to be validated with sector stakeholders.",
    ))

    if len(cantons_f) == 0:
        st.warning(t("Aucun canton ne correspond aux filtres sélectionnés.",
                      "No canton matches the selected filters."))
        return

    section_title(t("Distribution du score de priorité", "Priority score distribution"))
    col1, col2 = st.columns([1.3, 1])
    with col1:
        fig1 = px.histogram(
            cantons_f, x="priority_score", nbins=30, color_discrete_sequence=["#C8102E"],
            labels={"priority_score": "Water Infrastructure Priority Score (0-100)"},
            title=t("Distribution du score de priorité (sélection)", "Priority score distribution (selection)"),
        )
        p90 = cantons_f["priority_score"].quantile(0.9)
        fig1.add_vline(x=p90, line_dash="dash", line_color="black", annotation_text=t("90e percentile", "90th percentile"))
        fig1.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(t=40))
        st.plotly_chart(fig1, width="stretch", key="prio_hist")
    with col2:
        fig2 = px.scatter(
            cantons_f, x="pression_actuelle", y="FRI", size="total_pop", color="segment",
            color_discrete_map=SEGMENT_COLORS, hover_name="canton", hover_data=["region", "priority_score"],
            log_x=True,
            labels={"pression_actuelle": t("Pression actuelle (échelle log)", "Current pressure (log scale)"),
                    "FRI": t("Risque d'inondation (FRI)", "Flood risk (FRI)")},
            title=t("Matrice de segmentation : pression vs risque d'inondation",
                     "Segmentation matrix: pressure vs flood risk"),
        )
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(t=40),
                            legend=dict(orientation="h", y=-0.35, font=dict(size=8)))
        st.plotly_chart(fig2, width="stretch", key="prio_matrix")

    section_title(t("Territoires prioritaires (sélection filtrée)", "Priority territories (filtered selection)"))
    # Ces noms de segments correspondent aux valeurs exactes du jeu de données (colonne "segment").
    seg_names = [
        "Nouveaux ouvrages prioritaires",
        "Maintenance et renforcement urgents",
        "Renforcement (vulnerabilite aux inondations)",
        "Surveillance",
    ]
    tab_labels_en = [
        "Priority new infrastructure",
        "Urgent maintenance & reinforcement",
        "Reinforcement (flood vulnerability)",
        "Monitoring",
    ]
    tab_labels_fr = [
        "Nouveaux ouvrages prioritaires",
        "Maintenance et renforcement urgents",
        "Renforcement (vulnérabilité inondation)",
        "Surveillance",
    ]
    tab_labels = tab_labels_en if get_lang() == "en" else tab_labels_fr
    tabs = st.tabs(tab_labels)
    cols_show = ["region", "prefecture", "commune", "canton", "total_pop", "nb_ouvrages_documentes",
                 "FRI", "priority_score"]
    if get_lang() == "en":
        cols_rename = {
            "total_pop": "Population", "nb_ouvrages_documentes": "Documented infrastructure",
            "priority_score": "Priority score", "region": "Region", "prefecture": "Prefecture",
            "commune": "Commune", "canton": "Canton",
        }
    else:
        cols_rename = {
            "total_pop": "Population", "nb_ouvrages_documentes": "Ouvrages documentés",
            "priority_score": "Score de priorité", "region": "Région", "prefecture": "Préfecture",
            "commune": "Commune", "canton": "Canton",
        }
    for tab, seg in zip(tabs, seg_names):
        with tab:
            sub = cantons_f[cantons_f["segment"] == seg].sort_values("priority_score", ascending=False)
            st.caption(t(
                f"{format_number(len(sub))} cantons dans cette catégorie (sélection courante).",
                f"{format_number(len(sub))} cantons in this category (current selection).",
            ))
            st.dataframe(
                sub[cols_show].head(30).rename(columns=cols_rename),
                width="stretch", height=300, hide_index=True,
            )

    section_title(t("Scénarios de sensibilité (illustratifs, non prédictifs)",
                     "Sensitivity scenarios (illustrative, not predictive)"))
    scenarios = load_scenarios()
    col3, col4 = st.columns([1, 1.2])
    with col3:
        if get_lang() == "en":
            scen_rename = {
                "scenario": "Scenario", "croissance_population_%": "Pop. growth (%)",
                "nouveaux_ouvrages_hypothetiques": "New infrastructure (hyp.)",
                "population_scenario": "Population (scenario)",
                "ouvrages_documentes_scenario": "Infrastructure (scenario)",
                "pression_nationale_scenario": "National pressure (scenario)",
                "variation_pression_vs_actuel_%": "Change vs current (%)",
            }
        else:
            scen_rename = {
                "scenario": "Scénario", "croissance_population_%": "Croissance pop. (%)",
                "nouveaux_ouvrages_hypothetiques": "Nouveaux ouvrages (hyp.)",
                "population_scenario": "Population (scénario)",
                "ouvrages_documentes_scenario": "Ouvrages (scénario)",
                "pression_nationale_scenario": "Pression nationale (scénario)",
                "variation_pression_vs_actuel_%": "Variation vs actuel (%)",
            }
        st.dataframe(scenarios.rename(columns=scen_rename), width="stretch", hide_index=True, height=180)
    with col4:
        fig3 = px.bar(
            scenarios, x="scenario", y="variation_pression_vs_actuel_%",
            color="scenario", color_discrete_sequence=["#5B6660", "#F2B705", "#145C43"],
            labels={"variation_pression_vs_actuel_%": t("Variation de la pression nationale (%)",
                                                          "Change in national pressure (%)"), "scenario": ""},
            title=t("Effet des scénarios sur la pression hydraulique nationale",
                     "Effect of scenarios on national water pressure"),
        )
        fig3.update_layout(template=PLOTLY_TEMPLATE, showlegend=False, height=260, margin=dict(t=40))
        st.plotly_chart(fig3, width="stretch", key="prio_scenarios")

    note_box(t(
        "Ces scénarios sont des simulations basées sur des hypothèses explicites et illustratives (croissance "
        "de population, nombre de nouveaux ouvrages), et non des projections statistiques : les données "
        "fournies ne comportent qu'une seule année de recensement, insuffisante pour un calcul de taux de "
        "croissance fiable.",
        "These scenarios are simulations based on explicit, illustrative assumptions (population growth, "
        "number of new infrastructure units), not statistical projections: the data provided covers only a "
        "single census year, insufficient for a reliable growth-rate calculation.",
    ))

    section_title(t("Recommandations stratégiques", "Strategic recommendations"))
    recos = load_recommandations()
    priorite_label = t("Priorité", "Priority")
    territoire_label = t("Territoire", "Territory")
    constat_label = t("Constat", "Finding")
    action_label = t("Action recommandée", "Recommended action")
    impact_label = t("Impact attendu", "Expected impact")
    kpi_label = t("Indicateur de suivi", "Monitoring indicator")
    for _, r in recos.iterrows():
        tag_class = "haute" if r["Priorite"] == "Haute" else "moyenne"
        priorite_display = PRIORITE_LABELS_EN.get(r["Priorite"], r["Priorite"]) if get_lang() == "en" else r["Priorite"]
        st.markdown(
            f"""
            <div class="rec-card">
                <span class="rec-tag {tag_class}">{priorite_label} {priorite_display}</span>
                <div class="rec-title">{r['Probleme']}</div>
                <div><b>{territoire_label} :</b> {r['Territoire']}</div>
                <div><b>{constat_label} :</b> {r['Evidence']}</div>
                <div><b>{action_label} :</b> {r['Action']}</div>
                <div><b>{impact_label} :</b> {r['Impact_attendu']}</div>
                <div><b>{kpi_label} :</b> {r['KPI_de_suivi']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
