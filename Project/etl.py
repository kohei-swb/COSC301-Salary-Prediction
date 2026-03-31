import pandas as pd
import numpy as np
import csv
# extract part of  the pipline
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


def clean_dev_type(value):
    """
    Simplify DevType by taking the first listed role.
    Example:
    'Developer, full-stack;Developer, back-end' -> 'Developer, full-stack'
    """
    if pd.isna(value):
        return "Unknown"
    roles = [x.strip() for x in str(value).split(";") if x.strip()]
    return roles[0] if roles else "Unknown"


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


# Feature Engineering
def create_language_features(df, top_n=15):
    # Create binary columns for the top N most common languages.
    all_languages = df["LanguageHaveWorkedWith"].explode()
    top_languages = all_languages.value_counts().head(top_n).index.tolist()
    for lang in top_languages:
        col_name = f"lang_{lang.replace('/', '_').replace(' ', '_').replace('-', '_')}"
        df[col_name] = df["LanguageHaveWorkedWith"].apply(lambda langs: int(lang in langs))
    return df, top_languages


def create_country_features(df, top_n=10):
    #Keep only top countries, group the rest into 'Other'.
    top_countries = df["Country"].value_counts().head(top_n).index.tolist()
    df["Country"] = df["Country"].apply(lambda x: x if x in top_countries else "Other")
    return df


#Transform part of the ETL
def transform_data(df):
    df["YearsCodePro"] = df["YearsCodePro"].apply(clean_years_code_pro)
    df["EdLevel"] = df["EdLevel"].apply(clean_education)
    df["DevType"] = df["DevType"].apply(clean_dev_type)
    df["LanguageHaveWorkedWith"] = df["LanguageHaveWorkedWith"].apply(split_languages)
    df["Employment"] = df["Employment"].apply(clean_employment)
    df["ConvertedCompYearly"] = df["ConvertedCompYearly"].apply(clean_salary)
    df = df.dropna(subset=["ConvertedCompYearly"]).copy()
    df = df[df["Employment"].isin(["Employed_full_time", "Employed_part_time", "Self_employed"])].copy()
    df = df.dropna(subset=["YearsCodePro", "EdLevel", "DevType", "Country"]).copy()
    df = remove_salary_outliers(df, "ConvertedCompYearly")
    df = create_country_features(df, top_n=10)
    df, top_languages = create_language_features(df, top_n=15)
    df = pd.get_dummies(df, columns=["Country", "DevType", "Employment"], drop_first=True)
    return df, top_languages


# Load part of the ETL
def load_model_data(file_path):
    df = extract_data(file_path)
    cleaned_df, top_languages = transform_data(df)
    cleaned_df = cleaned_df.drop(columns=["LanguageHaveWorkedWith"])
    X = cleaned_df.drop(columns=["ConvertedCompYearly"])
    y = cleaned_df["ConvertedCompYearly"]
    return X, y, cleaned_df, top_languages


#running the ETL 
file_path = r"C:\COSC 301\COSC 301 Project\Project\subset.csv"
X, y, cleaned_df, top_languages = load_model_data(file_path)
X.to_csv("cleaned_data.csv", index =  False)
with open('Top_languages.csv', 'w') as file:
   for lang in top_languages:
        file.write(lang + '\n')