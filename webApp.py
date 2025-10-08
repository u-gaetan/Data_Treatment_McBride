# webApp.py

import streamlit as st
import pandas as pd
from io import BytesIO
import re
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

# Vos modules existants
from tutoriel import render_tutoriel
from fonctions_traitement_dataframes import column_mapping, append_with_mapping, add_comp_formulations
from fonctions_traitement_total_fichiers import traiter_performance_xls, traiter_formulation_xlsx

st.title("McBride - Traitement automatique des données de tests")
render_tutoriel()

uploaded_files = st.file_uploader(
    "Déposez vos fichiers ici",
    type=["xlsx","XLSX","xls", "pdf"],
    accept_multiple_files=True
)

name_database = "Database.xlsx"

# Activer le bouton dès qu'au moins la database est présente
has_db = False
if uploaded_files:
    names = [f.name for f in uploaded_files]
    has_db = name_database in names

process_clicked = st.button("Lancer le traitement", type="primary", disabled=not has_db)

if not uploaded_files:
    st.info(f"Uploadez au minimum la base {name_database}, puis cliquez sur Lancer le traitement.")
elif not has_db:
    st.warning(f"Fichier {name_database} manquant. Merci de l'uploader.")
else:
    st.caption("Cliquez sur Lancer le traitement pour démarrer.")

if uploaded_files and process_clicked:
    with st.spinner("Traitement en cours..."):
        liste_perf_dfs = []   # DFs issus des .xls
        liste_formul_dfs = [] # DFs issus des .xlsx
        file_database = None
        database = None
        database_bytes = None

        # 1) Charger la base
        for file in uploaded_files:
            if file.name == name_database:
                file_database = file
                database_bytes = file.getvalue()
                database = pd.read_excel(BytesIO(database_bytes))
                break

        if file_database is None:
            st.error(f"Merci d'uploader le fichier de base {name_database}.")
            st.stop()

        # Template vide aligné sur la base
        template_database = pd.DataFrame(columns=database.columns)

        # 2) Parcourir les autres fichiers
        for file in uploaded_files:
            if file.name == name_database:
                continue
            if file.name.lower().endswith(".pdf"):
                continue

            if file.name.lower().endswith(".xls"):
                # Performances
                try:
                    perf_dfs = traiter_performance_xls(file, sheet_names=["AISE+"], search_value="Soil removal")
                    # Conserver toutes les lignes de perfs (pas de déduplication)
                    liste_perf_dfs.extend(perf_dfs)
                except Exception as e:
                    st.warning(f"Erreur traitement performances '{file.name}': {e}")

            elif file.name.lower().endswith(".xlsx"):
                # Formulations -> une ligne alignée sur la DB (doit inclure 'Formulation ID')
                try:
                    row_df = traiter_formulation_xlsx(file, template_database.columns)
                    liste_formul_dfs.append(row_df)
                except Exception as e:
                    st.warning(f"Erreur traitement formulation '{file.name}': {e}")
        if liste_formul_dfs:
            comp_formulations=pd.concat(liste_formul_dfs, ignore_index=True)
        else:
            comp_formulations = pd.DataFrame(columns=template_database.columns)

        # 3) Appliquer le mapping des perfs vers template (append sans regrouper)
        for df in liste_perf_dfs:
            template_database = append_with_mapping(df, template_database, column_mapping)

        # 4) Nettoyer les colonnes "*Unnamed: x"
        unnamed_pattern = r'^Unnamed:\s*\d+$'
        unnamed_cols = [c for c in template_database.columns if isinstance(c, str) and re.match(unnamed_pattern, c)]
        if unnamed_cols:
            template_database = template_database.drop(columns=unnamed_cols)

        template_database = add_comp_formulations(template_database, comp_formulations)


        # 6) Écrire dans la base existante (préserver la mise en page)
        try:
            book = openpyxl.load_workbook(BytesIO(database_bytes))

            # S'assurer qu'au moins une feuille est visible
            visibles = [ws for ws in book.worksheets if ws.sheet_state == 'visible']
            if not visibles:
                book.worksheets[0].sheet_state = 'visible'
                book.active = 0
            ws = visibles[0] if visibles else book.worksheets[0]

            # Append des lignes du DataFrame (sans header/index)
            added_rows = 0
            for row in dataframe_to_rows(template_database, index=False, header=False):
                if any(cell is not None and cell != "" for cell in row):
                    ws.append(row)
                    added_rows += 1

            output = BytesIO()
            book.save(output)
            output.seek(0)

            if added_rows == 0:
                st.warning("Aucune ligne à ajouter (aucun fichier perfs/formulations ou aucun mappage réussi).")

            st.success("Traitement terminé.")
            st.download_button(
                label="Télécharger la nouvelle database",
                data=output,
                file_name="resultats.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="unique_download_button"
            )
        except Exception as e:
            st.error(f"Erreur lors de l'écriture dans la base: {e}")
