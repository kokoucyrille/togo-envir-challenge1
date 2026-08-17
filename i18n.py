"""Aide légère pour la bascule de langue Français / Anglais de l'application.

Usage : t("Texte en français", "Text in English") retourne la version
correspondant à la langue active, stockée dans st.session_state["lang"].
"""
import streamlit as st

LANGUAGES = {"fr": "Français", "en": "English"}
DEFAULT_LANG = "fr"


def get_lang() -> str:
    return st.session_state.get("lang", DEFAULT_LANG)


def set_lang(lang: str):
    st.session_state["lang"] = lang


def t(fr: str, en: str) -> str:
    """Retourne le texte français ou anglais selon la langue active."""
    return en if get_lang() == "en" else fr


# Traductions des valeurs de données récurrentes (segments, colonnes, etc.)
# utilisées pour l'affichage, sans modifier les fichiers de données sources.
# NB : les clés (côté français) reproduisent volontairement l'orthographe sans
# accent des données sources (CSV), afin que la correspondance de recherche
# (mapping.get) fonctionne. Ne pas les accentuer sans mettre à jour les CSV.
SEGMENT_LABELS_EN = {
    "Nouveaux ouvrages prioritaires": "Priority new infrastructure",
    "Maintenance et renforcement urgents": "Urgent maintenance & reinforcement",
    "Renforcement (vulnerabilite aux inondations)": "Reinforcement (flood vulnerability)",
    "Renforcement (vulnerabilite inondation)": "Reinforcement (flood vulnerability)",
    "Surveillance": "Monitoring",
}

SEGMENT_SHORT_LABELS_EN = {
    "Nouveaux ouvrages prioritaires": "New infrastructure",
    "Maintenance et renforcement urgents": "Urgent maintenance",
    "Renforcement (vulnerabilite aux inondations)": "Reinforcement (flooding)",
    "Surveillance": "Monitoring",
}

STADE_LABELS_EN = {
    "Reception definitive": "Final acceptance",
    "Reception provisoire": "Provisional acceptance",
    "En cours": "In progress",
    "Non demarre": "Not started",
}

NIVEAU_RISQUE_LABELS_EN = {
    "Faible": "Low",
    "Modere": "Moderate",
    "Eleve": "High",
}

PRIORITE_LABELS_EN = {
    "Haute": "High",
    "Moyenne": "Medium",
    "Basse": "Low",
}


def translate_value(value: str, mapping: dict) -> str:
    """Traduit une valeur de donnée (segment, stade, etc.) si la langue est EN."""
    if get_lang() == "en":
        return mapping.get(value, value)
    return value


def translate_series(series, mapping: dict):
    """Traduit une colonne pandas entière (copie) si la langue est EN."""
    if get_lang() == "en":
        return series.map(lambda v: mapping.get(v, v))
    return series
