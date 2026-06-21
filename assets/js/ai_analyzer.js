document.addEventListener("DOMContentLoaded", async () => {
  // Populate Player Dropdowns
  try {
    const res = await fetch('/api/top-players?limit=500');
    const data = await res.json();
    const players = data.players.map(p => p.name).sort();
    
    const analyzerSelect = document.getElementById('ai-player-select');
    const compP1Select = document.getElementById('comp-p1-select');
    const compP2Select = document.getElementById('comp-p2-select');
    
    let options = '<option value="">-- Select a Player --</option>';
    players.forEach(p => {
      options += `<option value="${p}">${p}</option>`;
    });
    
    if(analyzerSelect) analyzerSelect.innerHTML = options;
    if(compP1Select) compP1Select.innerHTML = options;
    if(compP2Select) compP2Select.innerHTML = options;
  } catch(e) {
    console.error("Error fetching players for dropdowns", e);
  }

  // Handle AI Analyzer Selection
  const analyzerSelect = document.getElementById('ai-player-select');
  if(analyzerSelect) {
    analyzerSelect.addEventListener('change', async (e) => {
      const player = e.target.value;
      if(!player) return;
      
      document.getElementById('ai-loading').style.display = 'block';
      document.getElementById('ai-content').style.display = 'none';
      
      try {
        const res = await fetch(`/api/player-analysis?player=${encodeURIComponent(player)}`);
        const data = await res.json();
        
        if(data.error) {
          alert(data.error);
          return;
        }
        
        // Fetch Image
        const photoEl = document.getElementById('ai-player-photo');
        const loaderEl = document.getElementById('ai-photo-loader');
        if (photoEl && loaderEl) {
          photoEl.style.opacity = '0';
          loaderEl.style.display = 'flex';
          
          fetch(`/api/player-image?name=${encodeURIComponent(player)}`)
            .then(r => r.json())
            .then(imgData => {
              photoEl.onload = () => {
                loaderEl.style.display = 'none';
                photoEl.style.opacity = '1';
              };
              photoEl.src = imgData.url;
            })
            .catch(err => {
              console.error(err);
              loaderEl.style.display = 'none';
              photoEl.style.opacity = '1';
            });
        }
        
        // Populate Profile
        document.getElementById('ai-name').textContent = player;
        document.getElementById('ai-matches').textContent = data.stats.Matches;
        document.getElementById('ai-runs').textContent = data.stats.Runs;
        document.getElementById('ai-avg').textContent = data.stats.Average.toFixed(2);
        document.getElementById('ai-sr').textContent = data.stats.Strike_Rate.toFixed(2);
        document.getElementById('ai-hs').textContent = data.stats.Highest_Score;
        
        // Populate AI Output
        document.getElementById('ai-eff').textContent = data.stats.Efficiency_Score.toFixed(1) + " / 100";
        document.getElementById('ai-pred').textContent = data.prediction;
        document.getElementById('ai-conf').textContent = data.confidence.toFixed(1) + "%";
        document.getElementById('ai-cluster').textContent = data.cluster;
        document.getElementById('ai-future').textContent = data.future_potential;
        document.getElementById('ai-insight').textContent = data.insight;
        
        // Populate Similar Players
        let simHtml = '';
        data.similar_players.forEach(sim => {
          simHtml += `<li><strong>${sim.name}</strong> - ${sim.similarity.toFixed(1)}% Similarity</li>`;
        });
        document.getElementById('ai-similar-list').innerHTML = simHtml;
        
        // Render Feature Importance Chart
        renderFeatureImportanceChart(data.feature_importances);
        
        document.getElementById('ai-loading').style.display = 'none';
        document.getElementById('ai-content').style.display = 'block';
        
      } catch(err) {
        console.error(err);
        alert("Failed to load AI Analysis");
      }
    });
  }

  // Handle Player Comparison
  const compBtn = document.getElementById('comp-btn');
  if(compBtn) {
    compBtn.addEventListener('click', async () => {
      const p1 = document.getElementById('comp-p1-select').value;
      const p2 = document.getElementById('comp-p2-select').value;
      if(!p1 || !p2 || p1 === p2) {
        alert("Please select two different players");
        return;
      }
      
      document.getElementById('comp-loading').style.display = 'block';
      document.getElementById('comp-results-container').style.display = 'none';

      try {
        const res = await fetch(`/api/player-comparison?p1=${encodeURIComponent(p1)}&p2=${encodeURIComponent(p2)}`);
        const data = await res.json();
        
        // Fetch images
        fetch(`/api/player-image?name=${encodeURIComponent(p1)}`)
          .then(r => r.json())
          .then(imgData => document.getElementById('comp-p1-img').src = imgData.url);
        fetch(`/api/player-image?name=${encodeURIComponent(p2)}`)
          .then(r => r.json())
          .then(imgData => document.getElementById('comp-p2-img').src = imgData.url);

        // Section 1
        document.getElementById('comp-p1-name').textContent = data.p1.name;
        document.getElementById('comp-p1-pred').textContent = data.p1.profile.prediction;
        document.getElementById('comp-p1-eff').textContent = data.p1.profile.stats.Efficiency_Score.toFixed(1);

        document.getElementById('comp-p2-name').textContent = data.p2.name;
        document.getElementById('comp-p2-pred').textContent = data.p2.profile.prediction;
        document.getElementById('comp-p2-eff').textContent = data.p2.profile.stats.Efficiency_Score.toFixed(1);

        // Section 2 Winner Logic
        let winner, loser, margin;
        if (data.p1.profile.stats.Efficiency_Score > data.p2.profile.stats.Efficiency_Score) {
          winner = data.p1; loser = data.p2;
        } else {
          winner = data.p2; loser = data.p1;
        }
        margin = winner.profile.stats.Efficiency_Score - loser.profile.stats.Efficiency_Score;
        
        document.getElementById('comp-winner-name').textContent = winner.name;
        document.getElementById('comp-winner-margin').textContent = "+" + margin.toFixed(1) + " Points";
        document.getElementById('comp-winner-conf').textContent = winner.profile.confidence.toFixed(1) + "%";
        document.getElementById('comp-winner-reason').textContent = winner.profile.stats.Strike_Rate > loser.profile.stats.Strike_Rate ? "Higher Strike Rate & Efficiency" : "Better Average & Consistency";

        // Section 4
        document.getElementById('comp-p1-conf').textContent = data.p1.profile.confidence.toFixed(1) + "%";
        document.getElementById('comp-p1-matches').textContent = data.p1.profile.stats.Matches;
        document.getElementById('comp-p2-conf').textContent = data.p2.profile.confidence.toFixed(1) + "%";
        document.getElementById('comp-p2-matches').textContent = data.p2.profile.stats.Matches;

        // Section 5 Feature Importance
        let fHtml = '';
        data.p1.profile.feature_importances.forEach(f => {
          fHtml += `<div style="margin-bottom: 0.5rem; display: flex; justify-content: space-between;"><span style="color:var(--text-muted)">${f.feature.replace('_', ' ')}</span> <span style="font-weight:bold;">${(f.importance*100).toFixed(1)}%</span></div>
          <div style="width: 100%; background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; margin-bottom: 1rem;"><div style="width: ${(f.importance*100)}%; background: linear-gradient(90deg, var(--primary), #e3b432); height: 100%; border-radius: 4px;"></div></div>`;
        });
        document.getElementById('comp-feature-importance-list').innerHTML = fHtml;

        // Section 6 Similar
        let sim1Html = ''; data.p1.profile.similar_players.forEach(s => sim1Html += `<li>• <strong style="color:#fff;">${s.name}</strong> (${s.similarity.toFixed(1)}%)</li>`);
        document.getElementById('comp-p1-similar').innerHTML = sim1Html;
        let sim2Html = ''; data.p2.profile.similar_players.forEach(s => sim2Html += `<li>• <strong style="color:#fff;">${s.name}</strong> (${s.similarity.toFixed(1)}%)</li>`);
        document.getElementById('comp-p2-similar').innerHTML = sim2Html;

        // Section 7 Clusters
        document.getElementById('comp-p1-cluster').textContent = data.p1.profile.cluster;
        document.getElementById('comp-p2-cluster').textContent = data.p2.profile.cluster;

        // Section 8 Insights
        let insHtml = `<li><span style="color:var(--primary);">•</span> ${data.p1.name} has an Efficiency Score of <strong>${data.p1.profile.stats.Efficiency_Score.toFixed(1)}</strong>, compared to ${data.p2.name}'s <strong>${data.p2.profile.stats.Efficiency_Score.toFixed(1)}</strong>.</li>
        <li><span style="color:var(--primary);">•</span> ${winner.name} is classified as a <strong>${winner.profile.prediction}</strong> with ${winner.profile.confidence.toFixed(1)}% confidence.</li>
        <li><span style="color:var(--primary);">•</span> ${data.p1.profile.insight}</li>
        <li><span style="color:var(--primary);">•</span> ${data.p2.profile.insight}</li>`;
        document.getElementById('comp-insights-list').innerHTML = insHtml;

        // Section 9 Future Potential
        document.getElementById('comp-p1-pot-score').textContent = data.p1.profile.potential_score;
        document.getElementById('comp-p1-pot-text').textContent = data.p1.profile.future_potential;
        document.getElementById('comp-p2-pot-score').textContent = data.p2.profile.potential_score;
        document.getElementById('comp-p2-pot-text').textContent = data.p2.profile.future_potential;

        // Section 10 Final Verdict
        document.getElementById('comp-final-report-text').innerHTML = `
          After running advanced Machine Learning classification, K-Means clustering, and KNN similarity models on historical IPL data, the AI has concluded that <strong style="color:#e3b432; font-size: 1.5rem;">${winner.name}</strong> is the superior choice for your franchise. <br><br>
          With a predicted class of <strong>${winner.profile.prediction}</strong> (Confidence: ${winner.profile.confidence.toFixed(1)}%) and a future potential rating of <strong>${winner.profile.potential_score}/100</strong>, ${winner.name} provides a statistical edge of <span style="color:var(--accent-green);">+${margin.toFixed(1)} Efficiency Points</span> over ${loser.name}.<br><br>
          <strong>Recommendation:</strong> Draft ${winner.name} to maximize batting efficiency and overall team stability based on the highly influential ${data.p1.profile.feature_importances[0].feature.replace('_', ' ')} metric.
        `;
        
        renderRadarChart(data);

        document.getElementById('comp-loading').style.display = 'none';
        document.getElementById('comp-results-container').style.display = 'flex';
        
      } catch(err) {
        console.error(err);
        document.getElementById('comp-loading').style.display = 'none';
        alert("Failed to load comparison");
      }
    });
  }

  // Load ML Evaluation
  loadMLEvaluation();
});

