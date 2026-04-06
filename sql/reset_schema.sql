CREATE DATABASE IF NOT EXISTS salary_prediction;
USE salary_prediction;
SET foreign_key_checks = 0;
DROP TABLE IF EXISTS model_results;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS developer_languages;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS developers;
SET foreign_key_checks = 1;