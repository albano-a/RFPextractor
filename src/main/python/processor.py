import pandas as pd
import pdfplumber

START_TEXT = "(m³/dia) (kgf/cm²) (m)"
END_TEXT = "Temperaturas"


def extract_text_from_pdf(wellname, pdf_path, has_fluid=False):
    """extract text from 'Teste de Formação' to 'Temperaturas'"""

    extraction = ""
    start_extracting = False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if start_extracting:
                    if END_TEXT in text:
                        extraction += text[: text.index(END_TEXT)]
                        break
                    else:
                        extraction += text
                elif START_TEXT in text:
                    start_extracting = True
                    lines = text.split("\n")
                    for i, line in enumerate(lines):
                        if START_TEXT in line:
                            extraction += "\n".join(lines[i + 1 :])
                            break

                if page.extract_tables():
                    continue

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return

    extraction = extraction.replace(",", ".").replace(" ", ",")
    rows = extraction.split("\n")

    write_to_excel(wellname, rows, has_fluid)


def write_to_excel(wellname, rows, has_fluid=False):
    """Writes to excel"""
    try:
        data = [row.split(",") for row in rows]
        num_columns = max(len(row) for row in data) if data else 0

        if has_fluid is True:
            columns = [
                "Tipo",
                "Topo",
                "Base",
                "Vazao",
                "Fluido",
                "API",
                "Depl",
                "Pressao_Estatica",
                "Prof_Registrada",
            ]
        else:
            columns = [
                "Tipo",
                "Topo",
                "Base",
                "Vazao",
                "API",
                "Depl",
                "Pressao_Estatica",
                "Prof_Registrada",
            ]

        # Add generic names for additional columns
        for i in range(len(columns), num_columns):
            columns.append(f"Column_{i+1}")
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(f"{wellname}.xlsx", index=False)
    except Exception as e:
        print(f"Error writing to Excel: {e}")


extract_text_from_pdf("1-OGX-101-MA", "raw/1OGX101MA_CDPE_4_RFP.pdf")
extract_text_from_pdf("1-OGX-102-MA", "raw/1OGX102MA_CDPE_5_RFP.pdf")
extract_text_from_pdf("1-OGX-98-MA", "raw/1OGX98MA_CDPE_4_RFP.pdf")
