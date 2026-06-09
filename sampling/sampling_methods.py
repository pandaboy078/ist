import os
import pandas as pd
import numpy as np

def load_data(filepath="dataset/dataset.csv"):
    """Loads the clean dataset."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Clean dataset not found at {filepath}. Please run data_cleaning.py first.")
    return pd.read_csv(filepath)

def simple_random_sampling(df, sample_size=150, seed=42):
    """Generates a Simple Random Sample of size 150."""
    return df.sample(n=sample_size, random_state=seed).reset_index(drop=True)

def systematic_sampling(df, sample_size=150, seed=42):
    """Generates a Systematic Sample of size 150."""
    np.random.seed(seed)
    N = len(df)
    k = N // sample_size
    
    # Random starting point in [0, k-1]
    start = np.random.randint(0, k)
    
    # Generate indices
    indices = [start + i * k for i in range(sample_size)]
    
    # Slice the dataframe
    return df.iloc[indices].reset_index(drop=True)

def stratified_sampling(df, sample_size=150, strata_col="Team", seed=42):
    """Generates a Stratified Sample of size 150, maintaining Team proportion."""
    np.random.seed(seed)
    
    # Calculate proportions
    proportions = df[strata_col].value_counts(normalize=True)
    
    # Calculate exact allocation
    allocations = {strata: int(np.round(prop * sample_size)) for strata, prop in proportions.items()}
    
    # Adjust to make sure total sample size is exactly sample_size
    total_allocated = sum(allocations.values())
    diff = sample_size - total_allocated
    
    if diff != 0:
        # Add/remove from the largest stratum or list of strata
        sorted_strata = list(proportions.index)
        for i in range(abs(diff)):
            strata_to_adjust = sorted_strata[i % len(sorted_strata)]
            if diff > 0:
                allocations[strata_to_adjust] += 1
            else:
                allocations[strata_to_adjust] -= 1
                
    # Sample from each stratum
    sample_dfs = []
    for strata, size in allocations.items():
        strata_df = df[df[strata_col] == strata]
        # If strata size is smaller than allocated, sample with replacement or limit
        actual_size = min(len(strata_df), size)
        if actual_size > 0:
            sample_dfs.append(strata_df.sample(n=actual_size, random_state=seed))
        
    return pd.concat(sample_dfs).sample(frac=1, random_state=seed).reset_index(drop=True)

def cluster_sampling(df, sample_size=150, cluster_col="Team", seed=42):
    """Generates a Cluster Sample where each Team is a cluster. Shuffles clusters and selects whole clusters."""
    np.random.seed(seed)
    
    # Unique clusters (Teams)
    unique_clusters = list(df[cluster_col].unique())
    np.random.shuffle(unique_clusters)
    
    selected_clusters = []
    current_size = 0
    
    for cluster in unique_clusters:
        cluster_df = df[df[cluster_col] == cluster]
        selected_clusters.append(cluster_df)
        current_size += len(cluster_df)
        
        # Stop once we have reached or exceeded the sample_size or are close to it
        if current_size >= sample_size:
            break
            
    # Combine selected clusters
    cluster_sample = pd.concat(selected_clusters)
    
    # Optionally, we can shuffle the rows
    return cluster_sample.sample(frac=1, random_state=seed).reset_index(drop=True)

if __name__ == "__main__":
    os.makedirs("sampling", exist_ok=True)
    
    print("Loading clean dataset...")
    df = load_data()
    print(f"Population dataset loaded: {len(df)} records.")
    
    # Generate samples
    print("\nGenerating sampling subsets...")
    
    srs_df = simple_random_sampling(df, sample_size=150)
    sys_df = systematic_sampling(df, sample_size=150)
    strat_df = stratified_sampling(df, sample_size=150)
    clust_df = cluster_sampling(df, sample_size=150)
    
    # Save samples
    srs_df.to_csv("dataset/sample_random.csv", index=False)
    sys_df.to_csv("dataset/sample_systematic.csv", index=False)
    strat_df.to_csv("dataset/sample_stratified.csv", index=False)
    clust_df.to_csv("dataset/sample_cluster.csv", index=False)
    
    print(f"✔ Simple Random Sample size: {len(srs_df)} (Saved to dataset/sample_random.csv)")
    print(f"✔ Systematic Sample size: {len(sys_df)} (Saved to dataset/sample_systematic.csv)")
    print(f"✔ Stratified Sample size: {len(strat_df)} (Saved to dataset/sample_stratified.csv)")
    print(f"✔ Cluster Sample size: {len(clust_df)} (Saved to dataset/sample_cluster.csv) -- Clusters chosen: {clust_df['Team'].nunique()} teams ({', '.join(clust_df['Team'].unique())})")
