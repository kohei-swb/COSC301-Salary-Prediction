import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
# extract part of  the pipline
PATH_TO_RAW_DATA = os.getenv("PATH_TO_RAW_DATA")

def extract_data(file_path):
    df = pd.read_csv(file_path)
    columns_needed = [
        "Country",
        "YearsCodePro",
        "EdLevel",
        "DevType",
        "LanguageHaveWorkedWith",
        "Employment",
        "ConvertedCompYearly"
    ]
    return df[columns_needed].copy()


# Helper functions to transform the data 
def clean_years_code_pro(value):
    """
    Convert YearsCodePro into numeric years.
    Example:
    'Less than 1 year' -> 0.5
    'More than 50 years' -> 50
    '7' -> 7
    """
    if pd.isna(value):
        return np.nan
    value = str(value).strip()
    if value == "Less than 1 year":
        return 0.5
    elif value == "More than 50 years":
        return 50
    else:
        try:
            return float(value)
        except ValueError:
            return np.nan


def clean_education(value):
    """
    Convert education level into ordinal numeric values.
    Higher number = higher education level.
    """
    education_map = {
        "Primary/elementary school": 0,
        "Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)": 1,
        "Some college/university study without earning a degree": 2,
        "Associate degree (A.A., A.S., etc.)": 3,
        "Bachelor’s degree (B.A., B.S., B.Eng., etc.)": 4,
        "Master’s degree (M.A., M.S., M.Eng., MBA, etc.)": 5,
        "Professional degree (JD, MD, Ph.D, Ed.D, etc.)": 6,
        "Something else": np.nan
    }
    if pd.isna(value):
        return np.nan
    return education_map.get(value, np.nan)


# def clean_dev_type(value):
#     """
#     Simplify DevType by taking the first listed role.
#     Example:
#     'Developer, full-stack;Developer, back-end' -> 'Developer, full-stack'
#     """
#     if pd.isna(value):
#         return []
#     return [x.strip() for x in str(value).split(";") if x.strip()]


def split_languages(value):
    # Turn semicolon-separated languages into a list.
    if pd.isna(value):
        return []
    return [lang.strip() for lang in str(value).split(";") if lang.strip()]


def clean_employment(value):
    """
    Keep only the main employment category.
    Priority:
    full-time > part-time > contractor > student > unemployed > other
    """
    if pd.isna(value):
        return "Unknown"

    value = str(value)

    if "Employed, full-time" in value:
        return "Employed_full_time"
    elif "Employed, part-time" in value:
        return "Employed_part_time"
    elif "Independent contractor, freelancer, or self-employed" in value:
        return "Self_employed"
    elif "Student" in value:
        return "Student"
    elif "Not employed, but looking for work" in value:
        return "Unemployed_looking"
    elif "Not employed, and not looking for work" in value:
        return "Unemployed_not_looking"
    else:
        return "Other"


def clean_salary(value):
    #Clean salary column.
    if pd.isna(value):
        return np.nan
    try:
        return float(value)
    except ValueError:
        return np.nan


def remove_salary_outliers(df, column="ConvertedCompYearly"):
    # Remove extreme salary outliers using IQR.
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df[(df[column] >= lower) & (df[column] <= upper)].copy()


#Transform part of the ETL
def transform_data(df):
    df["YearsCodePro"] = df["YearsCodePro"].apply(clean_years_code_pro)
    df["EdLevel"] = df["EdLevel"].apply(clean_education)
    # df["DevType"] = df["DevType"].apply(clean_dev_type)
    df["LanguageHaveWorkedWith"] = df["LanguageHaveWorkedWith"].apply(split_languages)
    df["Employment"] = df["Employment"].apply(clean_employment)
    df["ConvertedCompYearly"] = df["ConvertedCompYearly"].apply(clean_salary)
    df = df.dropna(subset=["ConvertedCompYearly"]).copy()
    df = df[df["Employment"].isin(["Employed_full_time", "Employed_part_time", "Self_employed"])].copy()
    df = df.dropna(subset=["YearsCodePro", "EdLevel", "DevType", "Country"]).copy()
    df = remove_salary_outliers(df, "ConvertedCompYearly")
    df = df[~df["DevType"].str.contains("Other (please specify):", regex=False)].copy()
    df = df[~df["DevType"].str.contains("Student", regex=False)].copy()
    return df


#running the ETL 
file_path = PATH_TO_RAW_DATA
df = extract_data(file_path)
cleaned_df = transform_data(df)
cleaned_df['respondent_id'] = range(1, 1+len(cleaned_df))
cleaned_df.to_csv("cleaned_data.csv", index =  False)