let featureChartInst = null;
function renderFeatureImportanceChart(importances) {
  const ctx = document.getElementById('ai-feature-chart');
  if(!ctx) return;
  
  if(featureChartInst) featureChartInst.destroy();
  
  const labels = importances.map(f => f.feature);
  const data = importances.map(f => f.importance);
  
  featureChartInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Feature Importance',
        data: data,
        backgroundColor: '#e3b432'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' } },
        x: { grid: { display: false } }
      }
    }
  });
}

let radarChartInst = null;
function renderRadarChart(data) {
  const ctx = document.getElementById('comp-radar-chart');
  if(!ctx) return;
  
  if(radarChartInst) radarChartInst.destroy();
  
  const features = Object.keys(data.p1.normalized);
  const d1 = Object.values(data.p1.normalized);
  const d2 = Object.values(data.p2.normalized);
  
  radarChartInst = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: features,
      datasets: [
        {
          label: data.p1.name,
          data: d1,
          backgroundColor: 'rgba(54, 162, 235, 0.4)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 3,
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
          pointHoverRadius: 8
        },
        {
          label: data.p2.name,
          data: d2,
          backgroundColor: 'rgba(255, 99, 132, 0.4)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 3,
          pointBackgroundColor: 'rgba(255, 99, 132, 1)',
          pointHoverRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: 'rgba(255,255,255,0.3)', lineWidth: 1 },
          grid: { color: 'rgba(255,255,255,0.2)', lineWidth: 1 },
          pointLabels: { color: '#fff', font: { size: 16, weight: 'bold' } },
          ticks: { display: false, max: 100, min: 0 }
        }
      },
      plugins: {
        legend: { labels: { color: '#fff', font: { size: 18 } } },
        tooltip: {
          bodyFont: { size: 14 },
          titleFont: { size: 16 }
        }
      }
    }
  });
}

