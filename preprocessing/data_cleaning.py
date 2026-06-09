import os
import pandas as pd
import numpy as np

def clean_data(raw_path="dataset/raw_dataset.csv", clean_path="dataset/dataset.csv"):
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw dataset not found at '{raw_path}'")
        
    print(f"Loading raw dataset from '{raw_path}'...")
    df = pd.read_csv(raw_path)
    initial_count = len(df)
    
    # 1. Duplicate removal
    df = df.drop_duplicates().reset_index(drop=True)
    duplicates_removed = initial_count - len(df)
    
    # 2. Numerical conversion
    numeric_cols = ["Matches", "Innings", "Runs", "Balls_Faced", "Dot_Balls", "Dismissals"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        
    # 3. Outlier and inactive player handling
    # We filter out players with fewer than 15 balls faced to ensure statistical reliability
    inactive_mask = df["Balls_Faced"] < 15
    inactive_count = inactive_mask.sum()
    df = df[~inactive_mask].reset_index(drop=True)
    
    # 4. Handle Missing Values & Logical Imputation
    # Fill empty teams with 'Unknown'
    missing_teams = df["Team"].isna().sum()
    df["Team"] = df["Team"].fillna("Unknown")
    
    # Calculate basic cricket metrics
    # Batting Average = Runs / Dismissals
    # If dismissals is 0, average is set to Runs (never dismissed)
    df["Batting_Average"] = np.where(
        df["Dismissals"] > 0,
        (df["Runs"] / df["Dismissals"]).round(2),
        df["Runs"].astype(float).round(2)
    )
    
    # Strike Rate = (Runs / Balls_Faced) * 100
    df["Strike_Rate"] = np.where(
        df["Balls_Faced"] > 0,
        ((df["Runs"] / df["Balls_Faced"]) * 100).round(2),
        0.0
    )
    
    # Dot Ball Percentage = (Dot_Balls / Balls_Faced) * 100
    df["Dot_Ball_Percentage"] = np.where(
        df["Balls_Faced"] > 0,
        ((df["Dot_Balls"] / df["Balls_Faced"]) * 100).round(2),
        0.0
    )
    
    # 5. Green Dot Ball Initiative Feature Engineering
    # Trees Planted = Dot Balls * 19
    df["Trees_Planted"] = df["Dot_Balls"] * 19
    
    # 6. Feature Normalization & Efficiency Score
    # Min-max normalization values across the clean population
    runs_min, runs_max = df["Runs"].min(), df["Runs"].max()
    sr_min, sr_max = df["Strike_Rate"].min(), df["Strike_Rate"].max()
    avg_min, avg_max = df["Batting_Average"].min(), df["Batting_Average"].max()
    trees_min, trees_max = df["Trees_Planted"].min(), df["Trees_Planted"].max()
    
    # Normalize features helper
    def norm(col, col_min, col_max):
        if col_max == col_min:
            return 0.0
        return (col - col_min) / (col_max - col_min)
        
    df["Norm_Runs"] = norm(df["Runs"], runs_min, runs_max)
    df["Norm_Strike_Rate"] = norm(df["Strike_Rate"], sr_min, sr_max)
    df["Norm_Batting_Average"] = norm(df["Batting_Average"], avg_min, avg_max)
    df["Norm_Trees_Planted"] = norm(df["Trees_Planted"], trees_min, trees_max)
    
    # Efficiency Score Formula:
    # 0.40 * Norm(Runs) + 0.30 * Norm(Strike_Rate) + 0.20 * Norm(Batting_Average) + 0.10 * Norm(Trees_Planted)
    # Scaled between 0 and 100.
    df["Efficiency_Score"] = (
        (0.40 * df["Norm_Runs"] +
         0.30 * df["Norm_Strike_Rate"] +
         0.20 * df["Norm_Batting_Average"] +
         0.10 * df["Norm_Trees_Planted"]) * 100
    ).round(4)
    
    # Drop temp norm columns to keep output dataset clean and readable
    df = df.drop(columns=["Norm_Runs", "Norm_Strike_Rate", "Norm_Batting_Average", "Norm_Trees_Planted"])
    
    # Save the cleaned dataset
    df.to_csv(clean_path, index=False)
    final_count = len(df)
    
    print(f"✔ Records Before Cleaning: {initial_count}")
    # We report imputed as missing_teams because batting average and strike rate were computed logically
    print(f"✔ Records After Cleaning: {final_count} (Removed {inactive_count} inactive/bowler profiles)")
    print(f"✔ Duplicates Removed: {duplicates_removed}")
    print(f"✔ Missing Teams Imputed: {missing_teams}")
    print(f"✔ Computed features: Batting_Average, Strike_Rate, Dot_Ball_Percentage, Trees_Planted, and Efficiency_Score")
    
    return df

if __name__ == "__main__":
    clean_data()
