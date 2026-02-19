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

def run_analysis():
    """
    Performs statistical analysis and generates a boxplot visualization.
    """
    print("\n--- Starting Full Analysis ---")
    conn = get_db_connection()
    
    try:
        # Query to select all relevant data for the analysis
        query = f"""
            SELECT *
            FROM {TABLE_NAME}
            WHERE 
                disease = 'melanoma' AND
                treatment = 'miraclib' AND
                sample_type = 'pbmc'
        """
        df = pd.read_sql_query(query, conn)
        print(f"Filtered down to {len(df)} PBMC samples from melanoma patients treated with miraclib.")

        # --- Data Transformation (Melting) ---
        # We transform the data from a wide format (one column per cell type)
        # to a long format (one column for 'population', one for 'count').
        # This makes it much easier to plot with seaborn.
        df_melted = df.melt(
            id_vars=['subject_id', 'response'],
            value_vars=CELL_POPULATIONS,
            var_name='population',
            value_name='count'
        )

        # --- Data Visualization (Boxplot) ---
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='population', y='count', hue='response', data=df_melted)
        plt.title('Cell Counts by Population and Response Status (Melanoma, Miraclib, PBMC)')
        plt.ylabel('Relative Frequency (Count)')
        plt.xlabel('Cell Population')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_filename = 'responder_analysis_boxplot.png'
        plt.savefig(output_filename)
        print(f"\nBoxplot visualization saved as '{output_filename}'")

        # --- Statistical Significance Testing ---
        print("\n--- Statistical Significance Report ---")
        print(f"Comparing cell counts between responders and non-responders.")
        print(f"Using Independent Samples t-test. Significance threshold p < {SIGNIFICANCE_THRESHOLD}.")

        for pop in CELL_POPULATIONS:
            print("-" * 30)
            print(f"Population: {pop}")

            # Separate the data for the current cell population
            responders = df[df['response'] == 'yes'][pop]
            non_responders = df[df['response'] == 'no'][pop]

            # Perform the t-test
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

# --- Main execution block ---
if __name__ == "__main__":
    run_analysis()
