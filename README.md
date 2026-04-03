# Patient Readmission Risk Dashboard

Clinical data science project for estimating 30-day hospital readmission risk from the MIMIC-III Clinical Database Demo. The repository combines exploratory analysis, feature engineering, interpretable risk scoring, fairness analysis, and a Streamlit dashboard for presenting patient-level predictions.

## Overview

Hospital readmission is a widely tracked quality metric in US healthcare. This project explores how demographic variables, comorbidity burden, and laboratory measurements can be used to estimate short-term readmission risk in an ICU cohort.

The repository is designed as a portfolio project rather than a deployable medical device. It emphasizes:

- end-to-end analytical workflow
- interpretable feature design
- fairness-oriented model review
- clear presentation through an interactive dashboard

## Workflow

```text
MIMIC-III clinical tables
  -> feature engineering
  -> readmission risk modeling
  -> SHAP-based interpretation
  -> subgroup fairness analysis
  -> Streamlit dashboard
```

## Key Results

### Feature Importance
![SHAP feature importance](data/shap_readmission.png)

### Fairness Analysis
![Fairness analysis](data/fairness_analysis.png)

### Model Evaluation
![Confusion matrix](data/confusion_matrix.png)

## Clinical Findings

| Finding | Interpretation |
| --- | --- |
| Hemoglobin is the strongest predictor | Discharge anemia may be associated with impaired recovery and follow-up risk |
| Male patients show higher readmission rates than female patients in the demo cohort | Suggests a need to review discharge planning differences by subgroup |
| Patients aged 45 to 60 show the highest observed readmission rate | Indicates elevated risk in a group that may be under-monitored |
| Patients with multiple comorbidities show the highest risk | Supports comorbidity burden as a practical clinical signal |
| Readmission patterns vary by insurance category | Highlights the importance of socioeconomic context in post-discharge care |

## Repository Structure

```text
patient-readmission-risk/
|-- data/
|   |-- mimic-iii-clinical-database-demo-1.4.zip
|   |-- shap_readmission.png
|   |-- fairness_analysis.png
|   `-- confusion_matrix.png
|-- notebooks/
|   `-- 01_readmission_pipeline.ipynb
|-- src/
|   `-- app.py
|-- requirements.txt
`-- README.md
```

## Technical Stack

| Layer | Tools |
| --- | --- |
| Data source | MIMIC-III Clinical Database Demo |
| Modeling | XGBoost, scikit-learn |
| Explainability | SHAP |
| Experiment tracking | MLflow |
| Application layer | Streamlit |
| Languages | Python, SQL |

## Installation

```bash
git clone https://github.com/pavankalmanoor/patient-readmission-risk.git
cd patient-readmission-risk
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Dashboard

```bash
streamlit run src/app.py
```

## Methodology Notes

### Why leave-one-out cross-validation

The demo cohort is small, with only 129 patients and 11 positive readmission events. A traditional train-test split would leave too few positive examples in the test set to support stable evaluation, so leave-one-out cross-validation is a more defensible choice for the dataset size.

### Why gradient boosting instead of deep learning

For structured tabular clinical data, gradient-boosted trees are often more practical than deep learning. They handle missingness well, work effectively with modest dataset sizes, and integrate naturally with SHAP for interpretation.

### Why recall matters

In the readmission setting, false negatives can be costly because they represent high-risk patients who are not identified for follow-up. For that reason, the project prioritizes recall over a strictly precision-optimized threshold.

## Fairness Review

The analysis includes subgroup review across gender, age, insurance, and ethnicity. This is useful for identifying disparities, but it is not sufficient for deployment approval. Any production use would require a larger dataset, stronger calibration testing, and formal clinical governance.

## Limitations

| Limitation | Impact |
| --- | --- |
| Demo cohort of 129 patients | Results are directionally useful but not production-ready |
| Only 11 readmission events | Limits statistical confidence and model stability |
| Single-institution source data | Reduces generalizability |
| Historical data from 2001 to 2012 | May not reflect current practice patterns |

This repository should be understood as a research and portfolio artifact. Clinical deployment would require expanded data access, prospective validation, regulatory review, and privacy-compliant implementation.

## Citation

```text
Johnson, A., Pollard, T., and Mark, R. (2019).
MIMIC-III Clinical Database Demo (version 1.4).
PhysioNet. https://doi.org/10.13026/C2HM2Q
```
