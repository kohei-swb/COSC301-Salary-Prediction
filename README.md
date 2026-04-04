# Predicting Developer Salaries Using the Stack Overflow 2024 Survey

## Setup

1. Create a `data/` folder in the root directory
2. Download the dataset from https://survey.stackoverflow.co/ and place it in the `data/` folder
3. Create a `.env` file in the root directory:
```
PATH_TO_RAW_DATA=./data/survey_results_public.csv
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=salary_prediction
```
4. Create a virtual environment: `python -m venv .venv`
5. Activate it:
   - Mac/Linux: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
6. Install dependencies: `pip install -r requirements.txt`


## Requirements

- Python 3.10+
- MySQL 9.5.0+