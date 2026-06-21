import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, mean_squared_error, r2_score
import joblib
import json
import os
import warnings

warnings.filterwarnings('ignore')

os.makedirs('models/saved', exist_ok=True)
os.makedirs('assets', exist_ok=True)

print("Starting Advanced AI Pipeline...")

# 1. Load Data
df = pd.read_csv('dataset/dataset.csv')
features = ['Matches', 'Innings', 'Runs', 'Balls_Faced', 'Dot_Balls', 'Batting_Average', 'Strike_Rate']
X_raw = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)
joblib.dump(scaler, 'models/saved/ai_scaler.pkl')

# 2. Target Variable creation for 4-class Classification
# Elite Performer, High Performer, Average Performer, Needs Improvement
pct_80 = np.percentile(df['Efficiency_Score'], 80)
pct_50 = np.percentile(df['Efficiency_Score'], 50)
pct_20 = np.percentile(df['Efficiency_Score'], 20)

def categorize(score):
    if score >= pct_80: return 3 # Elite
    elif score >= pct_50: return 2 # High
    elif score >= pct_20: return 1 # Average
    else: return 0 # Needs Improvement

y = df['Efficiency_Score'].apply(categorize)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

# 3. Initial Classification Model
base_rf = RandomForestClassifier(random_state=42)
base_rf.fit(X_train, y_train)
y_pred_base = base_rf.predict(X_test)
acc_before = accuracy_score(y_test, y_pred_base)

# 4. Hyperparameter Tuning using GridSearchCV
print("Running GridSearchCV...")
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10, 15],
    'min_samples_split': [2, 5, 10]
}
grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

best_rf = grid_search.best_estimator_
y_pred_tuned = best_rf.predict(X_test)
acc_after = accuracy_score(y_test, y_pred_tuned)

y_prob_tuned = best_rf.predict_proba(X_test)
prec = precision_score(y_test, y_pred_tuned, average='weighted', zero_division=0)
rec = recall_score(y_test, y_pred_tuned, average='weighted', zero_division=0)
f1 = f1_score(y_test, y_pred_tuned, average='weighted', zero_division=0)
roc_auc = roc_auc_score(y_test, y_prob_tuned, multi_class='ovr')
mse = mean_squared_error(y_test, y_pred_tuned)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred_tuned)

# 5. Overfitting Analysis
train_acc = accuracy_score(y_train, best_rf.predict(X_train))
diff = train_acc - acc_after
if diff > 0.15: overfitting_conclusion = "Overfitting (High variance between train and test)"
elif diff < -0.05: overfitting_conclusion = "Underfitting (Test > Train abnormally)"
else: overfitting_conclusion = "Good Generalization (Model performs consistently)"

# 6. Cross Validation
cv_scores = cross_val_score(best_rf, X_scaled, y, cv=5)

joblib.dump(best_rf, 'models/saved/ai_classifier.pkl')

evaluation_data = {
    "grid_search": {
        "best_params": grid_search.best_params_,
        "acc_before": float(acc_before),
        "acc_after": float(acc_after),
        "improvement": float(acc_after - acc_before)
    },
    "overfitting": {
        "train_acc": float(train_acc),
        "test_acc": float(acc_after),
        "difference": float(diff),
        "conclusion": overfitting_conclusion
    },
    "cross_validation": {
        "folds": [float(s) for s in cv_scores],
        "average": float(np.mean(cv_scores))
    },
    "metrics": {
        "accuracy": float(acc_after),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "mse": float(mse),
        "rmse": float(rmse),
        "r2": float(r2)
    }
}

with open('assets/advanced_ml_evaluation.json', 'w') as f:
    json.dump(evaluation_data, f, indent=4)

# 7. KNN for Similar Players
knn = NearestNeighbors(n_neighbors=4, metric='cosine') # 4 because the 1st nearest is the player itself
knn.fit(X_scaled)
joblib.dump(knn, 'models/saved/ai_knn.pkl')

# 8. K-Means Clustering
kmeans = KMeans(n_clusters=4, random_state=42)
df['Cluster'] = kmeans.fit_predict(X_scaled)
joblib.dump(kmeans, 'models/saved/ai_kmeans.pkl')

# Analyze clusters to name them
cluster_analysis = df.groupby('Cluster')[['Strike_Rate', 'Batting_Average', 'Matches', 'Runs']].mean()
# Assign names based on simple heuristics
# Highest SR -> Aggressive Power Hitters
# Highest Average -> Anchor Batsmen
# Highest Matches -> Finishers / Veterans
# Remaining -> Emerging Talents
sorted_sr = cluster_analysis.sort_values(by='Strike_Rate', ascending=False).index
sorted_avg = cluster_analysis.sort_values(by='Batting_Average', ascending=False).index

cluster_names = {}
assigned = set()

# Power hitters: highest SR
power_hitter_c = sorted_sr[0]
cluster_names[int(power_hitter_c)] = "Aggressive Power Hitters"
assigned.add(power_hitter_c)

# Anchor: highest Average among the rest
for c in sorted_avg:
    if c not in assigned:
        cluster_names[int(c)] = "Anchor Batsmen"
        assigned.add(c)
        break

# Veteran / Finishers: Highest Matches among the rest
sorted_matches = cluster_analysis.sort_values(by='Matches', ascending=False).index
for c in sorted_matches:
    if c not in assigned:
        cluster_names[int(c)] = "Experienced Finishers"
        assigned.add(c)
        break

# The remaining one
for i in range(4):
    if i not in assigned:
        cluster_names[int(i)] = "Emerging / Rotation Players"
        break

with open('models/saved/cluster_names.json', 'w') as f:
    json.dump(cluster_names, f)

print("Advanced AI Pipeline execution complete. Models saved.")
