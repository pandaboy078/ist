import os
import sys
# Add parent directory to sys.path to allow sibling folder imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# Import sampling functions from our sampling methods script
from sampling.sampling_methods import (
    simple_random_sampling,
    systematic_sampling,
    stratified_sampling,
    cluster_sampling
)

def train_and_save_models(seed=42):
    """Splits population dataset, generates samples, trains 15 models, and saves them."""
    # Ensure directories exist
    os.makedirs("models/saved_models", exist_ok=True)
    
    # 1. Load the clean population dataset
    df = pd.read_csv("dataset/dataset.csv")
    print(f"Population dataset loaded: {len(df)} records.")
    
    # 2. Split into Train (80%) and Test (20%) populations
    # We use random state to ensure reproducibility
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=seed)
    
    # Save the splits
    train_df.to_csv("dataset/population_train.csv", index=False)
    test_df.to_csv("dataset/population_test.csv", index=False)
    print(f"Split completed: Train population = {len(train_df)} rows, Test population = {len(test_df)} rows.")
    
    # 3. Generate sampling subsets from the training population
    print("\nGenerating training subsets from train population...")
    datasets = {
        "population": train_df,
        "sample_random": simple_random_sampling(train_df, sample_size=150, seed=seed),
        "sample_systematic": systematic_sampling(train_df, sample_size=150, seed=seed),
        "sample_stratified": stratified_sampling(train_df, sample_size=150, strata_col="Team", seed=seed),
        "sample_cluster": cluster_sampling(train_df, sample_size=150, cluster_col="Team", seed=seed)
    }
    
    # Print sample sizes
    for name, data in datasets.items():
        print(f"  - {name}: {len(data)} rows")
        # Save sample to dataset folder
        data.to_csv(f"dataset/{name}_train.csv", index=False)
        
    # 4. Define features and target
    features = ["Runs", "Batting_Average", "Strike_Rate", "Dot_Balls", "Trees_Planted"]
    target = "Efficiency_Score"
    
    # 5. Define model algorithms
    model_constructors = {
        "linear_regression": lambda: LinearRegression(),
        "random_forest": lambda: RandomForestRegressor(n_estimators=100, random_state=seed, n_jobs=-1),
        "xgboost": lambda: XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=seed, n_jobs=-1)
    }
    
    # 6. Train and save models
    print("\nTraining models...")
    for model_name, constructor in model_constructors.items():
        print(f"Algorithm: {model_name.replace('_', ' ').title()}")
        for data_name, train_subset in datasets.items():
            X_train = train_subset[features]
            y_train = train_subset[target]
            
            # Instantiate model
            model = constructor()
            
            # Fit model
            model.fit(X_train, y_train)
            
            # Save model
            model_path = f"models/saved_models/model_{model_name}_{data_name}.joblib"
            joblib.dump(model, model_path)
            print(f"  ✔ Trained on '{data_name}' -> Saved to {model_path}")
            
    print("\nAll 15 models trained and saved successfully.")

if __name__ == "__main__":
    train_and_save_models()
