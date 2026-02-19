import pandas as pd
import sqlite3

def calculate_avg_b_cells():
    """
    Calculate average B cell count for melanoma male responders at baseline.
    (Answers Part 4 of the assignment)
    """
    conn = sqlite3.connect('cell_counts.db')
    query = """
    SELECT b_cell
    FROM cell_counts
    WHERE
        condition = 'melanoma' AND
        sample_type = 'PBMC' AND
        treatment = 'miraclib' AND
        sex = 'M' AND
        response = 'yes' AND
        time = 0
    """
    df = pd.read_sql_query(query, conn)
    average_count = df['b_cell'].mean()
    conn.close()
    
    print(f"Average B cells for melanoma male responders at baseline: {average_count:.2f}")
    return average_count

if __name__ == "__main__":
    calculate_avg_b_cells()
