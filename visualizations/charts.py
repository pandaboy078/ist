import os
import sys
# Add parent directory to sys.path to allow sibling folder imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

# Define styling constants for futuristic dark theme
BG_COLOR = "#070709"
CARD_BG = "#121217"
TEXT_COLOR = "#ffffff"
MUTED_TEXT = "#8e8e9f"
NEON_GREEN = "#00ff66"
NEON_ORANGE = "#ff5500"
ACCENT_BLUE = "#00ccff"
ACCENT_PURPLE = "#cc33ff"
GRID_COLOR = "#22222b"

plt.rcParams.update({
    "figure.facecolor": BG_COLOR,
    "axes.facecolor": CARD_BG,
    "text.color": TEXT_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": MUTED_TEXT,
    "ytick.color": MUTED_TEXT,
    "axes.edgecolor": GRID_COLOR,
    "grid.color": GRID_COLOR,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10
})

def generate_all_charts():
    # Ensure asset directory exists
    img_dir = "assets/images"
    os.makedirs(img_dir, exist_ok=True)
    
    # 1. Load Datasets
    population = pd.read_csv("dataset/dataset.csv")
    srs = pd.read_csv("dataset/sample_random_train.csv")
    sys_sam = pd.read_csv("dataset/sample_systematic_train.csv")
    strat = pd.read_csv("dataset/sample_stratified_train.csv")
    clust = pd.read_csv("dataset/sample_cluster_train.csv")
    
    # Load evaluation results
    with open("analysis/results.json", "r") as f:
        eval_data = json.load(f)
        
    table_df = pd.DataFrame(eval_data["table"])
    summary_df = pd.DataFrame(eval_data["sampling_summary"])
    verdict = eval_data["verdict"]
    
    # ----------------------------------------------------
    # Chart 1: Runs vs Dot Balls (Population & Samples)
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(population["Dot_Balls"], population["Runs"], color="#1c1c24", alpha=0.2, s=10, label="Population Baseline")
    ax.scatter(strat["Dot_Balls"], strat["Runs"], color=NEON_GREEN, alpha=0.8, s=15, label="Stratified Sample Overlay")
    ax.set_title("Runs vs Dot Balls (Population & Sample Representation)", pad=15, fontweight="bold")
    ax.set_xlabel("Dot Balls Bowled Against Batsman")
    ax.set_ylabel("Runs Scored")
    ax.grid(True, linestyle=":", alpha=0.5)
    
    # Simple regression fit to show alignment
    z = np.polyfit(population["Dot_Balls"], population["Runs"], 1)
    p = np.poly1d(z)
    x_vals = np.linspace(population["Dot_Balls"].min(), population["Dot_Balls"].max(), 100)
    ax.plot(x_vals, p(x_vals), color=NEON_ORANGE, linestyle="--", linewidth=1.5, label="Population Trendline")
    
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart1_runs_vs_dot.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart1_runs_vs_dot.png")

    # ----------------------------------------------------
    # Chart 2: Strike Rate vs Efficiency
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(population["Strike_Rate"], population["Efficiency_Score"], c=population["Runs"], cmap="viridis", alpha=0.8, s=12)
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Total Runs", color=TEXT_COLOR)
    cbar.ax.yaxis.set_tick_params(color=MUTED_TEXT)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=MUTED_TEXT)
    
    ax.set_title("Strike Rate vs Batting Efficiency Score", pad=15, fontweight="bold")
    ax.set_xlabel("Strike Rate")
    ax.set_ylabel("Efficiency Score (0 - 100)")
    ax.grid(True, linestyle=":", alpha=0.5)
    
    # Fit line
    z2 = np.polyfit(population["Strike_Rate"], population["Efficiency_Score"], 1)
    p2 = np.poly1d(z2)
    x_vals2 = np.linspace(population["Strike_Rate"].min(), population["Strike_Rate"].max(), 100)
    ax.plot(x_vals2, p2(x_vals2), color=NEON_ORANGE, linestyle="--", linewidth=1.5, label="Correlation Trend")
    ax.legend(loc="upper left")
    
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart2_strike_rate_vs_efficiency.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart2_strike_rate_vs_efficiency.png")

    # ----------------------------------------------------
    # Chart 3: Trees Planted by Batsman
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    top_trees = population.groupby("Player_Name")["Trees_Planted"].sum().sort_values(ascending=False).head(10)
    
    bars = ax.barh(top_trees.index[::-1], top_trees.values[::-1], color=NEON_GREEN, edgecolor="none", height=0.6)
    ax.set_title("Top 10 Environmental Impact Contributors (Trees Planted)", pad=15, fontweight="bold")
    ax.set_xlabel("Total Trees Planted (Dot Balls × 19)")
    ax.grid(True, axis="x", linestyle=":", alpha=0.5)
    
    # Add values
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + (top_trees.max() * 0.01), 
            bar.get_y() + bar.get_height()/2, 
            f"{int(width):,}", 
            va="center", ha="left", color=TEXT_COLOR, fontsize=9
        )
        
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart3_trees_batsman.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart3_trees_batsman.png")

    # ----------------------------------------------------
    # Chart 4: Trees Planted by Team
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 6))
    team_trees = population.groupby("Team")["Trees_Planted"].sum().sort_values(ascending=False)
    
    bars = ax.bar(team_trees.index, team_trees.values, color=ACCENT_BLUE, edgecolor="none", width=0.55)
    ax.set_title("Trees Planted by IPL Franchises (Green Dot Ball Initiative)", pad=15, fontweight="bold")
    ax.set_ylabel("Total Trees Planted")
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    
    # Add values
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2, 
            yval + (team_trees.max() * 0.01), 
            f"{int(yval):,}", 
            va="bottom", ha="center", color=TEXT_COLOR, fontsize=8, rotation=0
        )
        
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart4_trees_team.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart4_trees_team.png")

    # ----------------------------------------------------
    # Grouped datasets helpers
    # ----------------------------------------------------
    pivoted_df = table_df.pivot(index="Sampling_Method", columns="Model")
    pivoted_df.index = [s.replace("sample_", "").title() for s in pivoted_df.index]
    pivoted_df = pivoted_df.reindex(["Population", "Random", "Systematic", "Stratified", "Cluster"])
    x = np.arange(len(pivoted_df.index))
    width = 0.24

    # ----------------------------------------------------
    # Chart 5: Sampling Technique vs R²
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    sub_r2 = pivoted_df["R2_Score"]
    rects1 = ax.bar(x - width, sub_r2["linear_regression"], width, label="Linear Regression", color=ACCENT_BLUE)
    rects2 = ax.bar(x, sub_r2["random_forest"], width, label="Random Forest", color=NEON_ORANGE)
    rects3 = ax.bar(x + width, sub_r2["xgboost"], width, label="XGBoost", color=NEON_GREEN)
    
    ax.set_title("R² Score Comparison Across Sampling Methods", pad=15, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(pivoted_df.index)
    ax.set_ylabel("R² Score")
    ax.set_ylim(0.90, 1.01)
    ax.legend(loc="lower left")
    ax.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart5_sampling_r2.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart5_sampling_r2.png")

    # ----------------------------------------------------
    # Chart 6: Sampling Technique vs RMSE
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    sub_rmse = pivoted_df["RMSE"]
    rects1 = ax.bar(x - width, sub_rmse["linear_regression"], width, label="Linear Regression", color=ACCENT_BLUE)
    rects2 = ax.bar(x, sub_rmse["random_forest"], width, label="Random Forest", color=NEON_ORANGE)
    rects3 = ax.bar(x + width, sub_rmse["xgboost"], width, label="XGBoost", color=NEON_GREEN)
    
    ax.set_title("RMSE Comparison Across Sampling Methods", pad=15, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(pivoted_df.index)
    ax.set_ylabel("Root Mean Squared Error (RMSE)")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart6_sampling_rmse.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart6_sampling_rmse.png")

    # ----------------------------------------------------
    # Chart 7: Sampling Technique vs MAE
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    sub_mae = pivoted_df["MAE"]
    rects1 = ax.bar(x - width, sub_mae["linear_regression"], width, label="Linear Regression", color=ACCENT_BLUE)
    rects2 = ax.bar(x, sub_mae["random_forest"], width, label="Random Forest", color=NEON_ORANGE)
    rects3 = ax.bar(x + width, sub_mae["xgboost"], width, label="XGBoost", color=NEON_GREEN)
    
    ax.set_title("MAE Comparison Across Sampling Methods", pad=15, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(pivoted_df.index)
    ax.set_ylabel("Mean Absolute Error (MAE)")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart7_sampling_mae.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart7_sampling_mae.png")

    # ----------------------------------------------------
    # Chart 8: Model Comparison
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    model_r2 = table_df.groupby("Model")["R2_Score"].mean().reset_index()
    
    bars = ax.bar(
        [m.replace("_", " ").title() for m in model_r2["Model"]], 
        model_r2["R2_Score"], 
        color=[ACCENT_BLUE, NEON_ORANGE, NEON_GREEN], 
        width=0.4
    )
    ax.set_title("Machine Learning Model Fit (Mean R²)", pad=15, fontweight="bold")
    ax.set_ylabel("Average R² Score")
    ax.set_ylim(0.92, 1.01)
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2, 
            yval + 0.005, 
            f"{yval:.5f}", 
            va="bottom", ha="center", color=TEXT_COLOR, fontsize=9
        )
        
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart8_model_comparison.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart8_model_comparison.png")

    # ----------------------------------------------------
    # Chart 9: Population vs Sample Comparison (Distribution)
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Custom histogram distribution lines
    def plot_dist(data, label, color, linestyle="-", lw=1.5):
        counts, bins = np.histogram(data["Efficiency_Score"], bins=20, range=(0, 100), density=True)
        centers = 0.5 * (bins[:-1] + bins[1:])
        ax.plot(centers, counts, label=label, color=color, linestyle=linestyle, lw=lw)
        ax.fill_between(centers, counts, alpha=0.04, color=color)
        
    plot_dist(population, "True Population", TEXT_COLOR, lw=2.5)
    plot_dist(srs, "Simple Random", ACCENT_BLUE, "--")
    plot_dist(sys_sam, "Systematic", NEON_ORANGE, ":")
    plot_dist(strat, "Stratified", NEON_GREEN, "-.")
    plot_dist(clust, "Cluster", ACCENT_PURPLE, "-.")
    
    ax.set_title("Efficiency Score Probability Density (Population vs Samples)", pad=15, fontweight="bold")
    ax.set_xlabel("Batting Efficiency Score (0 - 100)")
    ax.set_ylabel("Probability Density")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper right")
    
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart9_pop_vs_sample.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart9_pop_vs_sample.png")

    # ----------------------------------------------------
    # Chart 10: Final Sampling Ranking
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.axis("off")
    
    # Draw glowing card boarder
    rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=True, color=CARD_BG, ec=NEON_GREEN, lw=2, transform=ax.transAxes)
    ax.add_patch(rect)
    
    # Add title headers
    ax.text(0.5, 0.88, "FINAL STATISTICAL SAMPLING RANKING", color=NEON_GREEN, fontsize=16, fontweight="bold", ha="center", va="center")
    ax.text(0.5, 0.82, "Ranked by generalizability and accuracy to true population", color=MUTED_TEXT, fontsize=9.5, ha="center", va="center")
    ax.plot([0.1, 0.9], [0.77, 0.77], color=GRID_COLOR, lw=1)
    
    # Rankings data
    rankings = [
        ("Rank 1", "SIMPLE RANDOM", "R² Deviation: ~0.000", "Best overall generalizability, fully preserves variance.", NEON_GREEN),
        ("Rank 2", "STRATIFIED (TEAM)", "R² Deviation: ~0.000", "Preserves team ratios perfectly, holds low bias.", ACCENT_BLUE),
        ("Rank 3", "SYSTEMATIC", "R² Deviation: ~0.005", "Vulnerable to periodicity issues if sorted, otherwise stable.", NEON_ORANGE),
        ("Rank 4", "CLUSTER (TEAM)", "R² Deviation: ~0.022", "High variance, team-specific cluster bias introduced.", ACCENT_PURPLE)
    ]
    
    y_pos = 0.64
    for rank, name, deviation, description, color in rankings:
        # Drawing rank cards
        ax.text(0.12, y_pos, rank, color=color, fontsize=13, fontweight="bold")
        ax.text(0.30, y_pos, name, color=TEXT_COLOR, fontsize=14, fontweight="bold")
        ax.text(0.72, y_pos, deviation, color=MUTED_TEXT, fontsize=10.5, fontweight="bold")
        ax.text(0.12, y_pos - 0.06, description, color=MUTED_TEXT, fontsize=9.5)
        
        # Grid line
        ax.plot([0.1, 0.9], [y_pos - 0.09, y_pos - 0.09], color=GRID_COLOR, lw=0.5)
        y_pos -= 0.16
        
    ax.text(0.5, 0.07, "Conclusion: Simple Random & Stratified Sampling are ideal for cricket sports analytics modeling.", 
            color=TEXT_COLOR, fontsize=9.0, ha="center", fontstyle="italic")
            
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "chart10_final_ranking.png"), dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("✔ Chart saved: chart10_final_ranking.png")

if __name__ == "__main__":
    generate_all_charts()
