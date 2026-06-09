import os
import sys
# Add parent directory to sys.path to allow sibling folder imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

def evaluate_models():
    # Ensure directories exist
    os.makedirs("analysis", exist_ok=True)
    
    # 1. Load Test set
    test_df = pd.read_csv("dataset/population_test.csv")
    features = ["Runs", "Batting_Average", "Strike_Rate", "Dot_Balls", "Trees_Planted"]
    target = "Efficiency_Score"
    
    X_test = test_df[features]
    y_test = test_df[target]
    
    # 2. Setup loops
    models = ["linear_regression", "random_forest", "xgboost"]
    datasets = ["population", "sample_random", "sample_systematic", "sample_stratified", "sample_cluster"]
    
    results = []
    
    # Loop and evaluate
    for model_name in models:
        for data_name in datasets:
            model_path = f"models/saved_models/model_{model_name}_{data_name}.joblib"
            if not os.path.exists(model_path):
                print(f"Warning: Model not found at {model_path}")
                continue
                
            # Load model
            model = joblib.load(model_path)
            
            # Predict
            preds = model.predict(X_test)
            
            # Calculate metrics
            r2 = r2_score(y_test, preds)
            mae = mean_absolute_error(y_test, preds)
            rmse = root_mean_squared_error(y_test, preds)
            
            results.append({
                "Model": model_name,
                "Sampling_Method": data_name,
                "R2_Score": round(float(r2), 6),
                "MAE": round(float(mae), 6),
                "RMSE": round(float(rmse), 6)
            })
            
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save CSV
    results_df.to_csv("analysis/results_table.csv", index=False)
    print("✔ Saved results to 'analysis/results_table.csv'")
    
    # 3. Determine Final Verdict
    # Best Model: The one with highest R2 score on average, or overall highest
    best_model_row = results_df.loc[results_df["R2_Score"].idxmax()]
    
    # Let's find the best model overall (highest R2)
    overall_best_idx = results_df["R2_Score"].idxmax()
    overall_best = results_df.iloc[overall_best_idx]
    
    # To determine the best sampling method:
    # We compare the performance of models trained on samples to those trained on the full population.
    # The "best" sampling technique is the one that achieves the closest performance to the full population model,
    # or the highest average R2 score across all algorithms (excluding the population dataset itself).
    sample_results = results_df[results_df["Sampling_Method"] != "population"]
    
    # Calculate average performance by sampling method
    sampling_summary = sample_results.groupby("Sampling_Method").agg({
        "R2_Score": "mean",
        "MAE": "mean",
        "RMSE": "mean"
    }).reset_index()
    
    best_sampling_idx = sampling_summary["R2_Score"].idxmax()
    best_sampling = sampling_summary.iloc[best_sampling_idx]
    
    # Also find the highest R2, lowest RMSE, lowest MAE for the samples
    best_sample_row = sample_results.loc[sample_results["R2_Score"].idxmax()]
    
    verdict = {
        "best_overall_model": str(overall_best["Model"]),
        "best_overall_sampling": str(overall_best["Sampling_Method"]),
        "best_overall_r2": float(overall_best["R2_Score"]),
        "best_overall_rmse": float(overall_best["RMSE"]),
        "best_overall_mae": float(overall_best["MAE"]),
        
        "best_sample_model": str(best_sample_row["Model"]),
        "best_sample_sampling": str(best_sample_row["Sampling_Method"]),
        "best_sample_r2": float(best_sample_row["R2_Score"]),
        "best_sample_rmse": float(best_sample_row["RMSE"]),
        "best_sample_mae": float(best_sample_row["MAE"]),
        
        "best_sampling_method_by_avg_r2": str(best_sampling["Sampling_Method"]),
        "best_sampling_avg_r2": float(best_sampling["R2_Score"]),
        "best_sampling_avg_rmse": float(best_sampling["RMSE"]),
        "best_sampling_avg_mae": float(best_sampling["MAE"]),
        
        "population_baseline": results_df[results_df["Sampling_Method"] == "population"].to_dict(orient="records")
    }
    
    # Export results.json containing table and verdict
    export_data = {
        "table": results,
        "verdict": verdict,
        "sampling_summary": sampling_summary.to_dict(orient="records")
    }
    
    with open("analysis/results.json", "w") as f:
        json.dump(export_data, f, indent=4)
    print("✔ Saved results and verdict to 'analysis/results.json'")
    
    # Output to console
    print("\n" + "="*60)
    print("                      MODEL EVALUATION REPORT")
    print("="*60)
    print(results_df.to_string(index=False))
    print("="*60)
    print("                      FINAL VERDICT ANALYSIS")
    print("="*60)
    print(f"✔ Best Performing Model Overall: {verdict['best_overall_model'].replace('_', ' ').title()} trained on {verdict['best_overall_sampling'].replace('_', ' ').title()}")
    print(f"  - R² Score: {verdict['best_overall_r2']:.6f}")
    print(f"  - RMSE:     {verdict['best_overall_rmse']:.6f}")
    print(f"  - MAE:      {verdict['best_overall_mae']:.6f}")
    print(f"\n✔ Best Sampling Technique (Highest Avg R²): {verdict['best_sampling_method_by_avg_r2'].replace('_', ' ').title()}")
    print(f"  - Average Sample R² Score: {verdict['best_sampling_avg_r2']:.6f}")
    print(f"  - Average Sample RMSE:     {verdict['best_sampling_avg_rmse']:.6f}")
    print(f"  - Average Sample MAE:      {verdict['best_sampling_avg_mae']:.6f}")
    print("="*60)
    
    return results_df

if __name__ == "__main__":
    evaluate_models()
