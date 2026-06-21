import os
import sys
import subprocess
import json
import pandas as pd
import numpy as np
import joblib
import requests
from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context

app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# Disable caching for local development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

# API: Serve the Justification Report (Markdown)
@app.route('/api/justification')
def get_justification():
    report_path = "JUSTIFICATION_REPORT.md"
    if not os.path.exists(report_path):
        return jsonify({"status": "error", "message": "Report not found"}), 404
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content, 200, {"Content-Type": "text/plain; charset=utf-8"}

# Helper to read code files
@app.route('/api/code')
def get_code():
    file_path = request.args.get('file')
    if not file_path:
        return "Error: Missing file parameter", 400
        
    # Security check to prevent directory traversal
    allowed_files = [
        "preprocessing/aggregate_data.py",
        "preprocessing/data_cleaning.py",
        "sampling/sampling_methods.py",
        "models/model_training.py",
        "analysis/evaluation.py",
        "visualizations/charts.py"
    ]
    if file_path not in allowed_files:
        return "Error: Access denied", 403
        
    abs_path = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(abs_path):
        return f"Error: File '{file_path}' not found", 404
        
    with open(abs_path, 'r') as f:
        content = f.read()
    return Response(content, mimetype='text/plain')

# Serve index.html
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# API: Data cleaning statistics
@app.route('/api/cleaning-stats')
def cleaning_stats():
    try:
        raw_path = "dataset/raw_dataset.csv"
        clean_path = "dataset/dataset.csv"
        
        if not os.path.exists(raw_path) or not os.path.exists(clean_path):
            return jsonify({"status": "error", "message": "Pipeline has not been run yet. Please run the pipeline."})
            
        raw_df = pd.read_csv(raw_path)
        clean_df = pd.read_csv(clean_path)
        
        # Calculate dynamic stats
        before = len(raw_df)
        after = len(clean_df)
        outliers = before - after # inactive bowler profiles filtered out
        duplicates = 0
        imputed = 0
        
        return jsonify({
            "status": "success",
            "before": before,
            "after": after,
            "duplicates": duplicates,
            "outliers": outliers,
            "imputed": imputed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# API: Evaluation Metrics & Verdict
@app.route('/api/metrics')
def evaluation_metrics():
    try:
        results_path = "analysis/results.json"
        if not os.path.exists(results_path):
            return jsonify({"status": "error", "message": "Metrics not found. Run pipeline."})
            
        with open(results_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# API: SDG Sustainability Data
@app.route('/api/sdg-data')
def sdg_data():
    try:
        clean_path = "dataset/dataset.csv"
        if not os.path.exists(clean_path):
            return jsonify({"status": "error", "message": "Clean dataset not found."})
            
        df = pd.read_csv(clean_path)
        
        # Calculate dynamic stats
        total_trees = int(df["Trees_Planted"].sum())
        avg_trees = float(df["Trees_Planted"].mean())
        
        # Top individual batsman
        batsman_grouped = df.groupby("Player_Name")["Trees_Planted"].sum().reset_index()
        top_batsman_row = batsman_grouped.sort_values(by="Trees_Planted", ascending=False).iloc[0]
        top_batsman = {
            "name": top_batsman_row["Player_Name"],
            "trees": int(top_batsman_row["Trees_Planted"])
        }
        
        # Top 10 batsmen list
        top_10 = batsman_grouped.sort_values(by="Trees_Planted", ascending=False).head(10)
        top_10_list = [{"name": r["Player_Name"], "trees": int(r["Trees_Planted"])} for _, r in top_10.iterrows()]
        
        # Team rankings
        team_grouped = df.groupby("Team").agg({
            "Dot_Balls": "sum",
            "Trees_Planted": "sum"
        }).reset_index()
        team_rankings = team_grouped.sort_values(by="Trees_Planted", ascending=False).to_dict(orient="records")
        for rank in team_rankings:
            rank["Dot_Balls"] = int(rank["Dot_Balls"])
            rank["Trees_Planted"] = int(rank["Trees_Planted"])
            
        # Sampling Means Comparison
        sampling_means = {}
        samples = {
            "population": "dataset/dataset.csv",
            "sample_random": "dataset/sample_random_train.csv",
            "sample_systematic": "dataset/sample_systematic_train.csv",
            "sample_stratified": "dataset/sample_stratified_train.csv",
            "sample_cluster": "dataset/sample_cluster_train.csv"
        }
        
        for name, path in samples.items():
            if os.path.exists(path):
                sub_df = pd.read_csv(path)
                sampling_means[name] = {
                    "trees": float(sub_df["Trees_Planted"].mean()),
                    "efficiency": float(sub_df["Efficiency_Score"].mean())
                }
            else:
                sampling_means[name] = {"trees": 0.0, "efficiency": 0.0}
                
        return jsonify({
            "status": "success",
            "total_trees": total_trees,
            "avg_trees_per_player": avg_trees,
            "top_batsman": top_batsman,
            "top_batsmen_list": top_10_list,
            "team_rankings": team_rankings,
            "sampling_means": sampling_means
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# API: Top Players Leaderboard
@app.route('/api/top-players')
def top_players():
    try:
        clean_path = "dataset/dataset.csv"
        if not os.path.exists(clean_path):
            return jsonify({"status": "error", "message": "Clean dataset not found."})

        df = pd.read_csv(clean_path)

        # Sort by Efficiency Score descending, take top N
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '').lower()
        team_filter = request.args.get('team', '')

        if search:
            df = df[df['Player_Name'].str.lower().str.contains(search, na=False)]
        if team_filter:
            df = df[df['Team'] == team_filter]

        top_df = df.sort_values('Efficiency_Score', ascending=False).head(limit)

        players = []
        for _, row in top_df.iterrows():
            players.append({
                "name": row['Player_Name'],
                "team": row['Team'],
                "matches": int(row['Matches']),
                "innings": int(row['Innings']),
                "runs": int(row['Runs']),
                "balls_faced": int(row['Balls_Faced']),
                "dot_balls": int(row['Dot_Balls']),
                "strike_rate": round(float(row['Strike_Rate']), 2),
                "batting_average": round(float(row['Batting_Average']), 2),
                "trees_planted": int(row['Trees_Planted']),
                "efficiency_score": round(float(row['Efficiency_Score']), 4)
            })

        # Get unique teams for filter dropdown
        all_teams = sorted(df['Team'].dropna().unique().tolist())

        return jsonify({
            "status": "success",
            "players": players,
            "total_population": len(pd.read_csv(clean_path)),
            "teams": all_teams
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def get_player_ai_profile(player_name, df, scaler, classifier, knn, cluster_names):
    player_data = df[df['Player_Name'] == player_name].iloc[0]
    
    features = ['Matches', 'Innings', 'Runs', 'Balls_Faced', 'Dot_Balls', 'Batting_Average', 'Strike_Rate']
    player_features = player_data[features].values.reshape(1, -1)
    player_scaled = scaler.transform(player_features)
    
    pred_class = classifier.predict(player_scaled)[0]
    pred_probs = classifier.predict_proba(player_scaled)[0]
    confidence = float(pred_probs[pred_class]) * 100
    
    categories = {0: "Needs Improvement", 1: "Average Performer", 2: "High Performer", 3: "Elite Performer"}
    prediction_text = categories[pred_class]
    
    if player_data['Matches'] < 40 and pred_class >= 2:
        future_potential = "Future Superstar"
    elif pred_class == 3:
        future_potential = "Legend in Prime"
    elif pred_class == 2:
        future_potential = "High Potential"
    elif pred_class == 1:
        future_potential = "Promising Talent"
    else:
        future_potential = "Needs Development"
        
    pot_scores = {"Future Superstar": 95, "Legend in Prime": 90, "High Potential": 85, "Promising Talent": 75, "Needs Development": 60}
    potential_score = pot_scores.get(future_potential, 70)
    
    importances = classifier.feature_importances_
    feature_imp = []
    for i, f in enumerate(features):
        feature_imp.append({"feature": f, "importance": float(importances[i])})
    feature_imp.sort(key=lambda x: x['importance'], reverse=True)
    
    distances, indices = knn.kneighbors(player_scaled)
    
    similar_players = []
    for i in range(1, min(4, len(indices[0]))):
        idx = indices[0][i]
        sim_score = max(0, 100 - (distances[0][i] * 50))
        similar_players.append({
            "name": df.iloc[idx]['Player_Name'],
            "similarity": float(sim_score)
        })
        
    cluster_id = int(player_data.get('Cluster', -1))
    cluster_name = cluster_names.get(str(cluster_id), "Unknown Cluster")
    
    if player_data['Strike_Rate'] > 145 and player_data['Batting_Average'] > 35:
        insight = f"{player_name} is an elite aggressive batter, combining high strike rate with incredible consistency."
    elif player_data['Strike_Rate'] > 150:
        insight = f"{player_name} is a high-impact player capable of changing the game quickly."
    elif player_data['Batting_Average'] > 40:
        insight = f"{player_name} is a reliable anchor who consistently builds innings."
    else:
        insight = f"Strike Rate and Average are the most influential metrics determining {player_name}'s efficiency."
    
    stats = {
        "Matches": int(player_data['Matches']),
        "Innings": int(player_data['Innings']),
        "Runs": int(player_data['Runs']),
        "Average": float(player_data['Batting_Average']),
        "Strike_Rate": float(player_data['Strike_Rate']),
        "Highest_Score": int(player_data['Highest_Score']) if 'Highest_Score' in df.columns else int(player_data['Runs']) if player_data['Innings'] <= 1 else 0,
        "Fours": int(player_data['Fours']) if 'Fours' in df.columns else 0,
        "Sixes": int(player_data['Sixes']) if 'Sixes' in df.columns else 0,
        "Dot_Balls": int(player_data['Dot_Balls']),
        "Balls_Faced": int(player_data['Balls_Faced']),
        "Efficiency_Score": float(player_data['Efficiency_Score'])
    }
    
    return {
        "stats": stats,
        "prediction": prediction_text,
        "confidence": confidence,
        "future_potential": future_potential,
        "potential_score": potential_score,
        "feature_importances": feature_imp,
        "similar_players": similar_players,
        "cluster": cluster_name,
        "insight": insight
    }

# API: Advanced AI Player Analysis
@app.route('/api/player-analysis')
def player_analysis():
    player_name = request.args.get('player')
    if not player_name:
        return jsonify({"error": "No player specified"}), 400
        
    df = pd.read_csv('dataset/dataset.csv')
    if player_name not in df['Player_Name'].values:
        return jsonify({"error": "Player not found"}), 404
        
    scaler = joblib.load('models/saved/ai_scaler.pkl')
    classifier = joblib.load('models/saved/ai_classifier.pkl')
    knn = joblib.load('models/saved/ai_knn.pkl')
    try:
        with open('models/saved/cluster_names.json', 'r') as f:
            cluster_names = json.load(f)
    except:
        cluster_names = {}
        
    profile = get_player_ai_profile(player_name, df, scaler, classifier, knn, cluster_names)
    return jsonify(profile)

@app.route('/api/ml-evaluation')
def ml_evaluation():
    try:
        with open('assets/advanced_ml_evaluation.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

IMAGE_CACHE_FILE = 'assets/image_cache.json'

@app.route('/api/player-image')
def player_image():
    player_name = request.args.get('name')
    if not player_name:
        return jsonify({"url": "https://ui-avatars.com/api/?name=Player&background=0D8ABC&color=fff&size=400"})
        
    try:
        cache = {}
        if os.path.exists(IMAGE_CACHE_FILE):
            with open(IMAGE_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                
        if player_name in cache:
            return jsonify({"url": cache[player_name]})
            
        search_query = f"{player_name} cricketer"
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={search_query}&utf8=&format=json"
        res = requests.get(search_url, timeout=5).json()
        
        fallback = f"https://ui-avatars.com/api/?name={player_name}&background=1a1a2e&color=fff&size=400&font-size=0.33"
        
        if res['query']['search']:
            page_title = res['query']['search'][0]['title']
            img_url_api = f"https://en.wikipedia.org/w/api.php?action=query&titles={page_title}&prop=pageimages&format=json&pithumbsize=400"
            img_res = requests.get(img_url_api, timeout=5).json()
            
            pages = img_res['query']['pages']
            page_id = list(pages.keys())[0]
            if 'thumbnail' in pages[page_id]:
                img_url = pages[page_id]['thumbnail']['source']
                cache[player_name] = img_url
                with open(IMAGE_CACHE_FILE, 'w') as f:
                    json.dump(cache, f)
                return jsonify({"url": img_url})
                
        cache[player_name] = fallback
        with open(IMAGE_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        return jsonify({"url": fallback})
        
    except Exception as e:
        print("Image fetch error:", e)
        fallback = f"https://ui-avatars.com/api/?name={player_name}&background=1a1a2e&color=fff&size=400"
        return jsonify({"url": fallback})

@app.route('/api/player-comparison')
def player_comparison():
    p1 = request.args.get('p1')
    p2 = request.args.get('p2')
    if not p1 or not p2:
        return jsonify({"error": "Missing player names"}), 400
        
    df = pd.read_csv('dataset/dataset.csv')
    if p1 not in df['Player_Name'].values or p2 not in df['Player_Name'].values:
        return jsonify({"error": "Player(s) not found"}), 404
        
    scaler = joblib.load('models/saved/ai_scaler.pkl')
    classifier = joblib.load('models/saved/ai_classifier.pkl')
    knn = joblib.load('models/saved/ai_knn.pkl')
    try:
        with open('models/saved/cluster_names.json', 'r') as f:
            cluster_names = json.load(f)
    except:
        cluster_names = {}
        
    prof1 = get_player_ai_profile(p1, df, scaler, classifier, knn, cluster_names)
    prof2 = get_player_ai_profile(p2, df, scaler, classifier, knn, cluster_names)
    
    # Normalize features for radar chart (0-100)
    features = ['Runs', 'Batting_Average', 'Strike_Rate', 'Efficiency_Score', 'Matches']
    max_vals = df[features].max()
    min_vals = df[features].min()
    
    def normalize(val, col):
        if max_vals[col] == min_vals[col]: return 0
        return float(((val - min_vals[col]) / (max_vals[col] - min_vals[col])) * 100)
        
    def get_stat(prof, f):
        return prof["stats"]["Average"] if f == 'Batting_Average' else prof["stats"][f]
        
    comp1 = {f: normalize(get_stat(prof1, f), f) for f in features}
    comp2 = {f: normalize(get_stat(prof2, f), f) for f in features}
    
    return jsonify({
        "p1": {
            "name": p1,
            "profile": prof1,
            "normalized": comp1
        },
        "p2": {
            "name": p2,
            "profile": prof2,
            "normalized": comp2
        }
    })

# API: Dynamic Execution Pipeline
@app.route('/api/run-pipeline', methods=['POST'])
def run_pipeline():
    def generate():
        scripts = [
            ("preprocessing/aggregate_data.py", "Data Aggregation (parsing cricsheet matches)"),
            ("preprocessing/data_cleaning.py", "Data Cleansing and Feature Normalization"),
            ("sampling/sampling_methods.py", "Sampling Extraction (SRS, Sys, Strat, Cluster)"),
            ("models/model_training.py", "ML Regressor Training (LR, RF, XGBoost on all sets)"),
            ("analysis/evaluation.py", "Evaluations and Performance Logging"),
            ("visualizations/charts.py", "Generating Static Matplotlib Visualizations")
        ]
        
        for script_path, desc in scripts:
            yield f"\n> [STARTING] {desc} ({script_path})...\n"
            
            # Execute script and read output line by line
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Read stdout line-by-line in real time
            for line in iter(process.stdout.readline, ''):
                yield line
                
            process.stdout.close()
            return_code = process.wait()
            
            if return_code != 0:
                yield f"[ERROR] Script {script_path} failed with exit code {return_code}\n"
                return
            yield f"> [COMPLETED] {desc} finished successfully.\n"
            
        yield "\n> [PIPELINE SUCCESS] All stages completed successfully. Repopulating HUD metrics...\n"
        
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    # Ensure assets subdirectories exist
    os.makedirs('assets/css', exist_ok=True)
    os.makedirs('assets/js', exist_ok=True)
    os.makedirs('assets/images', exist_ok=True)
    
    print("Serving dashboard on http://127.0.0.1:5001")
    app.run(host='127.0.0.1', port=5001, debug=True)
