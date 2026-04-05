# Final Report: Predicting Developer Salaries Using the Stack Overflow 2024 Survey

**Course:** COSC 301 | **Group:** 29

## Question

Can we predict a software developer's annual salary from publicly available survey data?

The Stack Overflow 2024 Developer Survey captures self-reported information from over 65,000 respondents worldwide. We focused on seven features available at survey time — country, years of professional coding experience, education level, developer type, employment status, and programming languages used — and used them to predict `ConvertedCompYearly`, a USD-normalized annual compensation figure.

## Method

### 1. ETL (`src/etl.py`)

The raw CSV was extracted and reduced to the seven columns of interest. The following transformations were applied:

* **YearsCodePro:** String values like `"Less than 1 year"` and `"More than 50 years"` were converted to `0.5` and `50` respectively; all others were cast to float.
* **EdLevel:** Mapped to an ordinal integer scale from 0 (primary school) to 6 (professional/doctoral degree). `"Something else"` was treated as missing.
* **Employment:** Multi-value strings were reduced to a single priority category (full-time > part-time > self-employed > student > unemployed).
* **LanguageHaveWorkedWith:** Semicolon-separated strings were split into lists for later normalization into a relational table.
* **ConvertedCompYearly:** Rows with missing salary were dropped. Extreme outliers were removed using the IQR method (±1.5×IQR).
* Rows with missing values in `YearsCodePro`, `EdLevel`, `DevType`, or `Country` were dropped. Respondents with `DevType` of "Student" or "Other (please specify)" were excluded.

### 2. Database Design (`sql/schema.sql`, `src/load_db.py`)

Data was loaded into a MySQL database with the following schema:

* **`developers`** — one row per respondent; stores all scalar features and the target variable.
* **`languages`** — normalized lookup table of unique language names.
* **`developer_languages`** — junction table resolving the many-to-many relationship between developers and languages.
* **`predictions`** — stores predicted salaries per respondent for each model.
* **`model_results`** — stores R² and RMSE for each model configuration.

### 3. Exploratory Data Analysis (`notebooks/eda.ipynb`)

EDA was conducted by querying the MySQL database directly. Key analyses included:

* Distributions of `years_code_pro`, `ed_level`, and `converted_comp_yearly`.
* Correlation heatmap among numeric features.
* Box plots of salary by country (top 15) and by developer type (top 15).
* Average salary by programming language, computed via a JOIN across the three developer tables.

### 4. Model Training (`notebooks/models.ipynb`)

Features were one-hot encoded for `country`, `dev_type`, and `employment`. Programming languages were pivoted into binary indicator columns.

**Baseline models** were trained on the full cleaned dataset:

| Model | R² | RMSE |
|---|---|---|
| Linear Regression | 0.597 | 32,167 |
| Random Forest | 0.605 | 31,870 |

**Ablation study** evaluated log transformation and category filtering independently:

* *Log transformation* (applied to salary and `years_code_pro`) consistently decreased R² across all models.
* *Filtering* (removing part-time respondents, restricting to top 25 countries and top 15 developer types) improved performance across all models.

Based on these results, the Filter Only configuration was carried forward.

**Further models** tested on the filtered dataset:

| Model | R² | RMSE |
|---|---|---|
| Linear Regression (Filtered) | 0.620 | 32,019 |
| Random Forest (Filtered) | 0.638 | 31,261 |
| Gradient Boosting (Filtered) | 0.635 | 31,378 |
| XGBoost (Filtered) | 0.650 | 30,736 |
| **XGBoost + GridSearchCV (Filtered)** | **0.670** | **29,820** |

Hyperparameter tuning via `GridSearchCV` (3-fold CV over `n_estimators`, `max_depth`, `learning_rate`, `subsample`, `colsample_bytree`) yielded the best model: XGBoost with `n_estimators=1000`, `max_depth=7`, `learning_rate=0.01`.

## Results

The tuned XGBoost model achieved **R² = 0.670** and **RMSE = $29,820**, explaining approximately 67% of the variance in annual developer salary. This represents a 12% improvement in R² over the Linear Regression baseline.

Key findings from EDA and modeling:

* **Country** was the strongest predictor of salary. US-based developers consistently reported the highest compensation, with a large gap relative to other countries.
* **Years of professional experience** showed a positive correlation with salary, but the relationship was non-linear.
* **Education level** had a weak correlation with salary (r = 0.094), and its inclusion had little effect on model performance.
* **Developer type** influenced salary, with roles such as engineering manager and site reliability engineer associated with higher compensation.
* **Programming languages** contributed signal — languages like Scala, Go, and Rust were associated with higher average salaries.
* **Log transformation** of salary did not improve model fit on this dataset, likely because IQR-based outlier removal had already reduced skew sufficiently.

## Limitations

* **Self-reported data:** Salary figures are self-reported and converted to USD using a single annual exchange rate, which may not reflect actual purchasing power or mid-year fluctuations.
* **Missing contextual features:** Company size, industry sector, remote vs. on-site work arrangement, and geographic cost of living are not captured in this dataset but are known to influence compensation significantly.
* **No PPP adjustment:** Salaries were compared across countries in nominal USD, which overstates the real income gap between high- and low-cost regions.
* **Categorical truncation:** Restricting to the top 25 countries and top 15 developer types means the model does not generalize to respondents outside these groups.
* **Unexplained variance:** An R² of 0.67 means roughly 33% of salary variance remains unexplained by the available features.

## Next Steps

* **Additional features:** Incorporate company size, industry, and remote work status if available in future survey editions.
* **PPP-adjusted target:** Normalize salaries by purchasing power parity before training to make cross-country comparisons more meaningful.
* **Better multi-label handling:** Encode developer type as a multi-hot vector rather than a single primary role, preserving information about developers with multiple specializations.
* **Cross-validation:** Replace the single 80/20 train-test split with k-fold cross-validation to produce more reliable performance estimates.
* **Hyperparameter tuning for all models:** GridSearchCV was applied only to XGBoost; similar tuning for Random Forest and Gradient Boosting may close the performance gap.
* **Richer salary modeling:** Explore quantile regression or prediction intervals to communicate uncertainty in individual salary estimates, rather than reporting only point predictions.
