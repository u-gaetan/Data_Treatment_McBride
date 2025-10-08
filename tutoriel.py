import streamlit as st
def render_tutoriel(): st.markdown(""" 
## Explications d’utilisation
Déposez dans la zone ci-dessous l’ensemble des fichiers nécessaires.
Lancer le traitement puis vous pourrez télécharger la nouvelle base de données.
### Fichiers attendus
- 1 fichier de la base de données (database), au format Excel moderne:
  - Nom exact: `Database.xlsx`
  - Type: `.xlsx`
- les fichiers de performances de tests:
  - Type: `.xls` ,seul la première feuille est lue (nommée `AISE+`)
- les fichiers de compositions de formulations (souvent plusieurs pour 1 fichier de performances):
  - Type: `.xlsx` ou `.XLSX`
  - Nom de fichier = identifiant de la formulation: `17XXXXXX.xlsx` ou `16XXXXXX.xlsx` 
    (par exemple: `17083746.xlsx`, `16140844.xlsx`)
""")