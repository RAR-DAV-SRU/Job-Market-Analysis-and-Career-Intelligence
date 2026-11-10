"""
CAREERLENS - DATA ANALYSIS
-------------------------
Place this Python file in the same folder as CareerLens_Cleaned_Data.xlsx.
Run: python data_analysis.py

Outputs are saved in a folder named "analysis_output".
"""

from pathlib import Path
import pandas as pd

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    # Fallback for Jupyter Notebook / Google Colab environments where __file__ is not defined
    BASE_DIR = Path.cwd()

INPUT_FILE = BASE_DIR / "CareerLens_Cleaned_Data.xlsx"
OUTPUT_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_FILE.name}. Keep the Excel file in the same folder as this script."
        )

    # Load the main member-level dataset
    df = pd.read_excel(INPUT_FILE, sheet_name="Member_Data")

    # Basic cleaning
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("string").str.strip()

    numeric_cols = [
        "Age", "Experience_Years", "Technical_Skill_Pct",
        "Communication_Pct", "Career_Readiness_Pct"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 1. Dataset overview
    overview = pd.DataFrame({
        "Metric": [
            "Total records", "Total columns", "Duplicate rows",
            "Total missing values"
        ],
        "Value": [
            len(df), len(df.columns), int(df.duplicated().sum()),
            int(df.isna().sum().sum())
        ]
    })
    overview.to_csv(OUTPUT_DIR / "dataset_overview.csv", index=False)

    # 2. Missing values
    missing = df.isna().sum().rename("Missing_Count").to_frame()
    missing["Missing_Percentage"] = (missing["Missing_Count"] / max(len(df), 1) * 100).round(2)
    missing.to_csv(OUTPUT_DIR / "missing_values.csv")

    # 3. Numerical descriptive statistics
    df.describe(include="number").T.to_csv(OUTPUT_DIR / "numerical_summary.csv")

    # 4. Frequency summaries for important categorical columns
    categorical_cols = [
        "Education", "Specialization", "Location", "Industry",
        "Current_Role", "Top_Skill", "Job_Status", "Salary_Range",
        "Career_Level"
    ]
    for col in categorical_cols:
        if col in df.columns:
            result = df[col].value_counts(dropna=False).rename_axis(col).reset_index(name="Count")
            result.to_csv(OUTPUT_DIR / f"{col.lower()}_frequency.csv", index=False)

    # 5. Job-status analysis
    if "Job_Status" in df.columns:
        job_status = df["Job_Status"].value_counts(dropna=False).rename_axis("Job_Status").reset_index(name="Members")
        job_status["Percentage"] = (job_status["Members"] / max(len(df), 1) * 100).round(2)
        job_status.to_csv(OUTPUT_DIR / "job_status_analysis.csv", index=False)

    # 6. Career-readiness analysis by role
    if {"Current_Role", "Career_Readiness_Pct", "Technical_Skill_Pct"} <= set(df.columns):
        role_analysis = (
            df.groupby("Current_Role")
              .agg(
                  Members=("Current_Role", "size"),
                  Avg_Career_Readiness=("Career_Readiness_Pct", "mean"),
                  Avg_Technical_Skill=("Technical_Skill_Pct", "mean")
              )
              .round(2)
              .sort_values("Members", ascending=False)
        )
        role_analysis.to_csv(OUTPUT_DIR / "role_analysis.csv")

    # 7. Location analysis
    if {"Location", "Job_Status"} <= set(df.columns):
        location_analysis = pd.crosstab(df["Location"], df["Job_Status"])
        location_analysis["Total_Members"] = location_analysis.sum(axis=1)
        location_analysis.to_csv(OUTPUT_DIR / "location_job_status_analysis.csv")

    # 8. Correlation matrix
    numeric_data = df.select_dtypes(include="number")
    if not numeric_data.empty:
        numeric_data.corr().round(3).to_csv(OUTPUT_DIR / "correlation_matrix.csv")

    # 9. Human-readable report
    report_lines = [
        "CAREERLENS - DATA ANALYSIS REPORT",
        "=" * 40,
        f"Total records: {len(df)}",
        f"Total columns: {len(df.columns)}",
        f"Duplicate rows: {int(df.duplicated().sum())}",
        f"Missing values: {int(df.isna().sum().sum())}",
        "",
        "NUMERICAL SUMMARY",
        "-" * 40,
        df.describe(include="number").round(2).to_string(),
    ]
    if "Job_Status" in df.columns:
        report_lines += [
            "", "JOB STATUS COUNTS", "-" * 40,
            df["Job_Status"].value_counts(dropna=False).to_string()
        ]
    if "Career_Level" in df.columns:
        report_lines += [
            "", "CAREER LEVEL COUNTS", "-" * 40,
            df["Career_Level"].value_counts(dropna=False).to_string()
        ]

    (OUTPUT_DIR / "analysis_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
    print("Data analysis completed successfully.")
    print(f"Results saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
