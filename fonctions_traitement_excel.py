import xlrd
import pandas as pd

def find_cell_by_value(ws, search_value):
    for row_idx in range(ws.nrows):
        for col_idx in range(ws.ncols):
            if search_value in str(ws.cell_value(row_idx, col_idx)):
                return row_idx, col_idx
    return None, None

def extract_table_from_position(ws, start_row, start_col):

    
    # Trouver la dernière colonne de l'en-tête (vers la droite, à partir de start_col)
    end_col = start_col
    
    while end_col < ws.ncols and (ws.cell_value(start_row, end_col) not in (None, "", " ") or end_col<(start_col +3)):
        end_col += 1
    end_col -= 1

    # Trouver la dernière ligne (vers le bas, à partir de start_row+1)
    end_row = start_row + 1
    while end_row < ws.nrows and (ws.cell_value(end_row, start_col) not in (None, "", " ") or end_row<start_row+2):
        end_row += 1
    end_row -= 1

    # Extraire les données du tableau complet (rectangle)
    data = []
    for r in range(start_row, end_row + 1):
        row_data = []
        for c in range(start_col, end_col + 1):
            row_data.append(ws.cell_value(r, c))
        data.append(row_data)

    # Créer le DataFrame
    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
    else:
        df = pd.DataFrame()
    return df