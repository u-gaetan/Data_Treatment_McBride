# webApp.py

import streamlit as st
import pandas as pd
from io import BytesIO
import re
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from tutoriel import render_tutoriel
from fonctions_traitement_dataframes import column_mapping, append_with_mapping
from fonctions_traitement_total_fichiers import traiter_performance_xls, traiter_formulation_xlsx

st.title("Traitement automatique des données de tests")
render_tutoriel()
uploaded_files = st.file_uploader(
    "Déposez vos fichiers ici",
    type=["xlsx", "xls", "pdf"],
    accept_multiple_files=True
)

name_database = "Database.xlsx"

if uploaded_files:
    liste_perf_dfs = []  # DFs issus des .xls
    liste_formul_dfs = []  # DFs issus des .xlsx
    file_database = None
    database = None

    # 1. Trouver la base et la charger (bytes + DataFrame)
    for file in uploaded_files:
        if file.name == name_database:
            file_database = file
            database_bytes = file.getvalue()
            database = pd.read_excel(BytesIO(database_bytes))
            break
    if file_database is None:
        st.error("Merci d'uploader le fichier de base de données.")
        st.stop()

    # Template vide aligné sur la base
    template_database = pd.DataFrame(columns=database.columns)

    # 2. Parcourir les autres fichiers pour les traiter
    for file in uploaded_files:
        if file.name == name_database:
            continue
        if file.name.lower().endswith(".pdf"):
            continue

        if file.name.lower().endswith(".xls"):
            try:
                perf_dfs = traiter_performance_xls(file, sheet_names=["AISE+"], search_value="Soil removal")
                liste_perf_dfs.extend(perf_dfs)
            except Exception as e:
                st.warning(f"Erreur traitement performances '{file.name}': {e}")

        elif file.name.lower().endswith(".xlsx"):
            try:
                # Crée une ligne alignée sur les colonnes du template et concatène
                row_df = traiter_formulation_xlsx(file, template_database.columns)
                liste_formul_dfs.append(row_df)
            except Exception as e:
                st.warning(f"Erreur traitement formulation '{file.name}': {e}")

    
    comp_formulations=pd.concat(liste_formul_dfs, ignore_index=True)
    

    # 3. Appliquer le mapping des performances au template
    for df in liste_perf_dfs:
        template_database = append_with_mapping(df, template_database, column_mapping)

    # 4. Nettoyage éventuel des colonnes "Unnamed: x"
    unnamed_pattern = r'^Unnamed:\s*\d+$'
    unnamed_cols = [c for c in template_database.columns if isinstance(c, str) and re.match(unnamed_pattern, c)]
    if unnamed_cols:
        template_database = template_database.drop(columns=unnamed_cols)

    template_database = pd.concat([template_database, comp_formulations])
    template_database = template_database.groupby("Formulation ID", as_index=False).first()

    # 5. Append du template dans la database existante (préservation de la mise en page)
    try:
        book = openpyxl.load_workbook(BytesIO(database_bytes))

        # S'assurer qu'au moins une feuille est visible
        visibles = [ws for ws in book.worksheets if ws.sheet_state == 'visible']
        if not visibles:
            book.worksheets[0].sheet_state = 'visible'
            book.active = 0
        ws = visibles[0] if visibles else book.worksheets[0]

        # Append des lignes du DataFrame (sans header/index)
        for row in dataframe_to_rows(template_database, index=False, header=False):
            if any(cell is not None and cell != "" for cell in row):
                ws.append(row)

        # Sauvegarde dans un buffer
        output = BytesIO()
        book.save(output)
        output.seek(0)

        st.download_button(
            label="Télécharger la nouvelle database",
            data=output,
            file_name="resultats.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="unique_download_button"
        )
    except Exception as e:
        st.error(f"Erreur lors de l'écriture dans la base: {e}")

else:
    st.info("Merci d'uploader les fichiers nécessaires au traitement.")
