# Predicting Developer Salaries Using the Stack Overflow 2024 Survey

This project uses the Stack Overflow 2024 Developer Survey to predict annual developer salaries. It covers the full pipeline: data cleaning, loading into MySQL, exploratory analysis, and machine learning model training.

## Prerequisites

- Python 3.10+
- MySQL 9.5.0+
- git

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd COSC301-Salary-Prediction
   ```

2. Download the dataset from https://survey.stackoverflow.co/ (2024 results).
   Place `survey_results_public.csv` and `survey_results_schema.csv` in the `data/` folder.

3. Copy the example environment file and fill in your MySQL credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```
   PATH_TO_RAW_DATA=./data/survey_results_public.csv
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=salary_prediction
   ```

4. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac/Linux
   .venv\Scripts\activate         # Windows
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Run the full pipeline:
   ```bash
   python run_pipeline.py
   ```

## Pipeline Steps

`run_pipeline.py` runs the following steps in order:

| Step | Script | Description |
|------|--------|-------------|
| 1 | `src/etl.py` | Cleans the raw CSV (handles missing values, encodes education/employment, removes salary outliers) and outputs `output/cleaned_data.csv` |
| 2 | `src/load_db.py` | Creates the MySQL schema and loads the cleaned data into the database |
| 3 | `notebooks/eda.ipynb` | Exploratory data analysis — distributions, correlations, top languages |
| 4 | `notebooks/models.ipynb` | Trains and evaluates salary prediction models (Linear Regression, XGBoost); reports R² and RMSE |

## Project Structure

```
COSC301-Salary-Prediction/
├── config/
│   └── db_config.py            # Loads DB credentials from .env
├── data/
│   ├── survey_results_public.csv   # Raw dataset (download separately, ~160MB)
│   └── survey_results_schema.csv   # Field descriptions from Stack Overflow
├── notebooks/
│   ├── eda.ipynb               # Exploratory data analysis
│   ├── examine_file.ipynb      # Initial data inspection
│   └── models.ipynb            # Model training and evaluation
├── output/
│   └── cleaned_data.csv        # Cleaned dataset produced by ETL
├── sql/
│   ├── schema.sql              # Creates the database and all tables
│   └── reset_schema.sql        # Drops all tables (used before re-loading)
├── src/
│   ├── etl.py                  # Extract, transform, load from CSV
│   ├── load_db.py              # Inserts cleaned data into MySQL
│   └── data_dictionary.xlsx    # Definitions for all fields used
├── .env.example                # Template for environment variables
├── requirements.txt            # Python dependencies
├── run_pipeline.py             # Runs all pipeline steps end-to-end
└── Group29_init.twb            # Tableau workbook for visualization
```
