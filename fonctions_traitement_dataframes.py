import pandas as pd
import numpy as np

# --- Mapping cohérent des colonnes ---
column_mapping = {
    'Name ': 'Formulation ID',
    'Test': 'Test protocol',
    'Temperature': 'Temperature [°C]',
    'Water hardness': 'Water hardness [°fH]',
    'Machine': 'Machine',
    'Country ': 'Country',
    'Dosage': 'Dosage [ml]',
    #'Sample n°': 'Lot', #pas du tout le même format

    "Grass pure CFT  CS07": "Mean_Grass",
    "Fluid make-up CFT CS17": "Mean_Fluid_Make_Up",
    "Soot / Mineral oil CFT C01s": "Mean_ Soot_ Mineral_Oil",
    "Bilberry juice CFT CS15": "Mean_Bilberry_Juice",
    "Chocolate drink pure CFT CS44": "Mean_Chocolate_Drink_Pure",
    "Oatmeal with chocolate CFT CS54": "Mean_Oatmeal_with_Chocolate",
    "Salad dressing CFT CS06": "Mean_ Salad_Dressing",
    "Rice starch CFT CS28": "Mean_Rice_Starch",
    "Lard CFT CS62": "Mean_Lard",
    "Red wine Equest WE5RWWKC": "Mean_Red_Wine",
    "Napolina tomato puree Equest WE5TPWKC": "Mean_Napolina_Tomato_Puree",
    "Cooked beef fat Equest WE5BBPC2": "Mean_Cooked_Beef_Fat",
    "Mustard Equest WE5FSMWKC": "Mean_Mustard",
    "Grass & mud Equest WE5GMWKC": "Mean_Grass&Mud",
    "Sheep's blood Equest WE5DASBWKC": "Mean_Sheeps_blood",
    "Tea Equest WE5LTWKC": "Mean-Tea",
    "Coffee WE5ECWKC": "Mean_Coffee",
    "Sebum & Carbon Black Equest- 146 KC": "Mean_Sebum",
    #"Lipstick CFT CH078": "Mean_Lipstick",  # à vérifier si la colonne existe, sinon à ajouter
    #"Green Pesto 1 - Equest 151 KC": "Mean_Green_Pesto",  # à vérifier si la colonne existe, sinon à ajouter
    #"Frying fat CFT CS46B": "Mean_Frying_Fat",  # à vérifier si la colonne existe, sinon à ajouter
    #"Dirty Motor oil  Equest 049 KC": "Mean_Dirty_Motor_Oil",  # à vérifier si la colonne existe, sinon à ajouter
    #"Face MakeUp 1 Equest- 144 KC": "Mean_Face_MakeUp_1",  # à vérifier si la colonne existe, sinon à ajouter
    "Soot / Mineral oil CFT C01s": "Mean_ Soot_ Mineral_Oil",
    #"Greasy & particulate stain removal average": "Mean_Greasy_Particulate_Stain_Removal_Avg",  # à vérifier si la colonne existe, sinon à ajouter
    #"Enzymatic stain removal average": "Mean_Enzymatic_Stain_Removal_Avg",  # à vérifier si la colonne existe, sinon à ajouter
    #"Oxydable stains removal stain": "Mean_Oxydable_Stains_Removal",  # à vérifier si la colonne existe, sinon à ajouter
    #"Average of Soil removal": "Mean_Soil_Removal_Avg",  # à vérifier si la colonne existe, sinon à ajouter
    "Anti-greying Cotton WFK10A": "Mean_Anti_greying_Cotton_WFK10A",
    "Anti-greying Polyester / Cotton WFK20A": "Mean_Anti_greying_Polyester_Cotton_WFK20A",
    "Anti-greying Polyester WFK30A": "Mean_Anti_greying_Polyester_WFK30A",
    "Anti-greying Poyamide WFK40A": "Mean_Anti_greying_Poyamide_WFK40A",
    "Average of Anti-greying (Y)": "Mean_Anti_greying_Y"
    # Ajoute ici les autres mappings si tu as d'autres taches ou moyennes à intégrer
}



def append_with_mapping(source_df, target_df, column_mapping):
    # 1. Renommer les colonnes du DataFrame source selon le mapping
    mapped_df = source_df.rename(columns=column_mapping)
    for col in mapped_df.columns:
        if col == "Dosage [ml]":
            mapped_df[col] = mapped_df[col].apply(lambda x: x.split()[0])
    # 2. Supprimer les colonnes dupliquées (garde la première occurrence)
    mapped_df = mapped_df.loc[:, ~mapped_df.columns.duplicated()]
    # 3. Réindexer pour avoir les colonnes dans le même ordre que le target (remplit les manquantes avec NaN)
    mapped_df = mapped_df.reindex(columns=target_df.columns)
    # 4. Concaténer les deux DataFrames
    result = pd.concat([target_df, mapped_df], ignore_index=True)
    return result


# Utilisation :
# result_database = transfer_data(df, template_database, mapping)


def add_comp_formulations(df, comp_formulations):
    for idx, row in comp_formulations.iterrows():
        formulation_id = row['Formulation ID']
        for col, val in row.items():
            if col != 'Formulation ID':
                # Teste si la cellule n’est PAS vide
                if pd.notna(val) and val not in ["", " ", None]:
                    df.loc[df['Formulation ID'] == formulation_id, col] = val
    return df