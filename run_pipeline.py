import subprocess
import sys
import load_db
from Project import etl


def run_etl():
    print("=== Step 1: ETL ===")
    etl.main()


def run_load_db():
    print("=== Step 2: Load DB ===")
    load_db.main()


def run_notebook(path):
    subprocess.run([
        sys.executable, "-m", "nbconvert",
        "--to", "notebook", "--execute", "--output", "/tmp/executed.ipynb", path
    ], check=True)


def run_eda():
    print("=== Step 3: EDA ===")
    run_notebook("eda.ipynb")


def run_models():
    print("=== Step 4: Models ===")
    run_notebook("models.ipynb")


if __name__ == "__main__":
    run_etl()
    run_load_db()
    run_eda()
    run_models()
    print("\n=== Pipeline complete ===")
