"""
Script de précalcul - reproduit la méthodologie du notebook EDA_Eau_Potable_Togo.ipynb
et exporte des jeux de données légers (CSV / GeoJSON) consommés par l'application Streamlit.

Ce script n'est exécuté qu'une fois (hors ligne) : l'application Streamlit ne dépend
ensuite que de pandas / plotly, ce qui la rend légère à déployer.
"""
import json
import warnings
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

warnings.filterwarnings("ignore")


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


RAW_DIR = Path("/home/claude/Eau-Defi1/Eau-Defi1")
DATA_DIR = RAW_DIR / "data"
OUT_DIR = Path("/home/claude/togo_eau_app/app_data")
OUT_DIR.mkdir(exist_ok=True, parents=True)

RANDOM_STATE = 42
TODAY_REF = pd.Timestamp("2026-08-13")

# ---------------------------------------------------------------------------
# 1. Chargement
# ---------------------------------------------------------------------------
df_tde_raw = pd.read_csv(DATA_DIR / "file-chateaux-deau-forages-tde-19-12-2024-18-55-00.csv")
df_coso_raw = pd.read_csv(DATA_DIR / "subprojects-sector-eau-hydraulique.csv")
gdf_fri_cantons = gpd.read_file(DATA_DIR / "fri-cantons.gpkg")
df_conso_tde = pd.read_csv(DATA_DIR / "observationdata-mfcialc.csv")

# ---------------------------------------------------------------------------
# 2. Nettoyage TdE
# ---------------------------------------------------------------------------
def parse_wkt_point(wkt):
    try:
        coords = wkt.replace("POINT (", "").replace(")", "").split()
        return float(coords[0]), float(coords[1])
    except Exception:
        return np.nan, np.nan

df_tde = df_tde_raw.copy()
df_tde.columns = [c.strip().lower() for c in df_tde.columns]
df_tde[["lon", "lat"]] = df_tde["geometry"].apply(lambda g: pd.Series(parse_wkt_point(g)))
df_tde = df_tde.dropna(subset=["lon", "lat"]).reset_index(drop=True)


def classify_ouvrage(nom):
    n = strip_accents(str(nom)).lower()
    if "chateau" in n:
        return "Chateau d'eau"
    if "nsp" in n:
        return "Indetermine"
    return "Forage"


df_tde["type_ouvrage"] = df_tde["forage_chateau_nom"].apply(classify_ouvrage)
for c in ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd"]:
    df_tde[c] = df_tde[c].astype(str).str.strip()

gdf_tde = gpd.GeoDataFrame(df_tde, geometry=gpd.points_from_xy(df_tde["lon"], df_tde["lat"]), crs="EPSG:4326")

# ---------------------------------------------------------------------------
# 3. Nettoyage COSO
# ---------------------------------------------------------------------------
df_coso = df_coso_raw.copy()
df_coso.columns = [c.strip().lower() for c in df_coso.columns]

coord_invalid = (df_coso["latitude"].abs() < 0.01) | (df_coso["longitude"].abs() < 0.01)
df_coso.loc[coord_invalid, ["latitude", "longitude"]] = np.nan

date_cols = ["launch_date", "expected_end_date", "work_completion_date",
             "official_handover_date_to_community", "date_of_provisional_acceptance_of_work"]
for c in date_cols:
    df_coso[c] = pd.to_datetime(df_coso[c], errors="coerce")

num_cols = ["progress_percent", "estimated_cost", "total_contract_amount_paid", "population",
            "direct_beneficiaries_men", "direct_beneficiaries_women", "depth_of_drilling",
            "drilling_flow_rate", "expected_duration"]
for c in num_cols:
    df_coso[c] = pd.to_numeric(df_coso[c], errors="coerce")

df_coso["beneficiaires_totaux"] = df_coso[["direct_beneficiaries_men", "direct_beneficiaries_women"]].sum(axis=1, min_count=1)


