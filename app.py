import os
import sys
import subprocess
import json
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory, Response, stream_with_context

app = Flask(__name__, static_folder='assets', static_url_path='/assets')

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
