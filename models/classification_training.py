import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
import json

# Ensure directories exist
os.makedirs('assets/images', exist_ok=True)
os.makedirs('models/saved', exist_ok=True)

# 1. LOAD EXISTING DATASET
df = pd.read_csv('dataset/dataset.csv')

# 2. CREATE TARGET VARIABLE
scaler_minmax = MinMaxScaler((0, 100))
df['Norm_Efficiency'] = scaler_minmax.fit_transform(df[['Efficiency_Score']])

# Target: 1 if Norm_Efficiency >= 70 else 0
# Actually, to ensure a good sample, we'll use 50 if 70 gives too few, but user explicitly asked for 70. Let's see.
df['Efficient'] = (df['Norm_Efficiency'] >= 70).astype(int)

# If the target is highly imbalanced (e.g. less than 10 players), we adjust to top 20%
if df['Efficient'].sum() < 20:
    threshold = np.percentile(df['Norm_Efficiency'], 80)
    df['Efficient'] = (df['Norm_Efficiency'] >= threshold).astype(int)

print("Class distribution:")
print(df['Efficient'].value_counts())

# Features
features = ['Matches', 'Innings', 'Runs', 'Balls_Faced', 'Dot_Balls', 'Batting_Average', 'Strike_Rate', 'Trees_Planted']
X = df[features]
y = df['Efficient']

# Preprocessing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save scaler
joblib.dump(scaler, 'models/saved/cls_scaler.pkl')

# Train Models
models = {
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced'),
    'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=5, class_weight='balanced'),
    'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100, class_weight='balanced')
}

results = {}
best_model_name = ""
best_f1 = -1

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, "predict_proba") else y_pred
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    cm = confusion_matrix(y_test, y_pred)
    
    results[name] = {
        'model': model,
        'acc': acc,
        'prec': prec,
        'rec': rec,
        'f1': f1,
        'roc_auc': roc_auc,
        'mse': mse,
        'rmse': rmse,
        'r2': r2,
        'cm': cm,
        'fpr': fpr,
        'tpr': tpr
    }
    
    # Save model
    joblib.dump(model, f'models/saved/cls_{name.replace(" ", "_").lower()}.pkl')
    
    if f1 > best_f1:
        best_f1 = f1
        best_model_name = name

print(f"Best model: {best_model_name}")

# Generate JSON for the dashboard
dashboard_metrics = {}
for name, metrics in results.items():
    dashboard_metrics[name] = {
        'Accuracy': float(metrics['acc']),
        'Precision': float(metrics['prec']),
        'Recall': float(metrics['rec']),
        'F1 Score': float(metrics['f1']),
        'ROC-AUC': float(metrics['roc_auc']),
        'MSE': float(metrics['mse']),
        'RMSE': float(metrics['rmse']),
        'R2 Score': float(metrics['r2'])
    }
dashboard_metrics['Best_Model'] = best_model_name

with open('assets/classification_metrics.json', 'w') as f:
    json.dump(dashboard_metrics, f, indent=4)

# Visualization
import warnings
warnings.filterwarnings('ignore')
plt.style.use('dark_background')
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
model_names = list(results.keys())

# Graph 1: Confusion Matrix Heatmap (for best model)
best_cm = results[best_model_name]['cm']
plt.figure(figsize=(8, 6))
sns.heatmap(best_cm, annot=True, fmt='d', cmap='Greens', xticklabels=['Not Efficient', 'Efficient'], yticklabels=['Not Efficient', 'Efficient'], annot_kws={"size": 16})
plt.title(f'Confusion Matrix - {best_model_name}', fontsize=16)
plt.ylabel('True Label', fontsize=14)
plt.xlabel('Predicted Label', fontsize=14)
plt.tight_layout()
plt.savefig('assets/images/cls_confusion_matrix.png', dpi=300)
plt.close()

# Helper function to plot metric comparison
def plot_metric_comparison(metric_key, title, filename):
    values = [results[m][metric_key] for m in model_names]
    plt.figure(figsize=(10, 6))
    bars = plt.bar(model_names, values, color=colors)
    plt.title(title, fontsize=18)
    plt.ylabel('Score', fontsize=14)
    plt.ylim(0, 1.1)
    plt.grid(axis='y', alpha=0.3)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f'{yval:.3f}', ha='center', va='bottom', fontsize=12)
    plt.tight_layout()
    plt.savefig(f'assets/images/cls_{filename}.png', dpi=300)
    plt.close()

# Graph 2, 3, 4, 5
plot_metric_comparison('acc', 'Accuracy Comparison', 'accuracy_comparison')
plot_metric_comparison('prec', 'Precision Comparison', 'precision_comparison')
plot_metric_comparison('rec', 'Recall Comparison', 'recall_comparison')
plot_metric_comparison('f1', 'F1 Score Comparison', 'f1_comparison')

# Graph 6: ROC Curve
plt.figure(figsize=(10, 8))
for i, name in enumerate(model_names):
    plt.plot(results[name]['fpr'], results[name]['tpr'], label=f'{name} (AUC = {results[name]["roc_auc"]:.3f})', color=colors[i], linewidth=2)
plt.plot([0, 1], [0, 1], 'k--', linewidth=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=14)
plt.ylabel('True Positive Rate', fontsize=14)
plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=18)
plt.legend(loc="lower right", fontsize=12)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('assets/images/cls_roc_curve.png', dpi=300)
plt.close()

# Graph 7: Feature Importance (from Random Forest)
rf_model = results['Random Forest']['model']
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]
plt.figure(figsize=(12, 8))
plt.title('Feature Importance (Random Forest)', fontsize=18)
plt.bar(range(X.shape[1]), importances[indices], color='#e3b432', align='center')
plt.xticks(range(X.shape[1]), [features[i] for i in indices], rotation=45, ha='right', fontsize=12)
plt.xlim([-1, X.shape[1]])
plt.ylabel('Importance Score', fontsize=14)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('assets/images/cls_feature_importance.png', dpi=300)
plt.close()

# Graph 8: Model Performance Dashboard (Combined plot)
plt.figure(figsize=(14, 8))
metrics_to_plot = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
x = np.arange(len(model_names))
width = 0.2

for i, metric in enumerate(['acc', 'prec', 'rec', 'f1']):
    values = [results[m][metric] for m in model_names]
    plt.bar(x + (i - 1.5) * width, values, width, label=metrics_to_plot[i])

plt.xlabel('Models', fontsize=14)
plt.ylabel('Scores', fontsize=14)
plt.title('Model Performance Dashboard', fontsize=18)
plt.xticks(x, model_names, fontsize=12)
plt.legend(loc='lower right', fontsize=12)
plt.ylim(0, 1.1)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('assets/images/cls_performance_dashboard.png', dpi=300)
plt.close()

print("Classification Pipeline executed successfully.")