def simplify_status(s):
    s = strip_accents(str(s)).lower()
    if "definitive" in s:
        return "Reception definitive"
    if "provisoire" in s:
        return "Reception provisoire"
    if "communaute" in s:
        return "Remis a la communaute"
    if "technique" in s:
        return "Reception technique"
    if "acheve" in s:
        return "Acheve"
    return "En cours"


df_coso["stade_reception"] = df_coso["status"].apply(simplify_status)
df_coso["cout_par_beneficiaire"] = df_coso["estimated_cost"] / df_coso["beneficiaires_totaux"]
df_coso["retard_jours"] = (df_coso["work_completion_date"] - df_coso["expected_end_date"]).dt.days

df_coso_geo = df_coso.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
gdf_coso = gpd.GeoDataFrame(df_coso_geo, geometry=gpd.points_from_xy(df_coso_geo["longitude"], df_coso_geo["latitude"]), crs="EPSG:4326")

# ---------------------------------------------------------------------------
# 4. Nettoyage FRI cantons
# ---------------------------------------------------------------------------
gdf_fri = gdf_fri_cantons.copy()
gdf_fri.columns = [c.strip() for c in gdf_fri.columns]
gdf_fri = gdf_fri.drop(columns=["prefecture", "canton_n_1"], errors="ignore")
gdf_fri = gdf_fri.rename(columns={
    "region_nom": "region", "prefectu_1": "prefecture", "commune_no": "commune", "canton_nom": "canton"
})
gdf_fri["total_pop"] = pd.to_numeric(gdf_fri["total_pop"], errors="coerce")
gdf_fri["FRI"] = pd.to_numeric(gdf_fri["FRI"], errors="coerce")
if (~gdf_fri.geometry.is_valid).sum() > 0:
    gdf_fri["geometry"] = gdf_fri.geometry.buffer(0)
gdf_fri_wgs84 = gdf_fri.to_crs("EPSG:4326")

# ---------------------------------------------------------------------------
# 5. Pression démographique
# ---------------------------------------------------------------------------
infra_points = pd.concat([
    gdf_tde[["canton_nom_bdd"]].rename(columns={"canton_nom_bdd": "canton"}).assign(source="TdE"),
    df_coso[["canton"]].dropna(subset=["canton"]).assign(source="COSO")
], ignore_index=True)
infra_par_canton = infra_points.groupby("canton").size().rename("nb_ouvrages_documentes")

gdf_fri_pression = gdf_fri.merge(infra_par_canton, left_on="canton", right_index=True, how="left")
gdf_fri_pression["nb_ouvrages_documentes"] = gdf_fri_pression["nb_ouvrages_documentes"].fillna(0)
gdf_fri_pression["ouvrages_pour_10000_hab"] = np.where(
    gdf_fri_pression["total_pop"] > 0,
    gdf_fri_pression["nb_ouvrages_documentes"] / gdf_fri_pression["total_pop"] * 10000,
    np.nan
)
gdf_fri_pression["pression_actuelle"] = gdf_fri_pression["total_pop"] / (gdf_fri_pression["nb_ouvrages_documentes"] + 1)

# ---------------------------------------------------------------------------
# 6. Exposition au risque d'inondation (jointure spatiale)
# ---------------------------------------------------------------------------
gdf_tde_m = gdf_tde.to_crs(gdf_fri.crs)
gdf_coso_m = gdf_coso.drop(columns=["canton"], errors="ignore").to_crs(gdf_fri.crs)
fri_join_layer = gdf_fri[["canton", "region", "FRI", "max_fsi", "geometry"]]

tde_joined = gpd.sjoin(gdf_tde_m, fri_join_layer, how="left", predicate="within")
coso_joined = gpd.sjoin(gdf_coso_m, fri_join_layer, how="left", predicate="within")

seuil_risque_eleve = gdf_fri["FRI"].quantile(0.75)

tde_joined["expose_risque_eleve"] = tde_joined["FRI"] >= seuil_risque_eleve
coso_joined["expose_risque_eleve"] = coso_joined["FRI"] >= seuil_risque_eleve

