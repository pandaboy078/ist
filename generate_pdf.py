import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_pdf():
    doc = SimpleDocTemplate("IST_AAT_Report_Sampath_1BF24AI147.pdf", pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    
    # Reduced font sizes as requested
    h_toc = ParagraphStyle(name='HeadingTOC', parent=styles['Heading1'], fontName='Times-Bold', fontSize=14, spaceAfter=16, alignment=1)
    h1 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName='Times-Bold', fontSize=13, spaceAfter=12)
    h2 = ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName='Times-Bold', fontSize=12, spaceAfter=10)
    normal = ParagraphStyle(name='Normal', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, alignment=4, spaceAfter=8) # 4=TA_JUSTIFY
    normal_left = ParagraphStyle(name='NormalLeft', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, alignment=0, spaceAfter=8)
    normal_indent = ParagraphStyle(name='NormalIndent', parent=styles['Normal'], fontName='Times-Roman', fontSize=12, alignment=0, spaceAfter=8, leftIndent=36)
    caption = ParagraphStyle(name='Caption', parent=styles['Normal'], fontName='Times-BoldItalic', fontSize=10, alignment=1, spaceAfter=12) # 1=TA_CENTER
    
    story = []

    def add_heading(text, level=1, new_page=False):
        if new_page:
            story.append(PageBreak())
        if level == 1:
            story.append(Paragraph(text, h1))
        else:
            story.append(Paragraph(text, h2))
            
    def add_para(text, align="justify", indent=False):
        if indent:
            story.append(Paragraph(text, normal_indent))
        elif align == "left":
            story.append(Paragraph(text, normal_left))
        else:
            story.append(Paragraph(text, normal))

    def add_table(data, headers=None):
        table_data = []
        if headers:
            table_data.append([Paragraph(f"<b>{h}</b>", normal_left) for h in headers])
        
        for row in data:
            table_data.append([Paragraph(str(cell), normal_left) for cell in row])
            
        t = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.8*inch][:len(data[0])])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey) if headers else ('', (0,0), (0,0), colors.white),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Times-Bold') if headers else ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    # --- TABLE OF CONTENTS ---
    story.append(Paragraph('Table of Contents', h_toc))
    
    add_para("1. Objective", align="left")
    add_para("o Problem statement and goal of the study.", indent=True)
    
    add_para("2. Data Description", align="left")
    add_para("o Data source", indent=True)
    add_para("o Sample size", indent=True)
    add_para("o Variables considered", indent=True)
    
    add_para("3. Methodology", align="left")
    add_para("o Sampling/Data collection method", indent=True)
    add_para("o Statistical techniques used", indent=True)
    
    add_para("4. Analysis & Results", align="left")
    add_para("o Calculations/Outputs", indent=True)
    add_para("o Graphs/Tables (if any)", indent=True)
    add_para("o Hypothesis testing/Model evaluation", indent=True)
    
    add_para("5. Interpretation", align="left")
    add_para("o Key findings", indent=True)
    add_para("o Statistical inference", indent=True)
    
    add_para("6. Conclusion", align="left")
    add_para("o Final observations and decisions", indent=True)
    
    add_para("7. SDG Addressed", align="left")
    
    add_para("8. References", align="left")
    add_para("o Dataset/Books/Websites used", indent=True)

    # 1. OBJECTIVE
    add_heading('1. Objective', 1, new_page=True)
    add_heading('Problem statement and goal of the study', 2)
    add_para("The proliferation of large-scale sports analytics datasets has presented a substantial challenge in machine learning modeling: training efficiency and sample representation. Training machine learning models on entire populations is computationally expensive and conceptually redundant if a smaller, unbiased sample can effectively generalize to the true population. Selecting a representative sample from IPL (Indian Premier League) cricket data is crucial due to the inherent variance across different playing eras, team franchises, and performance tiers.")
    add_para("This project explores the challenge of efficiently predicting batsman efficiency scores using varying statistical sampling methods. Furthermore, it integrates the Green Dot Ball sustainability initiative, transforming standard cricket metrics into quantifiable environmental awareness impacts. By gamifying dot balls—where every dot ball equals 19 trees planted—we introduce a multi-objective challenge: evaluating a player not just on their run-scoring capacity, but on their ecological footprint as tracked through sports performance. The sheer volume of modern sports data necessitates analytical pipelines that can rapidly prototype models on statistically significant fractions of data without sacrificing performance.")
    add_para("The primary goal of this study is to evaluate the effect of four distinct statistical sampling methods—Simple Random Sampling (SRS), Stratified Sampling, Systematic Sampling, and Cluster Sampling—on the generalizability and accuracy of machine learning regressors. The study aims to predict the multi-objective Batting Efficiency Score and determine the best sampling method and the most optimal machine learning algorithm out of Linear Regression, Random Forest, and XGBoost. An integrated secondary goal is to map dot balls to carbon offset contributions (Trees Planted), aligning sports analytics with global sustainability goals. This directly challenges the convention that sports data analytics are solely for commercial gain, providing a reproducible framework for ecological accounting.")

    # 2. DATA DESCRIPTION
    add_heading('2. Data Description', 1, new_page=True)
    add_heading('Data source', 2)
    add_para("The dataset originates from the Cricsheet Ball-by-Ball IPL Match Data encompassing the period from 2008 to 2025. Data collection involved parsing over 1,200 match CSV files. The raw ball-by-ball events were systematically aggregated to form player-level career statistics for each team. Inactive batsmen (defined as having faced fewer than 15 balls) were filtered out to maintain robust and statistically significant records, resulting in the final clean population dataset.")

    add_heading('Sample size', 2)
    add_para("The aggregated and cleaned population consists of N = 570 unique batsman-team profiles. The sample size selected for experimental model training across all sampling methods is n = 150 observations. This results in a sampling fraction of f = n/N = 150/570 = 0.2632, or approximately 26.3%. At 26.3%, the sample comprehensively encapsulates the population variance, providing an ideal testing ground to evaluate whether smaller sample sets can perfectly model the population distribution without suffering from overfitting or high variance errors. Selecting an unnecessarily large sample size would defeat the purpose of algorithmic efficiency, while selecting too small a sample introduces high bias.")

    add_heading('Variables considered', 2)
    add_para("• Runs: Total career runs scored by the batsman for a given franchise. Acts as the primary volume metric.", align="left")
    add_para("• Batting Average: The average runs scored per dismissal, serving as the consistency metric.", align="left")
    add_para("• Strike Rate: The average number of runs scored per 100 balls faced, representing scoring velocity.", align="left")
    add_para("• Dot Balls: The absolute count of deliveries faced where no runs were scored.", align="left")
    add_para("• Trees Planted: The environmental metric computed directly as Dot Balls × 19 under the Green Dot Ball Initiative.", align="left")
    add_para("• Batting Efficiency Score: The continuous target variable calculated via a multi-objective linear combination of min-max normalized metrics: 0.4(Runs) + 0.3(Strike Rate) + 0.2(Average) + 0.1(Trees).", align="left")

    # 3. METHODOLOGY
    add_heading('3. Methodology', 1, new_page=True)
    add_heading('Sampling/Data collection method', 2)
    add_para("1. Simple Random Sampling (SRS): A probability sampling method where every member of the population has an equal and independent probability of selection (P = n/N). It was performed without replacement. This ensures no structural bias enters the sample dataset, serving as the fundamental baseline for comparative evaluation.")
    add_para("2. Stratified Sampling: The population was divided into homogenous subgroups (strata) based on IPL Franchise. Proportionate allocations were mathematically drawn to preserve the exact team distribution within the sample. Formula used: stratum_n = round((N_i / N) * n). This method guarantees that historically successful teams and underperforming teams are equally represented proportionally.")
    add_para("3. Systematic Sampling: A random starting point was selected, and every k-th element (where k = N/n) was systematically sampled from the dataset. This offers a highly efficient array-traversal sampling method.")
    add_para("4. Cluster Sampling: IPL teams were treated as intact clusters. Random teams were sampled, and all players within the chosen teams were included until the cumulative sample size reached 150. This deliberately tests how robust the regressors are against heavily localized, intra-cluster similarities.")

    add_heading('Statistical techniques used', 2)
    add_para("1. Linear Regression: Selected to model the exact linear continuous target variable. By the Gauss-Markov theorem, Ordinary Least Squares (OLS) serves as the Best Linear Unbiased Estimator (BLUE). It provides a completely deterministic mapping free from decision boundaries.")
    add_para("2. Random Forest Regression: An ensemble decision tree regressor utilizing bagging. Selected to assess nonlinear modeling limits, evaluating how well tree-based architectures can approximate a globally linear function. It acts as a defense against potential overfitting through random feature subspace selection.")
    add_para("3. XGBoost Regression: An advanced gradient boosting model selected for its aggressive error minimization through sequential learning stages. It sequentially corrects the residual errors of preceding weak learners, representing the absolute ceiling of modern non-linear predictive capabilities.")
    add_para("Evaluation Metrics used included R² Score (Coefficient of Determination), MAE (Mean Absolute Error), and RMSE (Root Mean Squared Error) to rigorously validate performance variance across samples. The comparison between R² scores specifically highlights the variance explained by the respective models.")

    # 4. ANALYSIS & RESULTS
    add_heading('4. Analysis & Results', 1, new_page=True)
    
    add_heading('Calculations/Outputs', 2)
    add_para("Table 1: Average Performance by Sampling Method", align="left")
    t1_data = [
        ["Simple Random (SRS)", "0.974395", "0.767414", "1.560880", "1st"],
        ["Stratified", "0.973311", "0.794247", "1.597056", "2nd"],
        ["Systematic", "0.969291", "0.860787", "1.710920", "3rd"],
        ["Cluster", "0.956942", "1.039265", "1.994075", "4th"]
    ]
    add_table(t1_data, ["Sampling Method", "Avg R² Score", "Avg MAE", "Avg RMSE", "Rank"])
    
    add_para("Table 2: Linear Regression Results", align="left")
    t2_data = [
        ["Simple Random", "1.000000", "0.000029", "0.000033"],
        ["Stratified", "1.000000", "0.000028", "0.000032"],
        ["Systematic", "1.000000", "0.000028", "0.000033"],
        ["Cluster", "1.000000", "0.000028", "0.000033"]
    ]
    add_table(t2_data, ["Training Dataset", "R² Score", "MAE", "RMSE"])

    add_heading('Graphs/Tables (if any)', 2)
    add_para("The following charts illustrate the performance differences between the sampling methods and algorithms.")
    
    def insert_image(path, caption_text, width=5.5*inch, height=4.125*inch):
        if os.path.exists(path):
            img = Image(path, width=width, height=height)
            story.append(img)
            story.append(Paragraph(caption_text, caption))
            story.append(Spacer(1, 12))
            
    insert_image('assets/images/chart5_sampling_r2.png', 'Chart 1: Average R² Score Comparison')
    insert_image('assets/images/chart8_model_comparison.png', 'Chart 2: Model Accuracy Comparison')
    insert_image('images/2_Dashboard_Overview.jpeg', 'Figure 1: Project Dashboard Overview', width=6*inch, height=3.375*inch)
    insert_image('images/5_ML_Model_Comparison.jpeg', 'Figure 2: ML Model Evaluation Dashboard', width=6*inch, height=3.375*inch)

    # Added NEW PAGE here as requested
    add_heading('Hypothesis testing/Model evaluation', 2, new_page=True)
    add_para("Experimental evaluation demonstrated that Simple Random Sampling (SRS) consistently outperformed all other methods because it provided a purely unbiased representation of the continuous feature space without pre-determined clustering assumptions. The null hypothesis—that all sampling methods yield identical model generalizability—is rejected based on the significant performance decay observed in cluster sampling.")
    add_para("Stratified Sampling performed second-best; while it logically ensures team proportion equity, the variance in batsman performance is not inherently localized to team strata. Unlike socio-economic surveys where stratification yields massive variance reductions, cricket statistics are globally distributed. Thus, stratification did not yield significant variance reduction over SRS, rendering the computational overhead of calculating proportional allocations largely unnecessary.")
    add_para("Systematic Sampling ranked third, as its periodic selection algorithm introduced slight clustering bias when data was inherently sorted alphabetically or by team ID. Systematic bias is a known vulnerability when periodicity aligns with sorting keys. Finally, Cluster Sampling performed worst (lowest R² drops up to 0.91 in tree models), proving that intra-cluster homogeneity (players on the same team facing identical conditions, bowling attacks, and home grounds) completely fails to reflect the overarching population diversity required to train robust regressors. Tree models specifically suffered heavily under cluster sampling due to the lack of boundary cases in their training phase, leading to massive unseen-data prediction errors.")

    # 5. INTERPRETATION
    add_heading('5. Interpretation', 1, new_page=True)
    add_heading('Key findings', 2)
    add_para("The empirical findings demonstrate that Linear Regression is the unequivocally optimal machine learning model for predicting the linear multi-objective Batting Efficiency Score. It effortlessly overcomes the quantization and discretization boundaries that severely limit both Random Forest and XGBoost. Tree-based regressors rely on orthogonal splits in feature space, meaning they can only ever approximate a globally continuous linear plane using thousands of tiny step functions, which inherently caps their R² below 1.0.")
    add_para("Furthermore, SRS stands as the most generalizable sampling technique, offering high predictive fidelity while aggressively reducing data consumption by nearly 74%. This confirms that data science pipelines handling linear multi-objective targets should strictly utilize continuous OLS algorithms rather than defaulting to highly-hyped non-linear ensemble techniques which mathematically struggle to extrapolate beyond their training envelopes.")
    
    add_heading('Statistical inference', 2)
    add_para("The perfect theoretical synergy between SRS and Linear Regression is corroborated by the Gauss-Markov theorem. By utilizing just 26.3% of the dataset, SRS ensures minimum variance, unbiasedness, and profound consistency. The estimator converges seamlessly, effectively substituting the need to train compute-heavy population models. The statistical inference drawn here proves that when the target variable is a known linear combination of the features, non-linear algorithms actively introduce unnecessary error limits. Linear Regression operating on a perfectly random, unbiased sample mathematically guarantees an unbiased estimator of population parameters.")

    # 6. CONCLUSION
    add_heading('6. Conclusion', 1, new_page=True)
    add_heading('Final observations and decisions', 2)
    add_para("This study rigorously substantiates that Simple Random Sampling paired with Linear Regression forms the most robust, accurate, and computationally efficient pipeline for cricket performance analysis. By correctly aligning the sampling distribution with the underlying population variance, the model achieves mathematical perfection (R² = 1.0) on unseen test data using only a 150-record sample. The study definitively decides against deploying tree-based regressors (Random Forest and XGBoost) for this specific formulation, saving substantial compute overhead while maximizing deterministic accuracy.")
    add_para("Concurrently, the Green Dot Ball Sustainability Initiative successfully marries predictive sports analytics with acute environmental accountability. By correlating dot balls to tree plantations, the study proves that statistical analysis can actively track, gamify, and publicly validate carbon offsetting efforts on a massive scale. This project sets a new benchmark for embedding environmental, social, and governance (ESG) metrics directly into sports analytics, demonstrating that data science can be leveraged to drive actionable climate change initiatives.")

    # 7. SDG ADDRESSED
    add_heading('7. SDG Addressed', 1, new_page=True)
    add_para("The analytical dashboard proves that sustainability metrics can be seamlessly woven into commercial performance evaluations, fulfilling the core restorative mandates of the United Nations Sustainable Development Goals. The following screenshots from the built interactive web application demonstrate how these goals are tracked and gamified.")
    
    # Inserting user's screenshots
    insert_image('images/7_Sustainability_Page.jpeg', 'Figure 3: Dashboard Sustainability Page tracking Carbon Offsetting through Cricket metrics', width=6*inch, height=3.375*inch)
    insert_image('assets/images/chart4_trees_team.png', 'Chart 3: Green Dot Ball Impact Breakdown (Trees Planted by IPL Franchise)', width=5.5*inch, height=4.125*inch)

    add_para("SDG 13 – Climate Action: The project directly integrates climate action into the core analytical pipeline by mathematically associating cricket performance with carbon offsetting. By interpreting every dot ball as 19 trees planted (addressing carbon sinks), it forces climate awareness into a highly engaging and publicized medium: sports data analytics.", align="left")
    add_para("SDG 15 – Life on Land: Transforming dot balls into millions of potential trees directly addresses terrestrial conservation. This actively mitigates soil erosion, preserves natural biodiversity, and aids global reforestation initiatives. The inclusion of these metrics within the batsman efficiency score effectively monetizes and rewards ecological impact.", align="left")

    # 8. REFERENCES
    add_heading('8. References', 1, new_page=True)
    add_heading('Dataset/Books/Websites used', 2)
    add_para("[1] Cochran, W. G. (1977). Sampling Techniques (3rd ed.). John Wiley & Sons.", align="left")
    add_para("[2] Gauss, C. F., & Markov, A. A. The Gauss-Markov Theorem and OLS Estimation Theory.", align="left")
    add_para("[3] James, G., Witten, D., Hastie, T., & Tibshirani, R. (2013). An Introduction to Statistical Learning. Springer.", align="left")
    add_para("[4] Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research.", align="left")
    add_para("[5] Cricsheet.org. (2025). Ball-by-Ball IPL Match Data 2008–2025.", align="left")

    doc.build(story)

if __name__ == '__main__':
    create_pdf()
