import os
import subprocess
import sys
import tempfile

from src import load_db
from src import etl


def run_etl():
    print("=== Step 1: ETL ===")
    etl.main()


def run_load_db():
    print("=== Step 2: Load DB ===")
    load_db.main()


def run_notebook(path):
    output_path = os.path.join(tempfile.gettempdir(), "executed.ipynb")
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    subprocess.run([
        sys.executable, "-m", "nbconvert",
        "--to", "notebook", 
        "--execute", 
        "--output", output_path, 
        path
    ], check=True, env=env)  


def run_eda():
    print("=== Step 3: EDA ===")
    run_notebook("notebooks/eda.ipynb")


def run_models():
    print("=== Step 4: Models ===")
    run_notebook("notebooks/models.ipynb")


if __name__ == "__main__":
    run_etl()
    run_load_db()
    run_eda()
    run_models()
    print("\n=== Pipeline complete ===")