ouvrages_exposition = pd.concat([
    tde_joined[["canton", "region", "FRI", "max_fsi", "expose_risque_eleve"]].assign(source="TdE"),
    coso_joined[["canton", "region", "FRI", "max_fsi", "expose_risque_eleve"]].assign(source="COSO")
], ignore_index=True)
taux_exposition = ouvrages_exposition["expose_risque_eleve"].mean() * 100

# ---------------------------------------------------------------------------
# 7. Water Infrastructure Priority Score
# ---------------------------------------------------------------------------
def normalize(series):
    s = series.astype(float)
    if s.max() == s.min():
        return pd.Series(0.5, index=s.index)
    return (s - s.min()) / (s.max() - s.min())


score_df = gdf_fri_pression.copy()
score_df["c_pression"] = normalize(score_df["pression_actuelle"])
score_df["c_fri"] = normalize(score_df["FRI"])
score_df["c_vulnerabilite"] = normalize(-score_df["min_rwi"])
score_df["c_couverture"] = normalize(-score_df["ouvrages_pour_10000_hab"].fillna(0))
score_df["c_population"] = normalize(score_df["total_pop"])

WEIGHTS = {
    "c_pression": 0.30,
    "c_fri": 0.25,
    "c_vulnerabilite": 0.15,
    "c_couverture": 0.20,
    "c_population": 0.10,
}
score_df["priority_score"] = (sum(score_df[c] * w for c, w in WEIGHTS.items()) * 100).round(1)

median_pression = score_df["pression_actuelle"].median()
median_fri = score_df["FRI"].median()


def segmenter(row):
    pression_forte = row["pression_actuelle"] >= median_pression
    risque_fort = row["FRI"] >= median_fri
    couverture_faible = row["nb_ouvrages_documentes"] == 0
    if pression_forte and couverture_faible:
        return "Nouveaux ouvrages prioritaires"
    if pression_forte and risque_fort and not couverture_faible:
        return "Maintenance et renforcement urgents"
    if risque_fort and not couverture_faible:
        return "Renforcement (vulnerabilite aux inondations)"
    return "Surveillance"


score_df["segment"] = score_df.apply(segmenter, axis=1)
score_df["risque_eleve"] = score_df["FRI"] >= seuil_risque_eleve

# ---------------------------------------------------------------------------
# 8. Modèle de risque de retard (COSO)
# ---------------------------------------------------------------------------
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.inspection import permutation_importance

df_model = df_coso.copy()
df_model["jours_depuis_lancement"] = (TODAY_REF - df_model["launch_date"]).dt.days
df_model["duree_prevue_jours"] = df_model["expected_duration"] * 30
df_model = df_model.dropna(subset=["progress_percent", "jours_depuis_lancement", "duree_prevue_jours",
                                    "estimated_cost", "type", "works_type"])
df_model["depassement_duree"] = df_model["jours_depuis_lancement"] - df_model["duree_prevue_jours"]
df_model["retard_significatif"] = ((df_model["progress_percent"] < 100) & (df_model["depassement_duree"] > 0)).astype(int)

feature_num = ["estimated_cost", "expected_duration", "depassement_duree"]
feature_cat = ["type", "works_type"]
X = df_model[feature_num + feature_cat]
y = df_model["retard_significatif"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y if y.nunique() > 1 else None
)
preprocess = ColumnTransformer([
    ("num", "passthrough", feature_num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), feature_cat),
])
models = {
    "Regression logistique": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, class_weight="balanced"),
    "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
}
results = []
fitted = {}
for name, clf in models.items():
    pipe = Pipeline([("prep", preprocess), ("clf", clf)])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1]
    results.append({
        "modele": name,
        "accuracy": round(accuracy_score(y_test, y_pred), 3),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 3),
        "f1": round(f1_score(y_test, y_pred, zero_division=0), 3),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 3) if y_test.nunique() > 1 else np.nan,
    })
    fitted[name] = pipe

