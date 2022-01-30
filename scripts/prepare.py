
import argparse
import pandas as pd

CONTINENT = "Europe"
COVID_COLUMNS = [
    "location",
    "date", 
    "new_cases_smoothed_per_million", 
    "new_deaths_smoothed_per_million", 
    "icu_patients_per_million", 
    "hosp_patients_per_million",
    "weekly_icu_admissions_per_million",
    "weekly_hosp_admissions_per_million", 
    "new_tests_smoothed_per_thousand",
    "new_vaccinations_smoothed_per_million",
    "hospital_beds_per_thousand"
]

def prepare_covid_data(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df[df["continent"] == CONTINENT][COVID_COLUMNS].copy()
    df.sort_values(by=["location", "date"], inplace=True)

    for col in ["new_vaccinations_smoothed_per_million", "new_cases_smoothed_per_million",
        "new_deaths_smoothed_per_million", "new_tests_smoothed_per_thousand"]:
        df[col].fillna(value=0, inplace=True)

    for col in ["icu_patients_per_million", "hosp_patients_per_million"]:
        # find out value and index for last date for each country and fill it
        for loc in df["location"].unique():
            subset = df[df["location"] == loc]
            subset_col = subset[col].fillna(method="pad")
            last_index = subset_col.index.to_list()[-1]
            last_val = subset_col.loc[last_index]
            df.loc[last_index, col] = last_val
        # backfill by using last data from newer dates
        # note that the latest date contains data filled from previous cycle
        df[col].fillna(method="backfill", inplace=True)

    for col in set([*df.columns]).difference({"location", "date"}):
        df[col] = df[col].apply(lambda v: 0 if v < 0 else v)
    return df

def main() -> None:

    parser = argparse.ArgumentParser(description="Remove processed hashes from csv")
    parser.add_argument(
        "input_csv_path",
        metavar="INPUT_CSV_PATH", 
        type=str, 
        help="path to csv file that contains information about cases, deaths and vaccination"
    )
    parser.add_argument(
        "output_csv_path",
        metavar="OUTPUT_CSV_PATH", 
        type=str, 
        help="path to csv file that contains information about cases, deaths and vaccination"
    )
    args = parser.parse_args()
    df = prepare_covid_data(pd.read_csv(args.input_csv_path))
    df.to_csv(args.output_csv_path, index=False)

if __name__ == "__main__":
    main()