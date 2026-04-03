from dataclasses import dataclass

import matplotlib.pyplot as plt
import streamlit as st


AGE_WEIGHT = 20.0
LENGTH_OF_STAY_WEIGHT = 15.0
COMORBIDITY_WEIGHT = 8.0
CREATININE_WEIGHT = 5.0
HEMOGLOBIN_WEIGHT = 3.0
WBC_WEIGHT = 2.0
BUN_WEIGHT = 0.5
MEDICARE_WEIGHT = 5.0
HIGH_RISK_THRESHOLD = 60.0
MEDIUM_RISK_THRESHOLD = 35.0

COMORBIDITY_OPTIONS = (
    "Cardiac disease",
    "Respiratory disease",
    "Diabetes",
    "Renal disease",
    "Sepsis",
    "Hypertension",
    "Cancer",
)

BENCHMARKS = (
    ("Overall readmission rate", "8.5%"),
    ("Male readmission rate", "12.9%"),
    ("Female readmission rate", "3.4%"),
    ("Highest-risk age group", "45-60 (20%)"),
)

RISK_COLORS = {
    "High": "#c0392b",
    "Moderate": "#d68910",
    "Low": "#1e8449",
}


@dataclass(frozen=True)
class PatientProfile:
    age: int
    gender: str
    length_of_stay: int
    insurance: str
    creatinine: float
    hemoglobin: float
    glucose: int
    sodium: int
    wbc: float
    bun: int
    conditions: tuple[str, ...]


def calculate_risk_components(profile: PatientProfile) -> dict[str, float]:
    components = {
        "Age": min(profile.age / 89, 1.0) * AGE_WEIGHT,
        "Length of stay": min(profile.length_of_stay / 30, 1.0) * LENGTH_OF_STAY_WEIGHT,
        "Comorbidities": len(profile.conditions) * COMORBIDITY_WEIGHT,
        "Creatinine": max(0.0, profile.creatinine - 1.2) * CREATININE_WEIGHT,
        "Hemoglobin": max(0.0, 12.0 - profile.hemoglobin) * HEMOGLOBIN_WEIGHT,
        "White blood cell count": max(0.0, profile.wbc - 11.0) * WBC_WEIGHT,
        "BUN": max(0.0, profile.bun - 25) * BUN_WEIGHT,
        "Insurance": MEDICARE_WEIGHT if profile.insurance == "Medicare" else 0.0,
    }
    return {name: round(value, 1) for name, value in components.items() if value > 0}


def total_risk_score(components: dict[str, float]) -> float:
    return min(round(sum(components.values()), 1), 100.0)


def risk_tier(score: float) -> str:
    if score >= HIGH_RISK_THRESHOLD:
        return "High"
    if score >= MEDIUM_RISK_THRESHOLD:
        return "Moderate"
    return "Low"


def age_group_risk_label(age: int) -> str:
    if 45 <= age <= 60:
        return "High"
    if age > 60:
        return "Moderate"
    return "Lower"


def build_risk_factors(profile: PatientProfile) -> list[tuple[str, str]]:
    factors: list[tuple[str, str]] = []

    if profile.creatinine > 1.5:
        factors.append(
            ("Elevated creatinine", "Kidney dysfunction is associated with higher readmission risk.")
        )
    if len(profile.conditions) >= 3:
        factors.append(
            (
                "High comorbidity burden",
                f"{len(profile.conditions)} documented conditions suggest more complex post-discharge care needs.",
            )
        )
    if profile.length_of_stay > 7:
        factors.append(
            ("Extended length of stay", "Longer admissions often reflect higher severity of illness.")
        )
    if profile.hemoglobin < 10.0:
        factors.append(("Low hemoglobin", "Anemia may slow recovery after discharge."))
    if profile.wbc > 11.0:
        factors.append(
            ("Elevated white blood cell count", "This may indicate active infection or inflammation.")
        )
    if 45 <= profile.age <= 60:
        factors.append(
            ("Peak-risk age group", "Patients aged 45 to 60 had the highest observed risk in the demo cohort.")
        )
    if "Renal disease" in profile.conditions:
        factors.append(
            ("Renal disease", "Chronic kidney disease is a common contributor to readmission risk.")
        )

    if not factors:
        return [("No major risk factors identified", "Current inputs do not indicate elevated risk drivers.")]
    return factors


