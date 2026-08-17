import streamlit as st

from components import section_title
from theme import GREEN_DARK, GREEN, GOLD, GREY, BORDER, INK
from i18n import t


def render(state):
    st.write(t(
        "Ce tableau de bord a été conçu et développé dans le cadre du Data Challenge sur l'accès "
        "à l'eau potable au Togo, pour le compte du Ministère de l'Eau, de l'Assainissement et de "
        "l'Hydraulique Villageoise.",
        "This dashboard was designed and developed as part of the Data Challenge on drinking water "
        "access in Togo, on behalf of the Ministry of Water, Sanitation and Rural Water "
        "Engineering.",
    ))

    section_title(t("Auteur", "Author"))

    job_title = t("Ingénieur des Travaux Informatiques", "Computer Engineering Technologist")
    linkedin_label = t("LinkedIn : ", "LinkedIn: ")
    bio_text = t(
        "Passionné par la data et l'intelligence artificielle appliquées aux enjeux de développement, "
        "je m'attache à transformer des données brutes en leviers de décision concrets pour les "
        "acteurs publics et privés. Mon parcours en développement logiciel, en administration systèmes "
        "et réseaux, ainsi qu'en collecte de données biométriques et gestion de bases de données, "
        "nourrit aujourd'hui une spécialisation en science des données et big data, avec une attention "
        "particulière portée aux problématiques socio-économiques du contexte ouest-africain.",
        "Passionate about data and artificial intelligence applied to development challenges, I focus "
        "on turning raw data into concrete decision-making levers for public and private stakeholders. "
        "My background in software development, systems and network administration, as well as "
        "biometric data collection and database management, now feeds into a specialization in data "
        "science and big data, with a particular focus on the socio-economic challenges of the West "
        "African context.",
    )
    st.markdown(
        f"""
        <div style="background:white; border:1px solid {BORDER}; border-left:4px solid {GREEN};
                     border-radius:10px; padding:30px 36px; width:100%;">
            <div style="font-size:1.35rem; font-weight:800; color:{GREEN_DARK};">
                DAYO Kokou Cyrille
            </div>
            <div style="font-size:1rem; color:{GREY}; margin-top:4px; margin-bottom:18px;">
                {job_title}
            </div>
            <div style="font-size:0.92rem; color:{INK}; line-height:1.65; margin-bottom:20px; max-width:820px;">
                {bio_text}
            </div>
            <div style="font-size:0.88rem; color:{INK}; border-top:1px solid {BORDER}; padding-top:14px;">
                <b>{linkedin_label}</b>
                <a href="https://linkedin.com/in/dkc023" target="_blank" style="color:{GREEN}; text-decoration:none;">
                    linkedin.com/in/dkc023
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_title(t("À propos de ce tableau de bord", "About this dashboard"))
    st.write(t(
        "L'application s'appuie sur une analyse exploratoire des ouvrages hydrauliques recensés par "
        "la Togolaise des Eaux (TdE), des sous-projets du programme COSO et de l'indice de risque "
        "d'inondation (FRI) disponible pour les 388 cantons du pays. La méthodologie complète, les "
        "sources de données et les limites du diagnostic sont détaillées dans la page Méthodologie "
        "et limites, ainsi que dans le rapport d'analyse associé.",
        "The application is based on an exploratory analysis of water infrastructure recorded by "
        "Togolaise des Eaux (TdE), sub-projects of the COSO program, and the flood risk index (FRI) "
        "available for the country's 388 cantons. The full methodology, data sources and limitations "
        "of the diagnosis are detailed on the Methodology and limitations page, as well as in the "
        "associated analysis report.",
    ))
