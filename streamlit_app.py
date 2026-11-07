import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import datetime

# --- CONFIGURATION & DATABASE ---
WATER_SPECIFIC_HEAT = 4.184  # J/(g·°C)

THEORETICAL_C = {
    "Aluminum": 0.897,
    "Brass": 0.380,
    "Copper": 0.385,
    "Iron": 0.450,
    "Lead": 0.128,
    "Nickel": 0.444,
    "Steel": 0.490,
    "Tin": 0.227,
    "Titanium": 0.523,
    "Zinc": 0.387,
    "Custom / Other": 0.0
}

st.set_page_config(page_title="Calorimetry Lab Calculator", page_icon="🧪", layout="wide")

st.title("🧪 Calorimetry Lab & Specific Heat Calculator")
st.markdown("Record experimental calorimetry trials, calibrate vessel heat capacity, calculate statistical metrics, and generate visual charts.")

# --- INITIALIZE SESSION STATE ---
if "trials" not in st.session_state:
    st.session_state.trials = []

# --- SIDEBAR: SETUP & CALIBRATION WIZARD ---
st.sidebar.header("⚙️ Experiment Setup")

material_name = st.sidebar.selectbox("Select Specimen Material", list(THEORETICAL_C.keys()))
c_theoretical = THEORETICAL_C[material_name]

if material_name == "Custom / Other":
    c_theoretical = st.sidebar.number_input("Enter Theoretical c (J/g·°C)", min_value=0.0, value=0.0, step=0.01)

m_sample = st.sidebar.number_input("Sample Mass m_s (g)", min_value=0.1, value=65.0, step=0.1)
m_water = st.sidebar.number_input("Water Mass m_w (g)", min_value=0.1, value=120.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("☕ Vessel Calibration (C_cal)")
use_calibration = st.sidebar.checkbox("Run Cup Calibration Wizard", value=False)

C_cal = 10.0  # Default estimate

if use_calibration:
    m_cold = st.sidebar.number_input("Cold Water Mass (g)", min_value=0.1, value=100.0)
    T_cold = st.sidebar.number_input("Cold Water Temp (°C)", value=22.0)
    m_hot = st.sidebar.number_input("Hot Water Mass (g)", min_value=0.1, value=100.0)
    T_hot = st.sidebar.number_input("Hot Water Temp (°C)", value=80.0)
    T_mix_final = st.sidebar.number_input("Mix Final Temp (°C)", min_value=T_cold, max_value=T_hot, value=48.0)
    
    q_lost_hot = m_hot * WATER_SPECIFIC_HEAT * (T_hot - T_mix_final)
    q_gained_cold = m_cold * WATER_SPECIFIC_HEAT * (T_mix_final - T_cold)
    
    if T_mix_final > T_cold:
        c_cal_calc = (q_lost_hot - q_gained_cold) / (T_mix_final - T_cold)
        C_cal = max(0.0, c_cal_calc)
        st.sidebar.success(f"Calibrated C_cal: **{C_cal:.2f} J/°C**")
    else:
        st.sidebar.warning("Final temp must be > cold water temp.")
else:
    C_cal = st.sidebar.number_input("Calorimeter Heat Capacity C_cal (J/°C)", min_value=0.0, value=10.0, step=1.0)

# --- MAIN PANEL: DATA ENTRY ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Record Trial Reading")
    T_sample_init = st.number_input("Initial Hot Sample Temp Ts (°C)", value=99.5, step=0.1)
    T_water_init = st.number_input("Initial Cold Water Temp Tw (°C)", value=22.0, step=0.1)
    T_final = st.number_input("Measured Equilibrium Final Temp Tf (°C)", value=26.8, step=0.1)

    if st.button("➕ Add Trial Reading", use_container_width=True):
        if T_final <= T_water_init:
            st.error("Error: Final temperature (Tf) must be greater than initial water temp (Tw).")
        elif T_sample_init <= T_final:
            st.error("Error: Initial sample temp (Ts) must be greater than final temp (Tf).")
        else:
            q_water = m_water * WATER_SPECIFIC_HEAT * (T_final - T_water_init)
            q_cal = C_cal * (T_final - T_water_init)
            q_gained = q_water + q_cal

            delta_T_sample = T_sample_init - T_final
            c_experimental = q_gained / (m_sample * delta_T_sample)

            pct_error = None
            if c_theoretical > 0:
                pct_error = abs(c_experimental - c_theoretical) / c_theoretical * 100

            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            trial_number = len(st.session_state.trials) + 1
            st.session_state.trials.append({
                "Trial": trial_number,
                "Time": timestamp,
                "Sample Mass (g)": m_sample,
                "Water Mass (g)": m_water,
                "Ts (°C)": T_sample_init,
                "Tw (°C)": T_water_init,
                "Tf (°C)": T_final,
                "Q Gained (J)": round(q_gained, 2),
                "c_exp (J/g·°C)": round(c_experimental, 4),
                "c_theo (J/g·°C)": round(c_theoretical, 4) if c_theoretical > 0 else "N/A",
                "Error (%)": round(pct_error, 2) if pct_error is not None else "N/A"
            })
            st.success(f"Trial #{trial_number} added successfully!")

with col2:
    st.subheader("📊 Session Control")
    if st.button("🗑️ Clear All Trials", use_container_width=True):
        st.session_state.trials = []
        st.rerun()

# --- DISPLAY TRIALS TABLE & SUMMARY ---
if st.session_state.trials:
    df = pd.DataFrame(st.session_state.trials)
    
    st.markdown("---")
    st.subheader("📋 Experimental Readings Log")
    st.dataframe(df, use_container_width=True)

    c_list = [row["c_exp (J/g·°C)"] for row in st.session_state.trials]
    mean_c = sum(c_list) / len(c_list)
    
    std_dev = 0.0
    if len(c_list) > 1:
        variance = sum((x - mean_c) ** 2 for x in c_list) / (len(c_list) - 1)
        std_dev = math.sqrt(variance)

    overall_error = None
    if c_theoretical > 0:
        overall_error = abs(mean_c - c_theoretical) / c_theoretical * 100

    st.markdown("### 📈 Session Experimental Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Trials", len(c_list))
    m2.metric("Mean Specific Heat", f"{mean_c:.4f} J/g·°C")
    m3.metric("Standard Deviation", f"±{std_dev:.4f}" if len(c_list) > 1 else "N/A")
    m4.metric("Overall Error", f"{overall_error:.2f}%" if overall_error is not None else "N/A")

    st.markdown("### 📊 Specific Heat Comparison Chart")
    fig, ax = plt.subplots(figsize=(8, 4))
    
    trial_labels = [f"Trial {t['Trial']}" for t in st.session_state.trials]
    bars = ax.bar(trial_labels, c_list, color='skyblue', edgecolor='black', label='Experimental c')
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.4f}", ha='center', va='bottom', fontsize=9)

    if c_theoretical > 0:
        ax.axhline(y=c_theoretical, color='r', linestyle='--', linewidth=2, label=f'Theoretical ({material_name})')

    ax.set_ylabel("Specific Heat Capacity (J/g·°C)")
    ax.set_title(f"Calorimetry Results: {material_name}")
    ax.legend(loc='lower right')
    ax.grid(axis='y', linestyle=':', alpha=0.7)
    
    max_y = max(max(c_list), c_theoretical if c_theoretical > 0 else 0) * 1.25
    ax.set_ylim(0, max_y)
    
    st.pyplot(fig)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV",
        data=csv_data,
        file_name=f"calorimetry_{material_name.lower().replace(' ', '_')}.csv",
        mime='text/csv'
    )
