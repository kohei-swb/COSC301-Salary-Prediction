import os
import subprocess
import sys
import tempfile

import nbformat

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

    with open(output_path, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code":
            for output in cell.outputs:
                if output.output_type == "stream" and output.name == "stdout":
                    print(output.text, end="")


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