df_results = pd.DataFrame(results).sort_values("recall", ascending=False)
best_model_name = df_results.iloc[0]["modele"]
best_pipe = fitted[best_model_name]

perm = permutation_importance(best_pipe, X_test, y_test, n_repeats=20, random_state=RANDOM_STATE, scoring="recall")
df_importance = pd.DataFrame({
    "variable": X_test.columns, "importance": perm.importances_mean
}).sort_values("importance", ascending=False)

proba_full = best_pipe.predict_proba(X)[:, 1]
df_predictions = df_model[["id", "title", "canton", "location_name", "type", "works_type", "region" if "region" in df_model.columns else "type"]].copy()
df_predictions = df_model[["id", "title", "canton", "location_name", "type", "works_type", "estimated_cost", "progress_percent", "depassement_duree"]].copy()
df_predictions["probabilite_retard"] = proba_full.round(3)
df_predictions["niveau_risque"] = pd.cut(
    df_predictions["probabilite_retard"], bins=[-0.01, 0.33, 0.66, 1.01], labels=["Faible", "Modere", "Eleve"]
)
df_predictions = df_predictions.sort_values("probabilite_retard", ascending=False)

# ---------------------------------------------------------------------------
# 9. Scénarios de sensibilité
# ---------------------------------------------------------------------------
population_actuelle = gdf_fri_pression["total_pop"].sum()
ouvrages_actuels = gdf_fri_pression["nb_ouvrages_documentes"].sum()
pression_actuelle_nationale = population_actuelle / (ouvrages_actuels + 1)

scenarios_def = {
    "Statu quo": {"croissance_pop": 0.0, "nouveaux_ouvrages": 0},
    "Investissement modéré": {"croissance_pop": 0.15, "nouveaux_ouvrages": int(len(gdf_fri_pression[gdf_fri_pression['nb_ouvrages_documentes'] == 0]) * 0.10)},
    "Investissement renforcé": {"croissance_pop": 0.15, "nouveaux_ouvrages": int(len(gdf_fri_pression[gdf_fri_pression['nb_ouvrages_documentes'] == 0]) * 0.30)},
}
scenarios_rows = []
for nom, param in scenarios_def.items():
    pop_scenario = population_actuelle * (1 + param["croissance_pop"])
    ouvrages_scenario = ouvrages_actuels + param["nouveaux_ouvrages"]
    pression_scenario = pop_scenario / (ouvrages_scenario + 1)
    scenarios_rows.append({
        "scenario": nom,
        "croissance_population_%": param["croissance_pop"] * 100,
        "nouveaux_ouvrages_hypothetiques": param["nouveaux_ouvrages"],
        "population_scenario": round(pop_scenario),
        "ouvrages_documentes_scenario": int(ouvrages_scenario),
        "pression_nationale_scenario": round(pression_scenario, 1),
        "variation_pression_vs_actuel_%": round((pression_scenario / pression_actuelle_nationale - 1) * 100, 1),
    })
df_scenarios = pd.DataFrame(scenarios_rows)

