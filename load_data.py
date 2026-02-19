import sqlite3
import csv
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Configuration ---
DB_FILE = os.path.join(SCRIPT_DIR, "cell_counts.db")
CSV_FILE = os.path.join(SCRIPT_DIR, "cell-count.csv")

def initialize_database():
    """
    Initializes the SQLite database. Deletes the old DB file if it exists
    and creates the necessary tables (Subjects, Samples).
    """
    # Delete the old database file if it exists to ensure a clean start
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old database file: {DB_FILE}")

    # Connect to the SQLite database (this will create the file)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"Database {DB_FILE} created.")

    # --- Create the Subjects table ---
    # This table stores information unique to each subject.
    # subject_id is the PRIMARY KEY.
    cursor.execute("""
        CREATE TABLE Subjects (
            subject_id TEXT PRIMARY KEY,
            project TEXT,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT
        );
    """)
    print("Table 'Subjects' created.")

    # --- Create the Samples table ---
    # This table stores data for each sample, linking back to a subject.
    # sample_id is the PRIMARY KEY.
    # subject_id is a FOREIGN KEY that references the Subjects table.
    cursor.execute("""
        CREATE TABLE Samples (
            sample_id TEXT PRIMARY KEY,
            subject_id TEXT,
            sample_type TEXT,
            time_from_treatment_start INTEGER,
            b_cell INTEGER,
            cd8_t_cell INTEGER,
            cd4_t_cell INTEGER,
            nk_cell INTEGER,
            monocyte INTEGER,
            FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id)
        );
    """)
    print("Table 'Samples' created.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def load_data():
    """
    Loads data from the tab-separated CSV file into the SQLite database.
    It populates the Subjects and Samples tables.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Use a set to keep track of subjects already added to avoid duplicates
    processed_subjects = set()

    # Open the CSV file and read it
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as infile:
            # Use csv.DictReader with comma delimiter (default)
            reader = csv.DictReader(infile)
            
            print(f"\nLoading data from {CSV_FILE}...")
            
            for row in reader:
                subject_id = row['subject']
                
                # --- Populate Subjects table (if subject is new) ---
                if subject_id not in processed_subjects:
                    cursor.execute("""
                        INSERT INTO Subjects (subject_id, project, condition, age, sex, treatment, response)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        subject_id,
                        row['project'],
                        row['condition'],
                        int(row['age']),
                        row['sex'],
                        row['treatment'],
                        row['response']
                    ))
                    processed_subjects.add(subject_id)

                # --- Populate Samples table ---
                cursor.execute("""
                    INSERT INTO Samples (sample_id, subject_id, sample_type, time_from_treatment_start, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['sample'],
                    subject_id,
                    row['sample_type'],
                    int(row['time_from_treatment_start']),
                    int(row['b_cell']),
                    int(row['cd8_t_cell']),
                    int(row['cd4_t_cell']),
                    int(row['nk_cell']),
                    int(row['monocyte'])
                ))
            
            conn.commit()
            print("Data loaded successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{CSV_FILE}' was not found.")
        print("Please make sure the file is in the same directory as the script.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

# --- Main execution block ---
if __name__ == "__main__":
    initialize_database()
    load_data()
