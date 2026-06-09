# IPL Batsman Efficiency & Green Dot Ball Sustainability Analytics

An industry-grade, research-focused sports analytics and sustainability telemetry dashboard. This platform investigates how various statistical sampling techniques impact machine learning regression accuracy when evaluating batsman performance, integrated with the environmental **IPL Green Dot Ball Sustainability Initiative**.

---

## 🚀 Project Overview

This project implements a complete pipeline (data generation, cleaning, sampling, machine learning model training, validation, and visual reporting) that analyzes IPL batting metrics. 

### Key Dual-Objectives
1. **Cricket Performance Evaluation**: Engineering a multi-objective **Batting Efficiency Score** summarizing scoring capacity, scoring speed, consistency, and eco-contribution.
2. **Environmental Impact Tracking**: Quantifying carbon offset contributions via the **Green Dot Ball Initiative** (where every dot ball bowled plants 19 trees) in accordance with UN Sustainable Development Goals (**SDG 13: Climate Action** and **SDG 15: Life on Land**).

The research compares model training on **Simple Random**, **Systematic**, **Stratified**, and **Cluster** samples of size 2,500 against the full population training baseline to analyze bias and representation.

---

## 📂 Project Structure

```text
IPL_GreenDotBall_Project/
│
├── dataset/
│   ├── raw_dataset.csv           # Raw dirty batsman data (~12,000 records)
│   ├── dataset.csv               # Clean, preprocessed population (~10,000 records)
│   ├── population_train.csv      # 80% train split from clean population
│   ├── population_test.csv       # 20% test split (gold standard evaluation)
│   └── *_train.csv               # Extracted train samples (SRS, Systematic, Stratified, Cluster)
│
├── preprocessing/
│   └── data_cleaning.py          # Data cleaning, outlier removal, normalization
│
├── sampling/
│   └── sampling_methods.py       # SRS, Systematic, Stratified, and Cluster algorithms
│
├── models/
│   ├── saved_models/             # 15 serialized trained model joblibs
│   └── model_training.py         # Trains 3 regressors on 5 datasets
│
├── analysis/
│   ├── evaluation.py             # Computes R², MAE, RMSE metrics
│   ├── results_table.csv         # Tabulated metric comparisons
│   └── results.json              # Aggregated metrics and analytical verdict
│
├── visualizations/
│   └── charts.py                 # Generates 12 dark-themed matplotlib PNG charts
│
├── assets/
│   ├── css/
│   │   └── style.css             # Futuristic UI style sheet (neon + glassmorphism)
│   ├── js/
│   │   └── dashboard.js          # Interactive counters, API fetching, Chart.js logic
│   └── images/                   # Export path for matplotlib charts
│
├── app.py                        # Flask backend server & pipeline orchestrator
├── index.html                    # Single-page dashboard client
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## 🛠️ Installation & Setup

Ensure you have **Python 3.10+** and **Node.js** installed.

### 1. Clone & Navigate
```bash
cd /Users/sampath/Desktop/AAT-IST
```

### 2. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```
> **Note for macOS Users:** If XGBoost fails to load, install the OpenMP runtime library via Homebrew:
> ```bash
> brew install libomp
> ```

### 3. Initialize the Data & Modeling Pipeline
You can trigger the entire pipeline using the python command line:
```bash
# Generate, clean, sample, train, evaluate, and output charts:
python3 preprocessing/data_cleaning.py
python3 sampling/sampling_methods.py
python3 models/model_training.py
python3 analysis/evaluation.py
python3 visualizations/charts.py
```
*Alternatively, you can run this pipeline directly from the Web Dashboard.*

### 4. Launch the Web Telemetry Dashboard
```bash
python3 app.py
```
Open your browser and navigate to **[http://127.0.0.1:5001](http://127.0.0.1:5001)**.

---

## 📊 Methodology & Formulas

### 1. Feature Engineering
* **Trees Planted Formula**:
  $$\text{Trees Planted} = \text{Dot Balls} \times 19$$
* **Batting Efficiency Score**:
  $$\text{Efficiency Score} = 0.4 \times \text{Norm}(\text{Runs}) + 0.3 \times \text{Norm}(\text{Strike Rate}) + 0.2 \times \text{Norm}(\text{Batting Average}) + 0.1 \times \text{Norm}(\text{Trees Planted})$$
  *Where $\text{Norm}(X)$ represents Min-Max Normalization to scale $[0, 1]$:*
  $$\text{Norm}(X) = \frac{X - X_{\min}}{X_{\max} - X_{\min}}$$

### 2. Statistical Sampling Techniques (Sample Size $n = 2500$)
* **Simple Random Sampling (SRS)**: Each member of the population has an equal probability of selection.
* **Systematic Sampling**: Select a random index $start \in [0, k-1]$, and pull every $k$-th record ($k = N/n$) thereafter.
* **Stratified Sampling**: The population is stratified by `Team` and proportionate allocations are sampled from each group to maintain team proportions:
  $$\text{stratum } n_i = \text{round}\left( \frac{N_i}{N} \times n \right)$$
* **Cluster Sampling**: Shuffles teams (clusters) and includes all records from selected teams until cumulative size reaches $\approx 2500$.

### 3. Regressor Models
* **Linear Regression**: A standard linear combination modeling baseline.
* **Random Forest Regressor**: Ensembled decision tree regressor using bagging.
* **XGBoost Regressor**: Optimized gradient boosting algorithm.

---

## 🍃 Sustainability Alignment (UN SDGs)

* **SDG 13 (Climate Action)**: Integrates sports analytics directly with carbon offsetting. By gamifying environmental contributions (trees planted per dot ball), it outlines a data-driven path for franchises to track their ecological footprint.
* **SDG 15 (Life on Land)**: By planting trees, the project directly addresses land restoration, soil erosion prevention, biodiversity conservation, and combating deforestation.

---

## 🎯 Findings & Analytical Verdict
1. **Best Model**: **Linear Regression** achieves a perfect R² of **1.0** because the target metric (`Efficiency_Score`) is calculated directly as a linear combination of normalized features. Tree-based regressors (XGBoost, Random Forest) also achieve extremely high fits (R² > 0.995) but are limited by split-based discretization.
2. **Best Sampling Technique**: **Stratified Sampling** and **Simple Random Sampling** show the highest generalizability. **Cluster Sampling** displays a slightly higher variance and can introduce team-specific bias if the selected clusters (teams) deviate from the overall average run distribution.
