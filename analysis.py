import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

# --- Configuration ---
DB_FILE = "cell_counts.db"
TABLE_NAME = "cell_counts"
SIGNIFICANCE_THRESHOLD = 0.05
CELL_POPULATIONS = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def run_statistical_analysis():
    """
    Performs the main statistical analysis comparing cell frequencies
    between responders and non-responders. (Corresponds to Part 3)
    """
    print("\n--- Starting Statistical Analysis (Part 3) ---")
    conn = get_db_connection()
    
    try:
        # This query selects the data for the main analysis.
        # We are looking for all PBMC samples, regardless of condition or treatment initially.
        query = f"SELECT * FROM {TABLE_NAME} WHERE sample_type = 'PBMC'"
        df = pd.read_sql_query(query, conn)
        print(f"Loaded {len(df)} PBMC samples for analysis.")

        # Melt the data to make it easy to plot and analyze
        df_melted = df.melt(
            id_vars=['subject_id', 'response'],
            value_vars=CELL_POPULATIONS,
            var_name='population',
            value_name='count'
        )

        # --- Data Visualization (Boxplot) ---
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='population', y='count', hue='response', data=df_melted)
        plt.title('Cell Counts by Population and Response Status (PBMC Samples)')
        plt.ylabel('Relative Frequency (Count)')
        plt.xlabel('Cell Population')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_filename = 'responder_analysis_boxplot.png'
        plt.savefig(output_filename)
        print(f"\nBoxplot visualization saved as '{output_filename}'")

        # --- Statistical Significance Testing ---
        print("\n--- Statistical Significance Report ---")
        print(f"Comparing cell counts between responders and non-responders across all PBMC samples.")
        print(f"Using Independent Samples t-test. Significance threshold p < {SIGNIFICANCE_THRESHOLD}.")

        for pop in CELL_POPULATIONS:
            print("-" * 30)
            print(f"Population: {pop}")
            responders = df[df['response'] == 'yes'][pop]
            non_responders = df[df['response'] == 'no'][pop]
            if len(responders) > 1 and len(non_responders) > 1:
                t_stat, p_value = ttest_ind(responders, non_responders, nan_policy='omit')
                print(f"  - P-value: {p_value:.4f}")
                if p_value < SIGNIFICANCE_THRESHOLD:
                    print("  - Conclusion: The difference is statistically significant.")
                else:
                    print("  - Conclusion: The difference is not statistically significant.")
            else:
                print("  - Not enough data to perform t-test.")
        print("-" * 30)

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
    finally:
        conn.close()

def run_subset_analysis():
    """
    Runs a descriptive analysis on a specific subset of the data. (Corresponds to Part 4)
    """
    print("\n--- Starting Data Subset Analysis (Part 4) ---")
    conn = get_db_connection()

    try:
        # Query for baseline melanoma samples
        query = f"SELECT * FROM {TABLE_NAME} WHERE condition = 'melanoma' AND time = 0"
        df = pd.read_sql_query(query, conn)
        print(f"Identified {len(df.subject_id.unique())} unique subjects from baseline melanoma samples.")

        print("\n--- Summary of the Baseline Melanoma Cohort ---")

        project_counts = df.groupby('project')['subject_id'].nunique().reset_index(name='sample_count')
        print("\n1. Sample Count per Project:")
        print(project_counts.to_string(index=False))

        response_counts = df.groupby('response')['subject_id'].nunique().reset_index(name='unique_subject_count')
        print("\n2. Subject Count by Response Status:")
        print(response_counts.to_string(index=False))
        
        sex_counts = df.groupby('sex')['subject_id'].nunique().reset_index(name='unique_subject_count')
        print("\n3. Subject Count by Sex:")
        print(sex_counts.to_string(index=False))

        print("\nAnalysis complete.")

    except Exception as e:
        print(f"An error occurred during subset analysis: {e}")
    finally:
        conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    run_subset_analysis()
    run_statistical_analysis()
