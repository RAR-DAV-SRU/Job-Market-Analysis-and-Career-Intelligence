"""
CAREERLENS - DATA VISUALIZATION
-------------------------------
Place this Python file in the same folder as CareerLens_Cleaned_Data.xlsx.
Run: python data_visualization.py

PNG charts are saved in a folder named "visualization_output".
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "CareerLens_Cleaned_Data.xlsx"
OUTPUT_DIR = BASE_DIR / "visualization_output"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_bar_chart(data, title, xlabel, ylabel, filename, rotate=35):
    if data.empty:
        return
    plt.figure(figsize=(10, 6))
    data.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotate, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close()

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_FILE.name}. Keep the Excel file in the same folder as this script."
        )

    df = pd.read_excel(INPUT_FILE, sheet_name="Member_Data")
    df.columns = df.columns.str.strip()

    # Convert numerical columns safely
    for col in ["Age", "Experience_Years", "Technical_Skill_%", "Communication_%", "Career_Readiness_%"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 1. Job status distribution
    if "Job_Status" in df.columns:
        counts = df["Job_Status"].value_counts()
        plt.figure(figsize=(8, 6))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
        plt.title("Member Job Status Distribution")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "01_job_status_distribution.png", dpi=300)
        plt.close()

    # 2. Members by current role
    if "Current_Role" in df.columns:
        role_counts = df["Current_Role"].value_counts().sort_values(ascending=True)
        plt.figure(figsize=(10, 7))
        role_counts.plot(kind="barh")
        plt.title("Number of Members by Current Role")
        plt.xlabel("Number of Members")
        plt.ylabel("Current Role")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "02_members_by_role.png", dpi=300)
        plt.close()

    # 3. Members by location (top 10)
    if "Location" in df.columns:
        location_counts = df["Location"].value_counts().head(10).sort_values()
        plt.figure(figsize=(10, 6))
        location_counts.plot(kind="bar")
        plt.title("Top 10 Locations by Number of Members")
        plt.xlabel("Location")
        plt.ylabel("Number of Members")
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "03_top_locations.png", dpi=300)
        plt.close()

    # 4. Average skill and career-readiness percentages
    score_cols = ["Technical_Skill_%", "Communication_%", "Career_Readiness_%"]
    available_scores = [col for col in score_cols if col in df.columns]
    if available_scores:
        averages = df[available_scores].mean().dropna()
        averages.index = [name.replace("_", " ").replace("%", "(%)") for name in averages.index]
        plt.figure(figsize=(9, 6))
        averages.plot(kind="bar")
        plt.title("Average Skills and Career Readiness")
        plt.xlabel("Measure")
        plt.ylabel("Average Percentage")
        plt.ylim(0, 100)
        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "04_average_skill_scores.png", dpi=300)
        plt.close()

    # 5. Career readiness by role
    if {"Current_Role", "Career_Readiness_%"} <= set(df.columns):
        role_readiness = (
            df.groupby("Current_Role")["Career_Readiness_%"]
              .mean()
              .dropna()
              .sort_values()
        )
        plt.figure(figsize=(10, 7))
        role_readiness.plot(kind="barh")
        plt.title("Average Career Readiness by Role")
        plt.xlabel("Average Career Readiness (%)")
        plt.ylabel("Current Role")
        plt.xlim(0, 100)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "05_career_readiness_by_role.png", dpi=300)
        plt.close()

    # 6. Age distribution
    if "Age" in df.columns:
        ages = df["Age"].dropna()
        if not ages.empty:
            plt.figure(figsize=(9, 6))
            plt.hist(ages, bins=10, edgecolor="black")
            plt.title("Member Age Distribution")
            plt.xlabel("Age")
            plt.ylabel("Number of Members")
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "06_age_distribution.png", dpi=300)
            plt.close()

    # 7. Experience distribution
    if "Experience_Years" in df.columns:
        experience = df["Experience_Years"].dropna()
        if not experience.empty:
            plt.figure(figsize=(9, 6))
            plt.hist(experience, bins=10, edgecolor="black")
            plt.title("Work Experience Distribution")
            plt.xlabel("Experience (Years)")
            plt.ylabel("Number of Members")
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "07_experience_distribution.png", dpi=300)
            plt.close()

    # 8. Technical skill vs communication skill
    if {"Technical_Skill_%", "Communication_%"} <= set(df.columns):
        plot_data = df[["Technical_Skill_%", "Communication_%"]].dropna()
        if not plot_data.empty:
            plt.figure(figsize=(8, 6))
            plt.scatter(plot_data["Technical_Skill_%"], plot_data["Communication_%"], alpha=0.65)
            plt.title("Technical Skills vs Communication Skills")
            plt.xlabel("Technical Skill (%)")
            plt.ylabel("Communication (%)")
            plt.xlim(0, 100)
            plt.ylim(0, 100)
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "08_technical_vs_communication.png", dpi=300)
            plt.close()

    print("Data visualization completed successfully.")
    print(f"Charts saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