# ---------------------------------------------------------------------------
# 10. Recommandations stratégiques
# ---------------------------------------------------------------------------
recommendations = [
    {
        "Probleme": "Absence d'ouvrage documenté dans une large majorité des cantons",
        "Territoire": "Cantons du segment Nouveaux ouvrages prioritaires",
        "Evidence": "0 ouvrage TdE/COSO documenté combiné à une pression démographique supérieure à la médiane nationale",
        "Action": "Lancer un recensement de terrain des points d'eau existants (au-delà de TdE et COSO) avant toute décision de forage, puis programmer les forages là où le déficit est confirmé",
        "Priorite": "Haute",
        "Impact_attendu": "Fiabilisation de la base de décision et réduction du déficit réel de couverture",
        "KPI_de_suivi": "Nombre de cantons avec au moins un ouvrage vérifié sur le terrain",
    },
    {
        "Probleme": "Ouvrages documentés situés dans des cantons à risque d'inondation élevé",
        "Territoire": "Cantons des segments Maintenance et renforcement urgents / Renforcement",
        "Evidence": f"{taux_exposition:.1f}% des ouvrages documentés exposés à un risque d'inondation élevé",
        "Action": "Programmer une inspection technique de résistance aux inondations (surélévation des têtes de forage, protection des châteaux d'eau) sur les ouvrages concernés",
        "Priorite": "Haute",
        "Impact_attendu": "Réduction du risque de mise hors service en cas d'inondation",
        "KPI_de_suivi": "Nombre d'ouvrages inspectés et mis aux normes de protection",
    },
    {
        "Probleme": "Absence de donnée d'état de fonctionnement des ouvrages",
        "Territoire": "Ensemble du territoire",
        "Evidence": "Champ fonctionnalité absent des données TdE livrées malgré sa présence dans le dictionnaire de champs",
        "Action": "Mettre en place une collecte régulière (au moins annuelle) de l'état de fonctionnement de chaque ouvrage, avec identifiant unique pérenne",
        "Priorite": "Haute",
        "Impact_attendu": "Capacité future à calculer un taux de panne fiable et à entraîner un modèle prédictif robuste",
        "KPI_de_suivi": "Taux de couverture de la collecte d'état de fonctionnement",
    },
    {
        "Probleme": "Sous-projets COSO présentant un risque de retard élevé",
        "Territoire": "Sous-projets identifiés dans predictions_retard_projets.csv",
        "Evidence": "Probabilité de retard élevée selon le modèle de classification (avancement déclaré et dépassement de durée)",
        "Action": "Renforcer le suivi de chantier et le dialogue avec les entreprises pour les sous-projets à risque élevé",
        "Priorite": "Moyenne",
        "Impact_attendu": "Réduction des délais de mise en service effective des ouvrages",
        "KPI_de_suivi": "Écart moyen entre durée prévue et durée réelle des sous-projets",
    },
    {
        "Probleme": "Absence de série démographique multi-annuelle permettant une projection fiable",
        "Territoire": "Ensemble du territoire",
        "Evidence": "Une seule année de recensement disponible (2010) dans les données fournies",
        "Action": "Intégrer au dashboard une source démographique actualisée et multi-annuelle pour permettre de véritables projections de besoins",
        "Priorite": "Moyenne",
        "Impact_attendu": "Fiabilisation des scénarios prospectifs de déficit hydraulique",
        "KPI_de_suivi": "Disponibilité d'au moins deux années de population par canton",
    },
]
df_recommandations = pd.DataFrame(recommendations)

# ---------------------------------------------------------------------------
# 11. KPI nationaux consolidés
# ---------------------------------------------------------------------------
kpi_national = {
    "nombre_points_tde": len(gdf_tde),
    "nombre_forages_tde": int((gdf_tde["type_ouvrage"] == "Forage").sum()),
    "nombre_chateaux_tde": int((gdf_tde["type_ouvrage"] == "Chateau d'eau").sum()),
    "nombre_sous_projets_coso": len(df_coso),
    "nombre_sous_projets_geolocalises": len(gdf_coso),
    "nombre_sous_projets_receptionnes_definitivement": int((df_coso["stade_reception"] == "Reception definitive").sum()),
    "cantons_couverts_fri": len(gdf_fri),
    "population_totale_estimee": float(gdf_fri["total_pop"].sum()),
    "beneficiaires_coso_cumules": float(df_coso["beneficiaires_totaux"].sum(skipna=True)),
    "cout_total_estime_coso_fcfa": float(df_coso["estimated_cost"].sum(skipna=True)),
    "fri_moyen_national": float(gdf_fri["FRI"].mean()),
    "part_cantons_fri_eleve_%": float((gdf_fri["FRI"] >= seuil_risque_eleve).mean() * 100),
    "nombre_ouvrages_documentes_total": int(len(gdf_tde) + len(df_coso)),
    "part_cantons_sans_ouvrage_%": float((gdf_fri_pression["nb_ouvrages_documentes"] == 0).mean() * 100),
    "ouvrages_pour_10000_hab_national": round(float(ouvrages_actuels / population_actuelle * 10000), 3),
    "population_par_ouvrage_documente_national": round(float(population_actuelle / (ouvrages_actuels + 1)), 1),
    "seuil_fri_risque_eleve": round(float(seuil_risque_eleve), 3),
    "part_ouvrages_exposes_risque_eleve_%": round(float(taux_exposition), 1),
    "score_priorite_moyen": round(float(score_df["priority_score"].mean()), 1),
    "nombre_cantons_nouveaux_ouvrages_prioritaires": int((score_df["segment"] == "Nouveaux ouvrages prioritaires").sum()),
    "nombre_cantons_maintenance_urgente": int((score_df["segment"] == "Maintenance et renforcement urgents").sum()),
    "nombre_cantons_renforcement_inondation": int((score_df["segment"] == "Renforcement (vulnerabilite aux inondations)").sum()),
    "nombre_cantons_surveillance": int((score_df["segment"] == "Surveillance").sum()),
}

