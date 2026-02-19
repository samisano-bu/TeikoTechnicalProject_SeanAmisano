import sqlite3
import pandas as pd
import os

# --- Configuration ---
DB_FILE = "cell_counts.db"
CSV_FILE = "cell-count.csv"

def create_database():
    """
    Creates and populates the SQLite database from the CSV file.
    A single denormalized table 'cell_counts' is created for simplicity.
    """
    # Ensure we start fresh by removing the old database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old database file: {DB_FILE}")

    try:
        # Load the raw data from the CSV file into a pandas DataFrame
        df = pd.read_csv(CSV_FILE)
        print(f"Successfully loaded data from {CSV_FILE}")

        # Rename columns to be more database-friendly (no spaces, all lowercase)
        df.rename(columns={
            'subject': 'subject_id',
            'time_from_treatment_start': 'time'
        }, inplace=True)

        # Establish a connection to the SQLite database
        conn = sqlite3.connect(DB_FILE)
        print(f"Database {DB_FILE} created.")

        # Write the entire DataFrame to a new SQL table named 'cell_counts'
        df.to_sql('cell_counts', conn, index=False, if_exists='replace')
        print("Table 'cell_counts' created and populated.")

        # Close the database connection
        conn.close()
        print("Database creation process complete.")

    except FileNotFoundError:
        print(f"Error: The file '{CSV_FILE}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    create_database()
