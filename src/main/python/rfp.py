"""
Reads tables from the final well report (RFP)
"""

import os

# import shutil
from io import StringIO
import pandas as pd
import pdfplumber

ROOT_PATH = "C:/Users/Icarl/Desktop/Data"

if not os.path.isdir(ROOT_PATH):
    dirs = ["raw", "processed"]
    for item in dirs:
        path = os.path.join(ROOT_PATH, item)
        os.makedirs(path)

# Diretório em sua estação de trabalho ou desktop local onde
# serão armazenadas as cópias dos arquivos AGP/RFP
rawdir = os.path.join(ROOT_PATH, "raw")

# Diretório em sua estação de trabalho ou desktop local onde serão armazenadas os arquivos
# no formato para importação das litologias para os softwares de interpretação
processeddir = os.path.join(ROOT_PATH, "processed")


def get_valid_rows(filename):
    """Extracts and returns specific text from a PDF"""

    with pdfplumber.open(filename) as pdf:
        data = []
        for num_page, page in enumerate(pdf.pages, start=0):
            text_page = page.extract_text()
            # var_page = f'{num_page}'
            # data = f'Página {num_page}:\n{text_page}\n'
            if "Topos Estratigráficos" in text_page:
                start_read = text_page.find("Topos Estratigráficos")
                stop_read = text_page.find(
                    "Indícios de Petróleo e/ou Gás",
                    start_read + len("Topos Estratigráficos"),
                )
                if stop_read == -1:
                    info = text_page[start_read:]
                else:
                    info = text_page[start_read:stop_read]
                return info


# variável onde os arquivos a serem usados serão guardados
paths = ["C:/Users/Icarl/Desktop/Data/raw/1OGX101MA_CDPE_4_RFP.pdf"]
wells = ["1-OGX-101-MA"]

# Para fins estatísticos
success = {}
fail = {}

newfiles = []
for file, well in zip(paths, wells):
    data = get_valid_rows(file)
    newpath = f'processed/{os.path.basename(file.replace(".pdf",".tab"))}'
    if data:
        if data.count("\n") > 4:
            df = pd.read_csv(
                StringIO(data.replace(".", "").replace(",", ".")),
                header=None,
                skiprows=4,
            )
            df["Well"] = well
            df["Surface"] = df[0].apply(lambda x: x[: x.find(x.split()[-4])])
            df["MD"] = pd.to_numeric(
                df[0].apply(lambda x: x.split()[-2]), errors="coerce"
            )
            df2 = df[["Well", "Surface", "MD"]].query('"SDT" not in Surface').dropna()
            df2.to_csv(newpath, sep="\t", index=False)
            success[file] = well
            newfiles.append(newpath)
        else:
            fail[file] = well
    else:
        fail[file] = well

DF = None
for file in newfiles:
    df_i = pd.read_csv(file, sep="\t")
    if DF is None:
        DF = df_i
    else:
        DF = pd.concat([DF, df_i])

# df_final = df.dropna().query('"" not in Surface').reset_index(drop=True)
df_final = DF.dropna().reset_index(drop=True)
df_final.to_csv("formation_tops_petrel.tab", sep="\t", index=False)
