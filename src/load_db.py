import pandas as pd
import mysql.connector
from config.db_config import DB_CONFIG


def load_languages(cursor, df):
    all_languages = set()
    
    for _, row in df.iterrows():
        languages = row["LanguageHaveWorkedWith"].strip('[').strip(']').split(',')
        languages = [x.strip().strip("'") for x in languages]
        languages = [x for x in languages if len(x) != 0]
        all_languages.update(languages)
    
    all_languages_list = list(all_languages)
    sorted_languages = sorted(all_languages_list)
    # print(sorted_languages)
    # print(all_languages)
    sql = """
    INSERT INTO languages (language_name) VALUES (%s)
    """
    for k in sorted_languages:
        cursor.execute(sql, (k,))
        # print(k)
    print(f"languages: {len(all_languages)}insertion completed")

def create_tables(cursor):
    with open("sql/schema.sql", "r") as f:
        sql = f.read()
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    print("Completed creating tables")
    
def reset_tables(cursor):
    with open("sql/reset_schema.sql") as f:
        sql = f.read()
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    print("Reset schema completed")

def load_developers(cursor, df):
    sql = """
        INSERT INTO developers 
            (respondent_id, country, years_code_pro, ed_level, dev_type, employment, converted_comp_yearly)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    rows = []
    for _, row in df.iterrows():
        rows.append((
            int(row["respondent_id"]),
            row["Country"],
            float(row["YearsCodePro"]),
            int(row["EdLevel"]),
            row["DevType"],
            row["Employment"],
            float(row["ConvertedCompYearly"])
        ))
    cursor.executemany(sql, rows)
    print(f"developers: {len(rows)} insertion completed")

def load_developer_languages(cursor, df):
    count = 0
    retrieve_languages_id_sql = """
        SELECT * FROM languages;
    """
    
    cursor.execute(retrieve_languages_id_sql)
    languages_li_tu = cursor.fetchall()
    
    insert_dev_lan_sql = """
        INSERT INTO developer_languages(respondent_id, language_id) 
        VALUES(%s, %s)
    """
    lang_map = {name: lid for lid, name in languages_li_tu}
    
    for _, row in df.iterrows():
        res_id = int(row["respondent_id"])
        languages = row["LanguageHaveWorkedWith"].strip('[').strip(']').split(',')
        languages = [x.strip().strip("'") for x in languages]
        languages = [x for x in languages if len(x) != 0]
        for l in languages:
            if l in lang_map:
                cursor.execute(insert_dev_lan_sql, (res_id, lang_map[l]))
                count += 1
    print(f"developer_languages: {count} insertion completed")

def main():
    df = pd.read_csv("output/cleaned_data.csv")
 
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
 
    try:
        reset_tables(cursor)
        create_tables(cursor)
        load_developers(cursor, df)
        load_languages(cursor, df)
        load_developer_languages(cursor, df)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error occured: {e}")
    finally:
        cursor.close()
        conn.close()
 
 
if __name__ == "__main__":
    main()