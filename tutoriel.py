import streamlit as st
def render_tutoriel(): st.markdown(""" 
## Explications d’utilisation
Déposez dans la zone ci-dessous l’ensemble des fichiers nécessaires.
L’application détecte les fichiers et lance le traitement automatiquement, puis vous propose la nouvelle base à télécharger.
### Fichiers attendus
- 1 fichier de base (database), au format Excel moderne:
  - Nom exact: `Database.xlsx`
  - Type: `.xlsx`
- les fichiers de performances de tests:
  - Type: `.xls` (AISE+)
- les fichiers de compositions de formulations (souvent 4 pour 1 fichier de performances):
  - Type: `.xlsx`
  - Nom de fichier = identifiant de la formulation: `17XXXXXX.xlsx` ou `16XXXXXX.xlsx`
    (par exemple: `17083746.xlsx`, `16140844.xlsx`)
""")