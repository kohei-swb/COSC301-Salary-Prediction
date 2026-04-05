CREATE DATABASE IF NOT EXISTS salary_prediction;
USE salary_prediction;
CREATE TABLE IF NOT EXISTS developers (
    respondent_id INT PRIMARY KEY,
    country VARCHAR(100),
    years_code_pro FLOAT,
    ed_level INT,
    dev_type VARCHAR(255),
    employment VARCHAR(50),
    converted_comp_yearly FLOAT
);

CREATE TABLE IF NOT EXISTS languages (
    language_id INT AUTO_INCREMENT PRIMARY KEY,
    language_name VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS developer_languages (
    respondent_id INT,
    language_id INT,
    PRIMARY KEY (respondent_id, language_id),
    FOREIGN KEY (respondent_id) REFERENCES developers(respondent_id),
    FOREIGN KEY (language_id) REFERENCES languages(language_id)
);

CREATE TABLE IF NOT EXISTS predictions (
    respondent_id INT,
    predicted_salary FLOAT,
    model_type VARCHAR(50),
    FOREIGN KEY (respondent_id) REFERENCES developers(respondent_id)
);

CREATE TABLE IF NOT EXISTS model_results (
    model_type VARCHAR(100),
    r2 FLOAT,
    rmse FLOAT
);