def render_sidebar() -> PatientProfile:
    st.sidebar.header("Patient Information")
    age = st.sidebar.slider("Age", min_value=18, max_value=89, value=65)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
    length_of_stay = st.sidebar.slider("Length of stay (days)", min_value=1, max_value=30, value=5)
    insurance = st.sidebar.selectbox(
        "Insurance",
        ["Medicare", "Private", "Medicaid", "Government"],
    )

    st.sidebar.header("Comorbidities")
    selected_conditions = tuple(
        option for option in COMORBIDITY_OPTIONS if st.sidebar.checkbox(option)
    )

    st.sidebar.header("Laboratory Values")
    creatinine = st.sidebar.slider("Creatinine (mg/dL)", min_value=0.5, max_value=10.0, value=1.2)
    hemoglobin = st.sidebar.slider("Hemoglobin (g/dL)", min_value=5.0, max_value=18.0, value=12.0)
    glucose = st.sidebar.slider("Glucose (mg/dL)", min_value=60, max_value=400, value=120)
    sodium = st.sidebar.slider("Sodium (mEq/L)", min_value=120, max_value=160, value=140)
    wbc = st.sidebar.slider("White blood cell count (K/uL)", min_value=1.0, max_value=30.0, value=8.0)
    bun = st.sidebar.slider("BUN (mg/dL)", min_value=5, max_value=100, value=20)

    return PatientProfile(
        age=age,
        gender=gender,
        length_of_stay=length_of_stay,
        insurance=insurance,
        creatinine=creatinine,
        hemoglobin=hemoglobin,
        glucose=glucose,
        sodium=sodium,
        wbc=wbc,
        bun=bun,
        conditions=selected_conditions,
    )


def render_summary(profile: PatientProfile, score: float, tier: str) -> None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Readmission risk score", f"{score:.1f}/100")
        st.markdown(
            f"<p style='color:{RISK_COLORS[tier]}; font-size:1.2rem; font-weight:600;'>"
            f"{tier} risk</p>",
            unsafe_allow_html=True,
        )

    with col2:
        st.metric("Comorbidity burden", f"{len(profile.conditions)} conditions")
        st.metric("Length of stay", f"{profile.length_of_stay} days")

    with col3:
        st.metric("Age group risk", age_group_risk_label(profile.age))
        creatinine_status = "Elevated" if profile.creatinine > 1.5 else "Normal"
        st.metric("Creatinine", f"{profile.creatinine:.1f} mg/dL", delta=creatinine_status)


def render_risk_factors(profile: PatientProfile) -> None:
    st.subheader("Top risk factors")
    for factor, explanation in build_risk_factors(profile):
        st.markdown(f"**{factor}**")
        st.caption(explanation)


def render_risk_breakdown(components: dict[str, float]) -> None:
    st.subheader("Risk score breakdown")

    if not components:
        st.info("No positive risk contributions were generated from the current inputs.")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    bar_colors = [
        RISK_COLORS["High"] if value > 10 else RISK_COLORS["Moderate"] if value > 5 else RISK_COLORS["Low"]
        for value in components.values()
    ]
    ax.barh(list(components.keys()), list(components.values()), color=bar_colors, edgecolor="black")
    ax.set_xlabel("Risk contribution")
    ax.set_title("Risk component contribution")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def render_benchmarks() -> None:
    st.subheader("Population benchmarks")
    columns = st.columns(len(BENCHMARKS))
    for column, (label, value) in zip(columns, BENCHMARKS):
        column.metric(label, value)
    st.caption(
        "Source: MIMIC-III Clinical Database Demo (n=129 ICU patients), MIT Laboratory for Computational Physiology."
    )


def main() -> None:
    st.set_page_config(
        page_title="Patient Readmission Risk Dashboard",
        layout="wide",
    )

    st.title("30-Day Hospital Readmission Risk Dashboard")
    st.markdown("Clinical decision-support prototype based on the MIMIC-III ICU demo cohort.")
    st.info(
        "This dashboard is a research prototype for portfolio and educational use. "
        "It is not intended for clinical decision-making."
    )

    profile = render_sidebar()
    components = calculate_risk_components(profile)
    score = total_risk_score(components)
    tier = risk_tier(score)

    render_summary(profile, score, tier)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        render_risk_factors(profile)
    with col2:
        render_risk_breakdown(components)

    st.divider()
    render_benchmarks()


if __name__ == "__main__":
    main()
