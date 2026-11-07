# ==============================================================================
# UNIFIED GOOGLE COLAB CALORIMETRY LAB & AUTOMATIC BAR CHART GENERATOR
# ==============================================================================

import csv
import datetime
import math
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Image

# --- CONFIGURATION & DATABASE ---
WATER_SPECIFIC_HEAT = 4.184  # J/(g·°C)

THEORETICAL_C = {
    "aluminum": 0.897,
    "brass": 0.380,
    "copper": 0.385,
    "iron": 0.450,
    "lead": 0.128,
    "nickel": 0.444,
    "steel": 0.490,
    "tin": 0.227,
    "titanium": 0.523,
    "zinc": 0.387
}


def get_float_input(prompt: str, min_val: float = None, max_val: float = None) -> float:
    """Safely handles numeric user inputs with boundary checks."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() == 'q':
            return None
        try:
            val = float(raw)
            if min_val is not None and val < min_val:
                print(f"  [ERROR] Value must be >= {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  [ERROR] Value must be <= {max_val}.")
                continue
            return val
        except ValueError:
            print("  [ERROR] Please enter a valid number (or 'q' to quit).")


def calibrate_cup_wizard() -> float:
    """Calculates custom calorimeter vessel heat capacity (C_cal) via hot/cold water mixing."""
    print("\n" + "=" * 60)
    print("      CALORIMETER CUP CALIBRATION WIZARD (OPTIONAL)      ")
    print("=" * 60)
    print("Mix known masses of hot and cold water to find cup capacity (C_cal).")

    use_wiz = input("Run calibration wizard? (y/n, default 'n'): ").lower().strip()
    if use_wiz != 'y':
        return 10.0  # Default estimate for 2 nested styrofoam cups

    m_cold = get_float_input("Mass of cold water in cup (g): ", min_val=0.1)
    if m_cold is None: return 10.0
    T_cold = get_float_input("Initial cold water temp (°C): ")
    if T_cold is None: return 10.0
    m_hot = get_float_input("Mass of hot water added (g): ", min_val=0.1)
    if m_hot is None: return 10.0
    T_hot = get_float_input("Initial hot water temp (°C): ")
    if T_hot is None: return 10.0
    T_final = get_float_input("Equilibrium final temp (°C): ", min_val=T_cold, max_val=T_hot)
    if T_final is None: return 10.0

    # Energy Balance: Heat lost by hot water = Heat gained by cold water + Heat gained by cup
    q_lost_hot = m_hot * WATER_SPECIFIC_HEAT * (T_hot - T_final)
    q_gained_cold = m_cold * WATER_SPECIFIC_HEAT * (T_final - T_cold)

    c_cal_exp = (q_lost_hot - q_gained_cold) / (T_final - T_cold)
    c_cal_exp = max(0.0, c_cal_exp)  # Safeguard non-negative capacity

    print(f"\n✔ Calibration complete! Measured C_cal = {c_cal_exp:.2f} J/°C\n")
    return c_cal_exp


def display_chart_from_csv(csv_filename: str, material_name: str):
    """Reads saved CSV using Pandas and renders the bar chart directly in Colab."""
    if not os.path.exists(csv_filename):
        print(f"❌ File '{csv_filename}' not found.")
        return

    try:
        df = pd.read_csv(csv_filename)
        if df.empty:
            print("❌ CSV file is empty. Please record at least 1 trial.")
            return

        trials = [f"Trial {int(row['Trial'])}" for _, row in df.iterrows()]
        exp_c = [float(row['c_exp_J_gC']) for _, row in df.iterrows()]

        plt.figure(figsize=(8, 5))
        plt.bar(trials, exp_c, color='skyblue', edgecolor='black', label='Experimental c')

        # Check and plot theoretical reference line
        first_theo = str(df['c_theo_J_gC'].iloc[0])
        if first_theo != "N/A" and first_theo != "nan":
            theo_val = float(first_theo)
            if theo_val > 0:
                plt.axhline(y=theo_val, color='r', linestyle='--', linewidth=2,
                            label=f'Theoretical ({material_name.title()})')

        plt.ylabel("Specific Heat Capacity (J/g·°C)")
        plt.xlabel("Experimental Trials")
        plt.title(f"Calorimetry Results: {material_name.title()}")
        plt.legend()
        plt.grid(axis='y', linestyle=':', alpha=0.7)

        # Save and show directly in output cell
        plot_path = csv_filename.replace('.csv', '_chart.png')
        plt.savefig(plot_path, dpi=300)

        print(f"\n📊 AUTOMATICALLY DISPLAYING BAR CHART:")
        plt.show()
        plt.close()

    except Exception as e:
        print(f"❌ Error generating plot: {e}")


# --- MAIN EXPERIMENTAL RUNNER ---
def main():
    print("=" * 60)
    print("     LIVE CALORIMETRY LAB & SPECIFIC HEAT CALCULATOR     ")
    print("=" * 60)

    # 1. SETUP SPECIMEN & CALORIMETER
    mat_name = input("\nEnter Material Name (e.g., Steel, Copper, Aluminum): ").strip()
    c_theoretical = THEORETICAL_C.get(mat_name.lower(), 0.0)

    m_sample = get_float_input("Enter Sample Mass m_s (grams): ", min_val=0.1)
    if m_sample is None: return

    m_water = get_float_input("Enter Water Mass m_w (grams): ", min_val=0.1)
    if m_water is None: return

    # Run calibration wizard or return default
    C_cal = calibrate_cup_wizard()

    csv_filename = f"calorimetry_{mat_name.lower().replace(' ', '_')}.csv"
    headers = [
        "Trial", "Timestamp", "Sample_Mass_g", "Water_Mass_g",
        "T_sample_init_C", "T_water_init_C", "T_final_C",
        "Q_gained_J", "c_exp_J_gC", "c_theo_J_gC", "Percent_Error_pct"
    ]

    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='') as f:
            csv.writer(f).writerow(headers)
        print(f"[INFO] New dataset initialized: '{csv_filename}'")
    else:
        print(f"[INFO] Appending to existing dataset: '{csv_filename}'")

    print("\n" + "=" * 60)
    print("BEGIN ENTERING READINGS (Type 'q' at any prompt to quit)")
    print("=" * 60)

    trials_data = []
    entry_num = 1

    # 2. EXPERIMENTAL DATA ENTRY LOOP
    while True:
        print(f"\n--- TRIAL #{entry_num} ---")

        T_sample_init = get_float_input("Initial Hot Sample Temp Ts (°C): ")
        if T_sample_init is None: break

        T_water_init = get_float_input("Initial Cold Water Temp Tw (°C): ")
        if T_water_init is None: break

        T_final = get_float_input("Measured Equilibrium Final Temp Tf (°C): ",
                                  min_val=T_water_init, max_val=T_sample_init)
        if T_final is None: break

        # 3. THERMAL CALCULATIONS
        q_water = m_water * WATER_SPECIFIC_HEAT * (T_final - T_water_init)
        q_cal = C_cal * (T_final - T_water_init)
        q_gained = q_water + q_cal

        delta_T_sample = T_sample_init - T_final
        c_experimental = q_gained / (m_sample * delta_T_sample)

        pct_error = None
        if c_theoretical > 0:
            pct_error = abs(c_experimental - c_theoretical) / c_theoretical * 100

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # 4. LOG RESULTS TO CSV
        with open(csv_filename, mode='a', newline='') as f:
            csv.writer(f).writerow([
                entry_num, timestamp, m_sample, m_water,
                T_sample_init, T_water_init, T_final,
                round(q_gained, 2), round(c_experimental, 4),
                round(c_theoretical, 4) if c_theoretical > 0 else "N/A",
                f"{pct_error:.2f}" if pct_error is not None else "N/A"
            ])

        trials_data.append({
            "trial": entry_num,
            "c_exp": c_experimental
        })

        # Display trial outputs
        print("-" * 45)
        print(f"Heat Gained by System (Q) : {q_gained:.2f} J")
        print(f"Exp. Specific Heat (c)    : {c_experimental:.4f} J/(g·°C)")
        if c_theoretical > 0:
            print(f"Theo. Specific Heat (c)   : {c_theoretical:.4f} J/(g·°C)")
            print(f"Trial Error               : {pct_error:.2f}%")
        print("-" * 45)
        print(f"✔ Trial #{entry_num} saved successfully.")

        entry_num += 1

    # 5. SESSION SUMMARY & AUTOMATIC CHART DISPLAY
    if trials_data:
        c_list = [t['c_exp'] for t in trials_data]
        mean_c = sum(c_list) / len(c_list)

        print("\n" + "=" * 60)
        print("                SESSION EXPERIMENTAL SUMMARY               ")
        print("=" * 60)
        print(f"Total Trials Recorded    : {len(trials_data)}")
        print(f"Mean Specific Heat (c)   : {mean_c:.4f} J/(g·°C)")

        if len(c_list) > 1:
            variance = sum((x - mean_c) ** 2 for x in c_list) / (len(c_list) - 1)
            std_dev = math.sqrt(variance)
            print(f"Sample Standard Dev. (s) : ±{std_dev:.4f} J/(g·°C)")

        if c_theoretical > 0:
            overall_error = abs(mean_c - c_theoretical) / c_theoretical * 100
            print(f"Overall Dataset Error    : {overall_error:.2f}%")
        print("=" * 60)

        # Plot bar chart directly from the saved CSV file
        display_chart_from_csv(csv_filename, mat_name)

    print(f"\n[COMPLETED] Session ended. CSV file saved as '{csv_filename}'.\n")

if __name__ == "__main__":
    main()
