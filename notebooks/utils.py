# Standard Library
import os
from pathlib import Path
from typing import List

# Third Party
import numpy as np
import pandas as pd


def dataframe_from_folder_of_csv(folder_path: Path, column_headings: List[str]) -> pd.DataFrame:
    """Iterate over all CSVs in a folder and concatenate them together."""

    return pd.concat(
        [
            pd.read_csv(f"{folder_path / file}", parse_dates=True, names=column_headings).assign(filename=file)
            for file in os.listdir(folder_path)
        ]
    )


def load_transactions(folder_path: Path) -> pd.DataFrame:
    column_headings = ["date", "amount", "desc", "balance"]
    df = dataframe_from_folder_of_csv(folder_path, column_headings)
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Remove income and transfers
    df = df[df.amount < 0]

    df = filter_by_prefix(df)
    df = strip_description_noise(df)
    # df = strip_description_locations(df)

    return df


def filter_by_prefix(df: pd.DataFrame) -> pd.DataFrame:
    # Remove other specific transactions
    prefixes_to_filter = [
        "Transfer",
        "Salary",
        "Direct Credit",
        "Wdl ATM CBA",
        "Home Loan Pymt",
        "Refund Purchase Medicare Benefit",
        "Refund Purchase MEDICARE BENEFIT",
        "Direct Debit 617704 PAYPAL AUSTRALIA",
    ]
    for k in prefixes_to_filter:
        df = df[~df.desc.str.startswith(k)]

    return df


def strip_description_noise(df: pd.DataFrame) -> pd.DataFrame:
    # Tidy up descriptions
    desc_filters = [
        " Card xx\d\d\d\d",
        " Value Date: \d\d/\d\d/\d\d\d\d",
        " \d\d+",
        "Direct Debit ",
        " AUS",
        " AU",
        " NS",
        " NSWAU",
    ]
    for f in desc_filters:
        df.desc = df.desc.str.replace(f, "", regex=True)

    df.desc = df.desc.str.replace(f"  ", " ")
    return df


def strip_description_locations(df: pd.DataFrame) -> pd.DataFrame:
    suburb_list = list(pd.read_csv(Path("../assets/suburbs.csv")).suburb)
    df.desc = df.desc.str.upper()  # case normalise first

    for suburb in suburb_list:
        df.desc = df.desc.str.replace(suburb.upper(), "")

    df.desc = df.desc.str.replace(f"  ", " ")
    return df


def deduplicate_transactions(df: pd.DataFrame) -> pd.DataFrame:
    tdf = (
        df.groupby(by=["date", "desc", "amount", "balance"])
        .agg(count_desc=("desc", "count"), dist_files=("filename", "nunique"))
        .reset_index()
    )

    print(
        f"Found {len(tdf[tdf.count_desc > 1])} duplicated entries \nand {len(tdf[(tdf.count_desc > 1) & (tdf.dist_files == 1)])} duplicates on the same day from the same file."
    )

    tdf = tdf.drop("count_desc", axis=1)
    return tdf


def classify_transactions(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(classification=pd.Series(df.desc.map(classify_transaction)))


def classify_transaction(transaction_description: str):
    output = transaction_description

    # Hard coded rules
    if not transaction_description.startswith("COLES EXPRESS") and any(
        [
            transaction_description.startswith(k)
            for k in [
                "COLES",
                "WOOLWORTHS",
                "RITCHIES SUPA IGA",
                "THE ESSENTIAL INGRED",
                "BWS LIQUOR",
                "HARRIS FARM MARKETS",
            ]
        ]
    ):
        output = "Groceries"
    elif transaction_description.startswith("Loan Repayment LN REPAY") or "CommInsure" in transaction_description:
        output = "HomeLoan"
    elif any(
        [
            transaction_description.lower().startswith(k.lower())
            for k in [
                "COLES EXPRESS",
                "7-ELEVEN",
                "BP ",
                "CALTEX",
                "METRO PETROLEUM",
                "SHELL",
                "AMPOL",
                "Enhance Neath Service",
            ]
        ]
    ):
        output = "Fuel"
    else:
        output = keyword_classifier(transaction_description)

    # Couldn't classify
    if output == transaction_description:
        output = "Other"

    return output


def keyword_classifier(transaction_description: str):
    labelled_keywords = {
        "Vehicle": ["Linkt", "CARLOVERS", "SNAP CAR WASH", "TOYOTA", "CIRCUM WASH"],
        "Fitness": ["URBANBASEFITNESS", "FITNESS PASSPORT", "The Forum Univer", "THE SELF C*", "REBEL"],
        "Utility": ["BPAY"],
        "Health/Pharmacy": [
            "Medical",
            "CHEMIST",
            "PHARMACY",
            "HUMMINGBIRD",
            "COUNSELLIN",
            "DOCS MEGASAVE",
            "Doctors",
            "THE GOOD DENTIST",
            "NOVAHEALTH",
            "PRICELINE",
            "SKINTIFIX",
            "FAMILY MED",
            "WENT PHARM MOSCHAKIS",
            "PLINEPH",
            "PLINE PH",
        ],
        "Parking": ["EASYPARK", "ParkPay", "WESTFIELD"],
        "Newspaper": ["ACM RURAL PRESS"],
        "Cafe": [
            "EQUIUM",
            "ONYX ESPRESSO",
            "HUBRO",
            "KAWUL",
            "BOCADOS",
            "Cafe",
            "T MY ENTERPRISE PL",
            "ALCMARIA PTY LTD",
            "SOUL ORIGIN",
            "AUTUMN ROOMS",
            "KAROO & CO",
        ],
        "Takeaway/Fastfood": [
            "SUSHI",
            "FAHS KITCHEN",
            "OLIVERS",
            "MCDONALDS",
            "Subway",
            "PIE",
            "BAKERS DELIGHT",
        ],
        "Home/Garden/Office": [
            "JB HI",
            "OFFICEWORKS",
            "BUNNINGS",
            "BIG W",
            "TARGET",
            "MISTER MINT",
            "POST",
            "NewsXpress",
        ],
        "Pets/Vet": ["Veterinary"],
    }
    for label, keywords in labelled_keywords.items():
        if any([k.lower() in transaction_description.lower() for k in keywords]):
            return label

    # Not found scenario
    return transaction_description


def time_bucket_labels(df: pd.DataFrame, period: str = "M") -> pd.DataFrame:
    df["time_bucket"] = df.date.dt.to_period(period).astype(str)
    return df
