"""Chargement et mise en cache des jeux de données précalculées de l'application."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "app_data"


@st.cache_data(show_spinner=False)
def load_cantons() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "cantons.csv")


@st.cache_data(show_spinner=False)
def load_cantons_geojson() -> dict:
    with open(DATA_DIR / "cantons.geojson", "r") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_tde_points() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "tde_points.csv")


@st.cache_data(show_spinner=False)
def load_coso_points() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "coso_points.csv")


@st.cache_data(show_spinner=False)
def load_coso_full() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "coso_full.csv")
    for c in ["launch_date", "expected_end_date", "work_completion_date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_predictions() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "predictions_retard.csv")


@st.cache_data(show_spinner=False)
def load_model_results() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "model_results.csv")


@st.cache_data(show_spinner=False)
def load_model_importance() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "model_importance.csv")


@st.cache_data(show_spinner=False)
def load_scenarios() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "scenarios.csv")


@st.cache_data(show_spinner=False)
def load_recommandations() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "recommandations.csv")


@st.cache_data(show_spinner=False)
def load_kpi_national() -> dict:
    with open(DATA_DIR / "kpi_national.json", "r") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_region_stats() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "region_stats.csv")


@st.cache_data(show_spinner=False)
def load_louvain_cantons() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "louvain_cantons.csv")


@st.cache_data(show_spinner=False)
def load_louvain_profil() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "louvain_profil.csv")


@st.cache_data(show_spinner=False)
def load_distributions() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "distributions.csv")


def logo_path() -> str:
    return str(DATA_DIR / "logo_ministere.png")
