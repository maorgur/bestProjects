#u can get the db from https://github.com/wiedehopf/tar1090-db/raw/refs/heads/csv/aircraft.csv.gz

import csv
import json
import sys

def csv_to_json(csv_file, json_file):
    """Convert CSV file to JSON file using first column as keys and third column as values."""
    data = {}
    count = 0
    try:
        with open(csv_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter=';')
            
            for row in reader:
                if len(row) >= 3 and row[2]:  # Check if 3rd column exists and is not empty
                    data[row[0]] = row[2]
                    count += 1
        
        with open(json_file, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=4)
        
        print(f"Successfully converted {csv_file} to {json_file}, with {count} entries.")
    
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input.csv> <output.json>")
        sys.exit(1)
    
    csv_to_json(sys.argv[1], sys.argv[2])