# ---------------------------------------------------------------------------
# 12. Exports légers pour le dashboard
# ---------------------------------------------------------------------------

# 12.1 Table cantons complète (attributs, pas de géométrie)
cantons_cols = [
    "region", "prefecture", "commune", "canton", "total_pop", "FRI", "max_fsi", "min_rwi",
    "urban_ratio", "building_count", "min_dist_basin", "nb_ouvrages_documentes",
    "ouvrages_pour_10000_hab", "pression_actuelle", "priority_score", "segment", "risque_eleve",
]
cantons_export = score_df[cantons_cols].copy()
cantons_export["canton_id"] = score_df.index
cantons_export.to_csv(OUT_DIR / "cantons.csv", index=False)

# 12.2 Géométries simplifiées (GeoJSON léger, WGS84, index = canton_id)
gdf_geo_export = gpd.GeoDataFrame(
    {"canton_id": score_df.index}, geometry=gdf_fri_wgs84.geometry.values, crs="EPSG:4326"
)
gdf_geo_export["geometry"] = gdf_geo_export.geometry.simplify(0.003, preserve_topology=True)
with open(OUT_DIR / "cantons.geojson", "w") as f:
    f.write(gdf_geo_export.to_json())

# 12.3 Points TdE
tde_export = gdf_tde[["lon", "lat", "region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd",
                       "canton_nom_bdd", "forage_chateau_nom", "organisme", "type_ouvrage"]].rename(columns={
    "region_nom_bdd": "region", "prefecture_nom_bdd": "prefecture", "commune_nom_bdd": "commune",
    "canton_nom_bdd": "canton"
}).copy()
tde_expo = tde_joined.reset_index(drop=True)[["FRI", "expose_risque_eleve"]]
tde_export["FRI_canton"] = tde_expo["FRI"].values
tde_export["expose_risque_eleve"] = tde_expo["expose_risque_eleve"].values
tde_export.to_csv(OUT_DIR / "tde_points.csv", index=False)

# 12.4 Points COSO
coso_export_cols = ["longitude", "latitude", "canton", "type", "works_type", "status", "stade_reception",
                     "progress_percent", "estimated_cost", "population", "beneficiaires_totaux",
                     "cout_par_beneficiaire", "launch_date", "expected_end_date", "work_completion_date",
                     "retard_jours", "location_name"]
coso_export = gdf_coso[coso_export_cols].rename(columns={"longitude": "lon", "latitude": "lat"}).copy()
coso_expo = coso_joined.reset_index(drop=True)[["FRI", "region", "expose_risque_eleve"]]
coso_export["FRI_canton"] = coso_expo["FRI"].values
coso_export["region"] = coso_expo["region"].values
coso_export["expose_risque_eleve"] = coso_expo["expose_risque_eleve"].values
for c in ["launch_date", "expected_end_date", "work_completion_date"]:
    coso_export[c] = coso_export[c].astype(str)
