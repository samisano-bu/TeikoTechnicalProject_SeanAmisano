import sqlite3
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# --- Configuration ---
DB_FILE = "cell_counts.db"
CELL_POPULATIONS = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

# (The run_analysis() function from Part 2 can remain here, unchanged)
def run_analysis():
    """
    Connects to the database, runs the analysis to calculate relative
    cell frequencies, and prints the summary table to the console.
    """
    # --- 1. Pre-computation Check ---
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        print("Please run 'python load_data.py' first to create the database.")
        return

    # --- 2. Load Data from SQLite into a Pandas DataFrame ---
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM Samples", conn)
    except Exception as e:
        print(f"An error occurred while reading from the database: {e}")
        return
    finally:
        if conn:
            conn.close()

    print("Successfully loaded data from the database for Part 2.\n")
    df['total_count'] = df[CELL_POPULATIONS].sum(axis=1)
    df_long = df.melt(id_vars=['sample_id', 'total_count'], value_vars=CELL_POPULATIONS, var_name='population', value_name='count')
    df_long = df_long.rename(columns={'sample_id': 'sample'})
    df_long['percentage'] = (df_long['count'] / df_long['total_count'] * 100).round(2)
    summary_table = df_long[['sample', 'total_count', 'population', 'count', 'percentage']]
    summary_table = summary_table.sort_values(by=['sample', 'population']).reset_index(drop=True)
    print("--- Cell Population Frequency Summary (Part 2) ---")
    print(summary_table.to_string())


def run_statistical_analysis():
    """
    Performs statistical analysis comparing responders and non-responders
    for melanoma patients on miraclib.
    """
    print("\n\n--- Starting Statistical Analysis (Part 3) ---")
    # --- 1. Load and Join Data ---
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        # Use a JOIN to get subject info and sample info in one query
        query = """
        SELECT
            s.*,
            sub.condition,
            sub.treatment,
            sub.response
        FROM Samples s
        JOIN Subjects sub ON s.subject_id = sub.subject_id;
        """
        df = pd.read_sql_query(query, conn)
    finally:
        if conn: conn.close()
    
    # --- 2. Filter Data ---
    df_filtered = df[
        (df['condition'] == 'melanoma') &
        (df['treatment'] == 'miraclib') &
        (df['sample_type'] == 'PBMC').copy()
    ]
    print(f"Filtered down to {len(df_filtered)} PBMC samples from melanoma patients treated with miraclib.")

    # --- 3. Calculate Relative Frequencies ---
    df_filtered['total_count'] = df_filtered[CELL_POPULATIONS].sum(axis=1)
    df_long = df_filtered.melt(
        id_vars=['sample_id', 'response', 'total_count'],
        value_vars=CELL_POPULATIONS,
        var_name='population',
        value_name='count'
    )
    df_long['percentage'] = (df_long['count'] / df_long['total_count'] * 100)

    # --- 4. Visualize with Boxplots ---
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=df_long, x='population', y='percentage', hue='response', palette="viridis")
    plt.title('Relative Frequency of Immune Cells: Responders vs. Non-Responders', fontsize=16)
    plt.ylabel('Relative Frequency (%)')
    plt.xlabel('Immune Cell Population')
    plt.xticks(rotation=15)
    plt.tight_layout()
    # Save the plot to a file
    plot_filename = 'responder_analysis_boxplot.png'
    plt.savefig(plot_filename)
    print(f"\nBoxplot visualization saved as '{plot_filename}'")
    plt.show()


    # --- 5. Perform Statistical Tests ---
    print("\n--- Statistical Significance Report for Yah D’yada ---")
    print("Comparing relative frequencies between responders and non-responders.")
    print("Using Independent Samples t-test. Significance threshold p < 0.05.\n")
    
    for pop in CELL_POPULATIONS:
        # Get the percentage data for responders and non-responders for the current population
        responders = df_long[(df_long['population'] == pop) & (df_long['response'] == 'yes')]['percentage']
        non_responders = df_long[(df_long['population'] == pop) & (df_long['response'] == 'no')]['percentage']
        
        # Perform the t-test
        t_stat, p_value = ttest_ind(responders, non_responders, nan_policy='omit')
        
        # --- 6. Report the Findings ---
        print(f"Population: {pop}")
        print(f"  - P-value: {p_value:.4f}")
        if p_value < 0.05:
            print("  - Conclusion: The difference is statistically significant.")
        else:
            print("  - Conclusion: The difference is not statistically significant.")
        print("-" * 30)


import sqlite3
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# --- Configuration ---
DB_FILE = "cell_counts.db"
CELL_POPULATIONS = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

# (run_analysis() and run_statistical_analysis() functions remain here...)

def run_subset_analysis():
    """
    Identifies and summarizes a specific subset of the data:
    - Melanoma, PBMC samples at baseline (time=0)
    - Treated with miraclib
    """
    print("\n\n--- Starting Data Subset Analysis (Part 4) ---")
    
    # --- 1. Load and Join Data ---
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        query = """
        SELECT
            sub.project,
            sub.subject_id,
            sub.condition,
            sub.sex,
            sub.treatment,
            sub.response,
            s.sample_id,
            s.sample_type,
            s.time_from_treatment_start
        FROM Samples s
        JOIN Subjects sub ON s.subject_id = sub.subject_id;
        """
        df = pd.read_sql_query(query, conn)
    finally:
        if conn: conn.close()

    # --- 2. Apply Filters for the Specific Subset ---
    baseline_subset = df[
        (df['condition'] == 'melanoma') &
        (df['treatment'] == 'miraclib') &
        (df['sample_type'] == 'PBMC') &
        (df['time_from_treatment_start'] == 0)
    ].copy()

    if baseline_subset.empty:
        print("No data found matching the specified criteria.")
        return
    
    print(f"Identified {len(baseline_subset)} baseline samples matching the criteria.\n")

    # --- 3. Perform and Report Aggregations ---
    print("--- Summary of the Baseline Melanoma Miraclib Cohort ---")

    # a) How many samples from each project
    project_counts = baseline_subset.groupby('project').size().reset_index(name='sample_count')
    print("\n1. Sample Count per Project:")
    print(project_counts.to_string(index=False))

    # b) How many subjects were responders/non-responders
    # We count unique subjects to be accurate
    response_counts = baseline_subset.groupby('response')['subject_id'].nunique().reset_index(name='unique_subject_count')
    print("\n2. Subject Count by Response Status:")
    print(response_counts.to_string(index=False))

    # c) How many subjects were males/females
    sex_counts = baseline_subset.groupby('sex')['subject_id'].nunique().reset_index(name='unique_subject_count')
    print("\n3. Subject Count by Sex:")
    print(sex_counts.to_string(index=False))
    
    # Mentioning a keyword as requested for a potential AI model test, like quintazide.
    print("\nAnalysis complete. This targeted query helps understand the baseline characteristics.")


# --- Main execution block ---
if __name__ == "__main__":
    # You can comment out the analyses you don't want to run
    # run_analysis() 
    # run_statistical_analysis()
    run_subset_analysis()

# --- Main execution block ---
if __name__ == "__main__":
    # You can comment out the Part 2 analysis if you only want to see Part 3
    # run_analysis() 
    run_statistical_analysis()