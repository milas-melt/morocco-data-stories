import os
import pandas as pd

RAW_PATH = "data/primary_schools_2023.csv"
OUT_PATH = "data/education_access_2023.csv"


def build_education_access_2023():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"Raw file not found at {RAW_PATH}")

    # Read raw schools list
    df = pd.read_csv(RAW_PATH)

    print("Columns in raw file:", list(df.columns))

    # We expect REGION and NOM_ETABL to exist
    if "REGION" not in df.columns or "NOM_ETABL" not in df.columns:
        raise ValueError(
            f"Expected columns REGION and NOM_ETABL in {RAW_PATH}, "
            f"got: {list(df.columns)}"
        )

    # Standardise column names
    df = df.rename(columns={"REGION": "region", "NOM_ETABL": "school_name"})

    # Group by region and count schools
    agg = df.groupby("region").agg(total_schools=("school_name", "count")).reset_index()

    # Enrich with year + simple public/private fields
    agg["year"] = 2023
    agg["public_schools"] = agg["total_schools"]
    agg["private_schools"] = 0  # only public primaries in this file

    # Reorder columns
    agg = agg[["region", "year", "total_schools", "public_schools", "private_schools"]]

    os.makedirs("data", exist_ok=True)
    agg.to_csv(OUT_PATH, index=False)

    print("\nSaved aggregated dataset to", OUT_PATH)
    print("\nPreview:")
    print(agg.head())


if __name__ == "__main__":
    build_education_access_2023()