coso_export.to_csv(OUT_DIR / "coso_points.csv", index=False)

# full coso (non géolocalisé inclus) pour analyses statistiques non cartographiques
coso_full_cols = ["id", "title", "type", "works_type", "status", "stade_reception", "canton",
                   "progress_percent", "estimated_cost", "total_contract_amount_paid", "population",
                   "beneficiaires_totaux", "cout_par_beneficiaire", "launch_date", "expected_end_date",
                   "work_completion_date", "retard_jours", "expected_duration", "location_name"]
coso_full = df_coso[coso_full_cols].copy()
for c in ["launch_date", "expected_end_date", "work_completion_date"]:
    coso_full[c] = coso_full[c].astype(str)
coso_full.to_csv(OUT_DIR / "coso_full.csv", index=False)

# 12.5 Prédictions de retard
df_predictions.to_csv(OUT_DIR / "predictions_retard.csv", index=False)
df_results.to_csv(OUT_DIR / "model_results.csv", index=False)
df_importance.to_csv(OUT_DIR / "model_importance.csv", index=False)

# 12.6 Scénarios
df_scenarios.to_csv(OUT_DIR / "scenarios.csv", index=False)

# 12.7 Recommandations
df_recommandations.to_csv(OUT_DIR / "recommandations.csv", index=False)

# 12.8 KPI nationaux
pd.DataFrame(list(kpi_national.items()), columns=["indicateur", "valeur"]).to_csv(
    OUT_DIR / "kpi_national.csv", index=False
)
with open(OUT_DIR / "kpi_national.json", "w") as f:
    json.dump(kpi_national, f, indent=2)

# 12.9 Stats régionales
region_stats = gdf_fri.groupby("region").agg(
    nb_cantons=("canton", "count"),
    population_totale=("total_pop", "sum"),
    fri_moyen=("FRI", "mean"),
    fri_max=("FRI", "max"),
    fsi_moyen=("max_fsi", "mean"),
    urbain_moyen=("urban_ratio", "mean"),
).reset_index()
tde_par_region = gdf_tde.groupby("region_nom_bdd").size().rename("nb_ouvrages_tde").reset_index().rename(columns={"region_nom_bdd": "region"})
region_stats = region_stats.merge(tde_par_region, on="region", how="left")
region_stats["nb_ouvrages_tde"] = region_stats["nb_ouvrages_tde"].fillna(0).astype(int)
expo_region = ouvrages_exposition.groupby("region").agg(
    nb_ouvrages_documentes=("FRI", "count"),
    fri_moyen_ouvrages=("FRI", "mean"),
    part_exposee=("expose_risque_eleve", "mean"),
).reset_index()
expo_region["part_exposee_%"] = (expo_region["part_exposee"] * 100).round(1)
expo_region = expo_region.drop(columns=["part_exposee"])
region_stats = region_stats.merge(expo_region, on="region", how="left")
region_stats.to_csv(OUT_DIR / "region_stats.csv", index=False)

# 12.10 Communautés Louvain (fichiers déjà fournis dans le projet, réintégrés tels quels)
louvain_cantons = pd.read_csv(RAW_DIR / "communautes_louvain_cantons.csv")
louvain_profil = pd.read_csv(RAW_DIR / "communautes_louvain_profil.csv")
louvain_cantons.to_csv(OUT_DIR / "louvain_cantons.csv", index=False)
louvain_profil.to_csv(OUT_DIR / "louvain_profil.csv", index=False)

# 12.11 Distribution / exploration stats (pour l'onglet exploration)
dist_export = gdf_fri[["region", "canton", "total_pop", "FRI", "max_fsi", "urban_ratio", "building_count", "min_rwi"]].copy()
dist_export.to_csv(OUT_DIR / "distributions.csv", index=False)

print("=== Export terminé ===")
for p in sorted(OUT_DIR.iterdir()):
    print(p.name, round(p.stat().st_size / 1024, 1), "Ko")
