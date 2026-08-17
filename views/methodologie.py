import streamlit as st

from components import section_title, warn_box, note_box
from i18n import t, get_lang


def render(state):
    st.write(t(
        "Cette page documente, de manière transparente, les sources de données utilisées, la méthode de "
        "construction des indicateurs, ainsi que les limites et hypothèses du diagnostic présenté dans ce "
        "tableau de bord. Elle reprend la structure du notebook d'analyse exploratoire qui constitue le socle "
        "analytique de ce dashboard.",
        "This page transparently documents the data sources used, the method for building the indicators, "
        "and the limitations and assumptions of the diagnosis presented in this dashboard. It follows the "
        "structure of the exploratory analysis notebook that forms the analytical basis of this dashboard.",
    ))

    section_title(t("Sources de données utilisées", "Data sources used"))
    if get_lang() == "en":
        st.markdown(
            """
| Dataset | Format | Content | Coverage |
|---|---|---|---|
| TdE points (Togolaise des Eaux) | CSV, WKT geometry | Water towers and boreholes managed by the national operator | 67 points, over 97% concentrated in the Maritime region |
| COSO sub-projects | CSV + GeoJSON | Water investments financed by the World Bank | 218 sub-projects, 83 validly geolocated (159 non-null coordinates, of which 76 invalid or placeholder) |
| Canton FRI (flood risk index) | GeoPackage | Flood risk, population, vulnerability per canton | 388 cantons, full national coverage |
| TdE consumption | CSV | Water volumes by user category, 2018-2022 | National context only, not territorialized |
| Population by locality | CSV | Census by locality | Single year (2010), cannot be reliably re-aggregated |
| Contiguity communities (Louvain) | CSV | Grouping of cantons by territorial proximity | Complementary exploratory analysis |
            """
        )
    else:
        st.markdown(
            """
| Jeu de données | Format | Contenu | Couverture |
|---|---|---|---|
| Points TdE (Togolaise des Eaux) | CSV, géométrie WKT | Châteaux d'eau et forages gérés par l'opérateur national | 67 points, concentrés à plus de 97% en région Maritime |
| Sous-projets COSO | CSV + GeoJSON | Investissements hydrauliques financés par la Banque mondiale | 218 sous-projets, 83 valablement géolocalisés (159 coordonnées non nulles, dont 76 invalides ou placeholders) |
| FRI cantons (indice de risque d'inondation) | GeoPackage | Risque d'inondation, population, vulnérabilité par canton | 388 cantons, couverture nationale complète |
| Consommation TdE | CSV | Volumes d'eau par catégorie d'usager, 2018-2022 | Contexte national uniquement, non territorialisé |
| Population par localité | CSV | Recensement par localité | Année unique (2010), non réagrégeable de manière fiable |
| Communautés de contiguïté (Louvain) | CSV | Regroupement des cantons par proximité territoriale | Analyse complémentaire exploratoire |
            """
        )

    section_title(t("Méthode de construction du Water Infrastructure Priority Score",
                     "Method for building the Water Infrastructure Priority Score"))
    if get_lang() == "en":
        st.markdown(
            """
The priority score (0 to 100) is calculated for each of the 388 cantons by combining five normalized
components (min-max, 0 to 1) and then weighting them:

- **Current demographic pressure** (30%) — canton population relative to the number of documented infrastructure units.
- **Flood risk (FRI)** (25%) — the canton's composite index.
- **Socio-economic vulnerability** (15%) — inverted relative wealth index (RWI): the lower the canton's
  minimum RWI, the higher the vulnerability is considered to be.
- **Weakness of documented coverage** (20%) — inverted number of documented infrastructure units per 10,000 inhabitants.
- **Absolute demographic weight** (10%) — total population of the canton.

These weights are an explicit, adjustable methodological choice that favors relative pressure and risk over
population size alone, so as not to systematically prioritize the Lome agglomeration. They should be
validated with the Ministry in charge of the water sector before any operational use.

The segmentation into four action categories (Priority new infrastructure, Urgent maintenance and
reinforcement, Reinforcement related to flood vulnerability, Monitoring) combines median demographic
pressure, median flood risk, and the presence or absence of documented infrastructure in the canton.
            """
        )
    else:
        st.markdown(
            """
Le score de priorité (0 à 100) est calculé pour chacun des 388 cantons en combinant cinq composantes
normalisées (min-max, 0 à 1) puis pondérées :

- **Pression démographique actuelle** (30 %) — population du canton rapportée au nombre d'ouvrages documentés.
- **Risque d'inondation (FRI)** (25 %) — indice composite du canton.
- **Vulnérabilité socio-économique** (15 %) — indice de richesse relative (RWI) inversé : plus le RWI minimal
  du canton est bas, plus la vulnérabilité est considérée comme forte.
- **Faiblesse de la couverture documentée** (20 %) — nombre d'ouvrages documentés pour 10 000 habitants, inversé.
- **Poids démographique absolu** (10 %) — population totale du canton.

Ces pondérations sont un choix méthodologique explicite et modifiable, qui privilégie la pression relative et
le risque plutôt que la seule taille de la population, afin de ne pas systématiquement prioriser
l'agglomération de Lomé. Elles devraient être validées avec le Ministère en charge du secteur eau avant tout
usage opérationnel.

La segmentation en quatre catégories d'action (Nouveaux ouvrages prioritaires, Maintenance et renforcement
urgents, Renforcement lié à la vulnérabilité aux inondations, Surveillance) croise la pression démographique
médiane, le risque d'inondation médian, et la présence ou l'absence d'ouvrage documenté dans le canton.
            """
        )

    section_title(t("Limites et transparence — à lire avant toute décision",
                     "Limitations and transparency — read before any decision"))
    warn_box(t(
        "Les deux jeux de données d'ouvrages géolocalisés (TdE, COSO) couvrent un nombre restreint d'ouvrages "
        "(67 et 218) au regard des 388 cantons du pays : ils ne constituent pas un inventaire exhaustif du parc "
        "hydraulique national. L'absence d'ouvrage documenté dans un canton peut refléter un véritable déficit "
        "ou un simple défaut de répertoriage des données disponibles.",
        "The two geolocated infrastructure datasets (TdE, COSO) cover a limited number of facilities (67 and "
        "218) relative to the country's 388 cantons: they do not constitute an exhaustive inventory of the "
        "national water infrastructure stock. The absence of documented infrastructure in a canton may reflect "
        "a genuine deficit or simply a gap in the available data's cataloging.",
    ))
    if get_lang() == "en":
        st.markdown(
            """
**Data quality and coverage**
- The operational status field (functional / broken down / abandoned) announced in the TdE field dictionary
  provided is absent from the data actually delivered. No reliable failure-rate or abandonment analysis could
  therefore be produced; an alternative (COSO sub-project commissioning delay risk) is proposed instead.
- The `canton` field of the COSO file is missing for most sub-projects; geographic coordinates are missing or
  invalid (placeholder values close to 0,0) for 135 of the 218 sub-projects (62%), which strongly reduces the
  effective coverage of spatial analyses on COSO sub-projects: only 83 sub-projects are validly geolocated.
- Population by locality (census) is only available for the year 2010, with no possibility of a reliable
  growth-rate calculation or demographic projection. The `total_pop` population of the canton FRI layer is a
  composite estimate whose construction method and reference year are not documented in the files provided.

**Potential biases**
- The priority score and maps may underestimate actual coverage in regions outside Maritime, or by operators
  other than TdE (rural water systems, NGOs, village water points), which are not represented in these
  datasets.
- Using the absence of documented infrastructure as a proxy for deficit may, in some cantons, reflect a mere
  cataloging gap rather than an actual absence of infrastructure on the ground.

**Model limitations**
- The COSO sub-project delay risk model is trained on a limited sample size (a few hundred rows at most) and
  should be considered indicative, not operational as is.
- The sensitivity scenarios on water pressure are simulations based on explicit assumptions, not statistical
  projections derived from real time series.

**Assumptions made**
- The high flood risk threshold is defined as the upper quartile (75th percentile) of the national FRI; this
  choice is arbitrary and adjustable.
- No value is invented to fill missing fields (operational status, demographic projection): when the requested
  analysis cannot be reliably carried out, this dashboard states so explicitly rather than producing an
  unfounded figure.

No indicator or prediction presented in this dashboard should be read as an absolute certainty.
            """
        )
    else:
        st.markdown(
            """
**Qualité et couverture des données**
- Le champ d'état de fonctionnement (fonctionnel / en panne / abandonné) annoncé dans le dictionnaire de
  champs TdE fourni est absent des données effectivement livrées. Aucune analyse de taux de panne ou
  d'abandon fiable n'a donc pu être produite ; une alternative (risque de retard de mise en service des
  sous-projets COSO) est proposée à la place.
- Le champ `canton` du fichier COSO est manquant pour la majorité des sous-projets ; les
  coordonnées géographiques sont manquantes ou invalides (valeurs placeholders proches de 0,0) pour 135 des
  218 sous-projets (62%), ce qui réduit fortement la couverture effective des analyses spatiales sur les
  sous-projets COSO : seuls 83 sous-projets sont valablement géolocalisés.
- La population par localité (recensement) n'est disponible que pour l'année 2010, sans possibilité de calcul
  de taux de croissance ni de projection démographique fiable. La population `total_pop` de la couche FRI
  cantons est une estimation composite dont la méthode de construction et l'année de référence ne sont pas
  documentées dans les fichiers fournis.

**Biais potentiels**
- Le score de priorité et les cartes peuvent sous-estimer la couverture réelle des régions hors Maritime, où
  des opérateurs autres que TdE (adductions rurales, ONG, points d'eau villageois) ne sont pas représentés
  dans ces jeux de données.
- L'usage de l'absence d'ouvrage documenté comme proxy de déficit peut, dans certains cantons, refléter un
  simple défaut de répertoriage plutôt qu'une absence réelle d'infrastructure sur le terrain.

**Limites des modèles**
- Le modèle de risque de retard des sous-projets COSO est entraîné sur un échantillon de taille limitée
  (quelques centaines de lignes au maximum) et doit être considéré comme indicatif, non opérationnel en l'état.
- Les scénarios de sensibilité sur la pression hydraulique sont des simulations basées sur des hypothèses
  explicites, non des projections statistiques issues de séries temporelles réelles.

**Hypothèses retenues**
- Le seuil de risque d'inondation élevé est défini comme le quartile supérieur (75e percentile) du FRI
  national ; ce choix est arbitraire et modifiable.
- Aucune valeur n'est inventée pour combler les champs manquants (état de fonctionnement, projection
  démographique) : lorsque l'analyse demandée n'est pas réalisable de manière fiable, ce tableau de bord
  l'indique explicitement plutôt que de produire un chiffre non fondé.

Aucun indicateur ou prédiction présenté dans ce tableau de bord ne doit être lu comme une certitude absolue.
            """
        )

    section_title(t("Démarche générale", "General approach"))
    note_box(t(
        "Données -&gt; Audit -&gt; Nettoyage -&gt; Diagnostic -&gt; Croisements -&gt; Analyse spatiale -&gt; "
        "Explication -&gt; Modélisation -&gt; Priorisation -&gt; Recommandations. ",
        "Data -&gt; Audit -&gt; Cleaning -&gt; Diagnosis -&gt; Cross-analysis -&gt; Spatial analysis -&gt; "
        "Explanation -&gt; Modeling -&gt; Prioritization -&gt; Recommendations. ",
    ))
