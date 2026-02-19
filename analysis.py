import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

# --- Configuration ---
DB_FILE = "cell_counts.db"
TABLE_NAME = "cell_counts"
SIGNIFICANCE_THRESHOLD = 0.05

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def run_statistical_analysis():
    """
    Performs the main statistical analysis comparing cell frequencies
    between responders and non-responders.
    """
    print("\n--- Starting Statistical Analysis ---")
    conn = get_db_connection()
    
    try:
        # This query selects all relevant data for the analysis
        query = f"""
            SELECT subject_id, response, population, count
            FROM {TABLE_NAME}
            WHERE 
                disease = 'melanoma' AND
                treatment = 'miraclib' AND
                sample_type = 'pbmc'
        """
        df = pd.read_sql_query(query, conn)
        print(f"Filtered down to {len(df)} PBMC samples from melanoma patients treated with miraclib.")

        # --- Data Visualization (Boxplot) ---
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='population', y='count', hue='response', data=df)
        plt.title('Cell Counts by Population and Response Status')
        plt.ylabel('Relative Frequency (Count)')
        plt.xlabel('Cell Population')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_filename = 'responder_analysis_boxplot.png'
        plt.savefig(output_filename)
        print(f"\nBoxplot visualization saved as '{output_filename}'")

        # --- Statistical Significance Testing ---
        print("\n--- Statistical Significance Report ---")
        print(f"Comparing relative frequencies between responders and non-responders.")
        print(f"Using Independent Samples t-test. Significance threshold p < {SIGNIFICANCE_THRESHOLD}.")

        cell_populations = df['population'].unique()
        for pop in cell_populations:
            print("-" * 30)
            print(f"Population: {pop}")

            # Separate the data for responders and non-responders
            responders = df[(df['population'] == pop) & (df['response'] == 'yes')]['count']
            non_responders = df[(df['population'] == pop) & (df['response'] == 'no')]['count']

            # Perform the t-test
            if len(responders) > 1 and len(non_responders) > 1:
                t_stat, p_value = ttest_ind(responders, non_responders, nan_policy='omit')
                print(f"  - P-value: {p_value:.4f}")
                
                # Determine significance
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
    Runs a descriptive analysis on a specific subset of the data:
    melanoma patients, baseline samples (time=0).
    """
    print("\n--- Starting Data Subset Analysis ---")
    conn = get_db_connection()

    try:
        # This query uses the simple 'cell_counts' table
        query = f"""
            SELECT *
            FROM {TABLE_NAME}
            WHERE 
                disease = 'melanoma'
                AND time = 0;
        """
        df = pd.read_sql_query(query, conn)
        print(f"Identified {len(df)} baseline samples matching the criteria.")

        print("\n--- Summary of the Baseline Melanoma Cohort ---")

        # 1. Sample count per project
        project_counts = df.groupby('project')['subject_id'].nunique().reset_index(name='sample_count')
        print("\n1. Sample Count per Project:")
        print(project_counts.to_string(index=False))

        # 2. Subject count by response status
        response_counts = df.groupby('response')['subject_id'].nunique().reset_index(name='unique_subject_count')
        print("\n2. Subject Count by Response Status:")
        print(response_counts.to_string(index=False))
        
        # 3. Subject count by sex
        sex_counts = df.groupby('sex')['subject_id'].nunique().reset_index(name='unique_subject_count')
        print("\n3. Subject Count by Sex:")
        print(sex_counts.to_string(index=False))

        print("\nAnalysis complete. This query helps understand baseline characteristics.")

    except Exception as e:
        print(f"An error occurred during subset analysis: {e}")
    finally:
        conn.close()


# --- Main execution block ---
if __name__ == "__main__":
    run_subset_analysis()
    run_statistical_analysis()
