import tabula
import pandas as pd
import re
import pdfplumber


def extract_vehicle_details(pdf_path):
    try:
        tables = tabula.read_pdf(pdf_path, pages=1)
        if not tables or len(tables) == 0:
            raise ValueError("No tables found in the PDF.")
        df = tables[0]
        vehicle_data = {
            "vin": str(df["VIN"][0]) if "VIN" in df.columns else None,
            "make_code": str(df["Make Code"][0]) if "Make Code" in df.columns else None,
            "fuel_type": str(df["Fuel Type"][0]) if "Fuel Type" in df.columns else None,
            "mfg_year": int(df["Mfg Year"][0]) if "Mfg Year" in df.columns else None,
            "engine_number": (
                str(df["Engine Number"][0]) if "Engine Number" in df.columns else None
            ),
        }

        with pdfplumber.open(pdf_path) as pdf:
            other_data = pdf.pages[0].extract_text()
            if "Customer" in other_data and "Name" in other_data:
                pattern = r"Customer Name:\s*(.*)"

                # Search for the pattern in the text
                match = re.search(pattern, other_data)

                # If a match is found, return the captured group, otherwise return None
                if match:
                    customer_name = match.group(1).strip()
                    customer_name = customer_name.replace("\u0000", "")

                    prefix = None
                    customer_name = customer_name.upper()
                    if customer_name.startswith("MR"):
                        prefix = "MR"
                        customer_name = customer_name.replace("MR", "")
                        customer_name = customer_name.replace(".", "")
                        customer_name = customer_name.strip()
                    if customer_name.startswith("MS"):
                        prefix = "MS"
                        customer_name = customer_name.replace("MS", "")
                        customer_name = customer_name.replace(".", "")
                        customer_name = customer_name.strip()

                    vehicle_data["prefix"] = prefix
                    vehicle_data["customerName"] = customer_name

        return vehicle_data
    except Exception as e:
        raise