async function loadMLEvaluation() {
  const el = document.getElementById('eval-cv');
  if(!el) return;
  
  try {
    const res = await fetch('/api/ml-evaluation');
    const data = await res.json();
    
    // Cross Validation
    let cvHtml = '';
    data.cross_validation.folds.forEach((fold, i) => {
      cvHtml += `<li>Fold ${i+1}: ${(fold*100).toFixed(2)}%</li>`;
    });
    cvHtml += `<li><strong>Average: ${(data.cross_validation.average*100).toFixed(2)}%</strong></li>`;
    document.getElementById('eval-cv').innerHTML = cvHtml;
    
    // Hyperparameter Tuning
    document.getElementById('eval-tune-before').textContent = (data.grid_search.acc_before*100).toFixed(2) + '%';
    document.getElementById('eval-tune-after').textContent = (data.grid_search.acc_after*100).toFixed(2) + '%';
    document.getElementById('eval-tune-imp').textContent = '+' + (data.grid_search.improvement*100).toFixed(2) + '%';
    document.getElementById('eval-tune-params').textContent = JSON.stringify(data.grid_search.best_params, null, 2);
    
    // Overfitting Analysis
    document.getElementById('eval-over-train').textContent = (data.overfitting.train_acc*100).toFixed(2) + '%';
    document.getElementById('eval-over-test').textContent = (data.overfitting.test_acc*100).toFixed(2) + '%';
    document.getElementById('eval-over-diff').textContent = (data.overfitting.difference*100).toFixed(2) + '%';
    document.getElementById('eval-over-conc').textContent = data.overfitting.conclusion;
    
  } catch(err) {
    console.error("Failed to load ML Evaluation", err);
  }
}
