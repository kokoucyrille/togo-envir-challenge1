import plotly.express as px
import streamlit as st

from components import section_title, format_number
from data_loader import load_coso_full
from theme import PLOTLY_TEMPLATE, GREEN, GOLD
from i18n import t, get_lang, translate_series, STADE_LABELS_EN


def render(state):
    df = load_coso_full()

    st.write(t(
        "Les sous-projets COSO (financement Banque mondiale) documentent des investissements hydrauliques "
        "principalement dans les régions Centrale, Kara et Savanes. Le champ disponible est un stade "
        "administratif de réception du chantier, et non un état de fonctionnement opérationnel après mise en "
        "service.",
        "COSO sub-projects (World Bank financing) document water investments mainly in the Centrale, Kara and "
        "Savanes regions. The available field is an administrative construction acceptance stage, not an "
        "operational status after commissioning.",
    ))

    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        types = sorted(df["type"].dropna().unique().tolist())
        sel_types = st.multiselect(t("Type de sous-projet", "Sub-project type"), types, default=[])
    with ctrl2:
        stades = sorted(df["stade_reception"].dropna().unique().tolist())
        stade_format = (lambda s: STADE_LABELS_EN.get(s, s)) if get_lang() == "en" else (lambda s: s)
        sel_stades = st.multiselect(t("Stade de réception", "Acceptance stage"), stades, default=[], format_func=stade_format)
    with ctrl3:
        cost_max = float(df["estimated_cost"].dropna().max()) if df["estimated_cost"].notna().any() else 0
        sel_cost = st.slider(t("Coût estimé (FCFA)", "Estimated cost (FCFA)"), 0.0, cost_max, (0.0, cost_max))

    dff = df.copy()
    if sel_types:
        dff = dff[dff["type"].isin(sel_types)]
    if sel_stades:
        dff = dff[dff["stade_reception"].isin(sel_stades)]
    dff = dff[(dff["estimated_cost"].fillna(0) >= sel_cost[0]) & (dff["estimated_cost"].fillna(0) <= sel_cost[1])]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(t("Sous-projets (sélection)", "Sub-projects (selection)"), format_number(len(dff)))
    with c2:
        st.metric(t("Coût total estimé", "Total estimated cost"),
                   format_number(dff["estimated_cost"].sum() / 1_000_000, 1) + t(" M FCFA", "M FCFA"))
    with c3:
        st.metric(t("Bénéficiaires cumulés", "Cumulative beneficiaries"), format_number(dff["beneficiaires_totaux"].sum()))
    with c4:
        def_rate = (dff["stade_reception"] == "Reception definitive").mean() * 100 if len(dff) else 0
        st.metric(t("Part en réception définitive", "Share with final acceptance"), f"{def_rate:.1f} %")

    section_title(t("Statut des sous-projets", "Sub-project status"))
    col1, col2 = st.columns(2)
    with col1:
        stade_counts = dff["stade_reception"].value_counts().reset_index()
        stade_counts.columns = ["stade_reception", "nb"]
        stade_counts["stade_reception"] = translate_series(stade_counts["stade_reception"], STADE_LABELS_EN)
        fig1 = px.bar(
            stade_counts.sort_values("nb"), x="nb", y="stade_reception", orientation="h",
            color_discrete_sequence=[GREEN],
            labels={"nb": t("Nombre de sous-projets", "Number of sub-projects"), "stade_reception": ""},
            title=t("Répartition par stade de réception", "Breakdown by acceptance stage"),
        )
        fig1.update_layout(template=PLOTLY_TEMPLATE, height=340, margin=dict(t=40))
        st.plotly_chart(fig1, width="stretch", key="coso_stade")
    with col2:
        fig2 = px.box(
            dff, x="type", y="estimated_cost", color_discrete_sequence=[GOLD],
            labels={"estimated_cost": t("Coût estimé (FCFA)", "Estimated cost (FCFA)"), "type": ""},
            title=t("Coût estimé par type de sous-projet", "Estimated cost by sub-project type"),
        )
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=340, margin=dict(t=40), xaxis_tickangle=-35)
        st.plotly_chart(fig2, width="stretch", key="coso_cost")
