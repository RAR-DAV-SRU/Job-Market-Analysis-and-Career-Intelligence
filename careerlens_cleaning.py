# ===== CareerLens data cleaning (Google Colab) =====
import pandas as pd
import numpy as np
from google.colab import files

# 1. Upload the Excel file
uploaded = files.upload()
fname = list(uploaded.keys())[0]

# 2. Load the main sheet
df = pd.read_excel(fname, sheet_name="Member_Data")
print("Original shape:", df.shape)

# 3. Standardise column names
df.columns = df.columns.str.strip().str.replace("%", "Pct").str.replace(" ", "_")

# 4. Trim whitespace and fix casing in text columns
text_cols = df.select_dtypes(include=["object", "string"]).columns
for c in text_cols:
    df[c] = df[c].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
df["Member_Name"] = df["Member_Name"].str.title()

# 5. Standardise categories (fix known variants)
df["Location"] = df["Location"].replace({"Bangalore": "Bengaluru", "Bombay": "Mumbai"})
df["Salary_Range"] = df["Salary_Range"].replace({"": "Not Provided", "nan": "Not Provided"})

# 6. Convert numeric columns and handle missing values
num_cols = ["Age", "Experience_Years", "Technical_Skill_Pct",
            "Communication_Pct", "Career_Readiness_Pct"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")
    df[c] = df[c].fillna(df[c].median())

# 7. Remove duplicates
df = df.drop_duplicates()
df = df.drop_duplicates(subset="Member_ID", keep="first")

# 8. Validate ranges (flag invalid rows, then remove)
bad = (
    ~df["Age"].between(15, 65)
    | ~df["Experience_Years"].between(0, 45)
    | (df["Experience_Years"] > df["Age"] - 15)  # experience impossible for age
    | ~df["Technical_Skill_Pct"].between(0, 100)
    | ~df["Communication_Pct"].between(0, 100)
    | ~df["Career_Readiness_Pct"].between(0, 100)
)
print("Invalid rows removed:", bad.sum())
df = df[~bad]

# 9. Make Career_Level consistent with experience (optional, edit thresholds)
def level(y):
    return "Entry Level" if y <= 2 else ("Junior" if y <= 6 else "Mid Level")
df["Career_Level_Check"] = df["Experience_Years"].apply(level)
print("Career_Level mismatches:", (df["Career_Level"] != df["Career_Level_Check"]).sum())
# To overwrite: df["Career_Level"] = df["Career_Level_Check"]
df = df.drop(columns="Career_Level_Check")

# 10. Fix dtypes and sort
df[num_cols] = df[num_cols].astype(int)
df = df.sort_values("Member_ID").reset_index(drop=True)

# 11. Final report
print("\nCleaned shape:", df.shape)
print("Missing values:\n", df.isna().sum())
print("\nJob status counts:\n", df["Job_Status"].value_counts())
display(df.head())

# 12. Rebuild summary sheets from the cleaned data
dashboard = pd.DataFrame({
    "Metric": ["Total Members", "Employed", "Looking for Job", "Higher Studies",
               "Internship", "Average Career Readiness %"],
    "Value": [len(df),
              (df.Job_Status == "Employed").sum(),
              (df.Job_Status == "Looking for Job").sum(),
              (df.Job_Status == "Higher Studies").sum(),
              (df.Job_Status == "Internship").sum(),
              round(df.Career_Readiness_Pct.mean(), 2)]
})
role = (df.groupby("Current_Role")
          .agg(Members=("Member_ID", "count"),
               Avg_Career_Readiness=("Career_Readiness_Pct", "mean"),
               Avg_Technical_Skill=("Technical_Skill_Pct", "mean"))
          .round(2).reset_index())
loc = (df.groupby("Location")
         .agg(Members=("Member_ID", "count"),
              Employed=("Job_Status", lambda s: (s == "Employed").sum()),
              Looking_For_Job=("Job_Status", lambda s: (s == "Looking for Job").sum()))
         .reset_index())

# 13. Save and download
out = "CareerLens_Cleaned_Final.xlsx"
with pd.ExcelWriter(out) as w:
    df.to_excel(w, sheet_name="Member_Data", index=False)
    dashboard.to_excel(w, sheet_name="Dashboard_Summary", index=False)
    role.to_excel(w, sheet_name="Role_Analytics", index=False)
    loc.to_excel(w, sheet_name="Location_Analytics", index=False)
files.download(out)



OUTPUT:
Cleaned shape: (500, 16)
Missing values:
 Member_ID               0
Member_Name             0
Age                     0
Education               0
Specialization          0
Location                0
Industry                0
Current_Role            0
Top_Skill               0
Experience_Years        0
Job_Status              0
Salary_Range            0
Technical_Skill_Pct     0
Communication_Pct       0
Career_Readiness_Pct    0
Career_Level            0
dtype: int64

Job status counts:
 Job_Status
Employed           351
Looking for Job     70
Higher Studies      57
Internship          22
Name: count, dtype: int64
