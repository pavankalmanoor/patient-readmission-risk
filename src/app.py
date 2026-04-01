import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from pathlib import Path

# ── Page Config ────────────────────────────────────────
st.set_page_config(
    page_title="Clinical Readmission Risk Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 30-Day Hospital Readmission Risk Dashboard")
st.markdown("**MIMIC-III ICU Cohort | Clinical Decision Support Tool**")
st.warning("⚠️ Research prototype only — not for clinical use")

# ── Sidebar — Patient Input ────────────────────────────
st.sidebar.header("📋 Patient Information")

age = st.sidebar.slider("Age", 18, 89, 65)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
los_days = st.sidebar.slider("Length of Stay (days)", 1, 30, 5)
insurance = st.sidebar.selectbox("Insurance", ["Medicare", "Private", "Medicaid", "Government"])

st.sidebar.header("🔬 Comorbidities")
has_cardiac      = st.sidebar.checkbox("Cardiac Disease")
has_respiratory  = st.sidebar.checkbox("Respiratory Disease")
has_diabetes     = st.sidebar.checkbox("Diabetes")
has_renal        = st.sidebar.checkbox("Renal Disease")
has_sepsis       = st.sidebar.checkbox("Sepsis")
has_hypertension = st.sidebar.checkbox("Hypertension")
has_cancer       = st.sidebar.checkbox("Cancer")

st.sidebar.header("🧪 Lab Values")
creatinine = st.sidebar.slider("Creatinine (mg/dL)", 0.5, 10.0, 1.2)
hemoglobin = st.sidebar.slider("Hemoglobin (g/dL)", 5.0, 18.0, 12.0)
glucose    = st.sidebar.slider("Glucose (mg/dL)", 60, 400, 120)
sodium     = st.sidebar.slider("Sodium (mEq/L)", 120, 160, 140)
wbc        = st.sidebar.slider("WBC (K/uL)", 1.0, 30.0, 8.0)
bun        = st.sidebar.slider("BUN (mg/dL)", 5, 100, 20)

# ── Compute Risk Score ─────────────────────────────────
comorbidity_count = sum([has_cardiac, has_respiratory, has_diabetes,
                         has_renal, has_sepsis, has_hypertension, has_cancer])

# Simple risk score (rule-based for demo)
risk_score = 0.0
risk_score += min(age / 89, 1.0) * 20
risk_score += min(los_days / 30, 1.0) * 15
risk_score += comorbidity_count * 8
risk_score += max(0, creatinine - 1.2) * 5
risk_score += max(0, 12 - hemoglobin) * 3
risk_score += max(0, wbc - 11) * 2
risk_score += max(0, bun - 25) * 0.5
risk_score += (1 if insurance == "Medicare" else 0) * 5
risk_score = min(risk_score, 100)

# ── Main Dashboard ─────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    color = "🔴" if risk_score >= 60 else "🟡" if risk_score >= 35 else "🟢"
    st.metric("Readmission Risk Score", f"{risk_score:.1f}/100")
    tier = "HIGH RISK" if risk_score >= 60 else "MEDIUM RISK" if risk_score >= 35 else "LOW RISK"
    st.markdown(f"### {color} {tier}")

with col2:
    st.metric("Comorbidity Burden", f"{comorbidity_count} conditions")
    st.metric("Length of Stay", f"{los_days} days")

with col3:
    st.metric("Age Group Risk", 
              "High" if 45 <= age <= 60 else "Moderate" if age > 60 else "Lower")
    st.metric("Creatinine", f"{creatinine} mg/dL",
              delta="⚠️ Elevated" if creatinine > 1.5 else "Normal")

st.divider()

# ── Risk Factors ───────────────────────────────────────
col4, col5 = st.columns(2)

with col4:
    st.subheader("🔍 Top Risk Factors")
    risk_factors = []
    if creatinine > 1.5:
        risk_factors.append(("🔴 Elevated Creatinine", "Kidney dysfunction increases readmission risk"))
    if comorbidity_count >= 3:
        risk_factors.append(("🔴 High Comorbidity Burden", f"{comorbidity_count} conditions — complex care needs"))
    if los_days > 7:
        risk_factors.append(("🟡 Extended Hospital Stay", "Longer stays indicate higher illness severity"))
    if hemoglobin < 10:
        risk_factors.append(("🟡 Low Hemoglobin", "Anemia reduces recovery capacity"))
    if wbc > 11:
        risk_factors.append(("🟡 Elevated WBC", "Suggests active infection or inflammation"))
    if age >= 45 and age <= 60:
        risk_factors.append(("🟡 Peak Risk Age Group", "45-60 shows highest readmission rate in cohort"))
    if has_renal:
        risk_factors.append(("🟡 Renal Disease", "Chronic kidney disease — frequent readmission driver"))
    if not risk_factors:
        risk_factors.append(("🟢 No major risk factors identified", "Continue standard care protocols"))

    for factor, explanation in risk_factors:
        st.markdown(f"**{factor}**")
        st.caption(explanation)

with col5:
    st.subheader("📊 Risk Score Breakdown")
    components = {
        'Age': min(age/89, 1.0) * 20,
        'Length of Stay': min(los_days/30, 1.0) * 15,
        'Comorbidities': comorbidity_count * 8,
        'Creatinine': max(0, creatinine-1.2) * 5,
        'Hemoglobin': max(0, 12-hemoglobin) * 3,
        'WBC': max(0, wbc-11) * 2,
        'BUN': max(0, bun-25) * 0.5,
    }
    components = {k: round(v, 1) for k, v in components.items() if v > 0}

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ['#e74c3c' if v > 10 else '#f39c12' if v > 5 else '#2ecc71'
              for v in components.values()]
    ax.barh(list(components.keys()), list(components.values()),
            color=colors, edgecolor='black')
    ax.set_xlabel('Risk Contribution')
    ax.set_title('Risk Score Components')
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# ── Population Benchmarks ──────────────────────────────
st.subheader("📈 Population Benchmarks (MIMIC-III Cohort)")

col6, col7, col8, col9 = st.columns(4)
col6.metric("Overall Readmission Rate", "8.5%")
col7.metric("Male Readmission Rate", "12.9%")
col8.metric("Female Readmission Rate", "3.4%")
col9.metric("Peak Risk Age Group", "45-60 (20%)")

st.caption("Source: MIMIC-III Clinical Database Demo (n=129 ICU patients) | MIT Laboratory for Computational Physiology")