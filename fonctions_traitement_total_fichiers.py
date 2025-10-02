# traitements_fichiers.py

from io import BytesIO
from typing import List, Sequence
import pandas as pd
import xlrd

from fonctions_traitement_excel import find_cell_by_value, extract_table_from_position

def traiter_performance_xls(uploaded_file,
                            sheet_names: List[str] | None = None,
                            search_value: str = "Soil removal") -> List[pd.DataFrame]:
    """
    Traite un fichier .xls (performances AISE+):
    - Extrait le tableau principal autour de 'search_value'
    - Extrait le tableau 'Name '
    - Fusionne et ajoute les métadonnées (Test, Temperature, etc.)
    Retourne une liste de DataFrames finalisés (un par feuille traitée).
    """
    if sheet_names is None:
        sheet_names = ["AISE+"]

    xls_bytes = uploaded_file.getvalue()
    wb = xlrd.open_workbook(file_contents=xls_bytes)

    dataframes_main: List[pd.DataFrame] = []
    dataframes_name: List[pd.DataFrame] = []

    # Liste des métadonnées à récupérer hors tableau
    name_values = [
        "Test", "Temperature", "Water hardness", "Machine", "Programme",
        "Drying", "Duration of the cycle", "Charge", "Name "
    ]
    # Une liste de valeurs par feuille (hors 'Name ')
    liste_values_for_test = [[] for _ in sheet_names]

    # 1) Extraction des blocs et des métadonnées
    for idx, sheet in enumerate(sheet_names):
        ws = wb.sheet_by_name(sheet)

        # Tableau principal (autour de search_value)
        (row, col) = find_cell_by_value(ws, search_value)
        if row is not None and col is not None:
            dataframes_main.append(extract_table_from_position(ws, row, col))
        else:
            # Si non trouvé, on ignore cette feuille
            continue

        # Tableau "Name " + métadonnées
        for name_value in name_values:
            (r, c) = find_cell_by_value(ws, name_value)
            if (r, c) == (None, None):
                continue
            if name_value == "Name ":
                dataframes_name.append(extract_table_from_position(ws, r, c))
            else:
                liste_values_for_test[idx].append(ws.cell_value(r, c + 1))

    # 2) Construction de la liste finale (fusion + méta)
    liste_finale: List[pd.DataFrame] = []
    for k in range(len(dataframes_main)):
        df_main = dataframes_main[k]
        df_name = dataframes_name[k]

        # Transpose + reset index pour transformer le tableau principal
        transposed = df_main.transpose()
        transposed_reset = transposed.reset_index()
        transposed_reset.columns = transposed_reset.iloc[0]
        transposed_reset = transposed_reset.rename(columns={'Soil removal': 'Name '})

        # Fusion sur 'Name '
        final_df = pd.merge(df_name, transposed_reset, on='Name ', how='left')
        final_df = final_df.drop(index=0).reset_index(drop=True)
        final_df = final_df.drop(final_df[final_df['Name ']=="Ref powder"].index).reset_index(drop=True)

        # Ajout des métadonnées (hors "Name ")
        meta_vals = [str(x).lstrip(': ').strip() for x in liste_values_for_test[k]]
        meta_keys = name_values[:-1]
        for key, val in zip(meta_keys, meta_vals):
            final_df[key] = val

        liste_finale.append(final_df)

    return liste_finale


def traiter_formulation_xlsx(uploaded_file,
                             template_columns: Sequence[str]) -> pd.DataFrame:
    """
    Traite un fichier .xlsx de formulation pour produire UNE ligne alignée
    sur les colonnes de la database (template_columns).

    Règle de mappage:
    - Pour chaque 'Component number' (colonne du fichier), on cherche une colonne
      du template dont le nom contient ce numéro (en substring) et on y place
      'Comp. Qty (BUn)'.
    - Les colonnes non trouvées restent vides (NaN).

    Retourne: un DataFrame d'une seule ligne, colonnes = template_columns.
    """
    df = pd.read_excel(uploaded_file)
    # Sécurise les colonnes attendues
    needed = ["Component number", "Comp. Qty (BUn)"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans la formulation: {missing}")

    # Démarre une ligne vide
    row_dict = {col: pd.NA for col in template_columns}

    # Ajoute l'ID (nom du fichier)
    row_dict["Formulation ID"] = int(uploaded_file.name.replace(".xlsx", ""))

    for _, r in df[needed].iterrows():
        comp = r["Component number"]
        qty = r["Comp. Qty (BUn)"]
        # comp peut être float; on force un str propre
        try:
            comp_str = str(int(comp))
        except Exception:
            comp_str = str(comp)

        # cherche une colonne contenant le numéro
        for col in template_columns:
            if comp_str in str(col):
                row_dict[col] = qty
                break
    


    return pd.DataFrame([row_dict], columns=template_columns)
