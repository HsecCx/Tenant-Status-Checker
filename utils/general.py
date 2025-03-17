import os
import csv
from typing import List, Dict, Any

class AuditUtils:
    
    def write_json_list_to_csv(self, json_list: List[Dict[str, Any]], filename: str) -> None:
        """
        Writes a list of JSON objects to a CSV file.

        Parameters:
        ----------
        json_list : List[Dict[str, Any]]
            A list of dictionaries (JSON-like structures) to be written into the CSV file.
        filename : str
            The name of the CSV file to write the data into.

        Returns:
        -------
        None
        """
        if not json_list:
            print("No data to write to CSV.")
            return

        # Ensure all items in json_list are dictionaries
        flattened_list = []
        for item in json_list:
            if isinstance(item, list):  # If it's a list, extend it
                flattened_list.extend(item)
            elif isinstance(item, dict):  # If it's a dict, add it directly
                flattened_list.append(item)
            else:  # Unexpected type, skip
                print(f"Skipping unsupported type: {type(item)}")

        # Collect all possible keys for the CSV headers
        all_keys = set()
        for item in flattened_list:
            if isinstance(item, dict):  # Ensure item is a dictionary
                all_keys.update(item.keys())

        # Ensure the target folder exists
        if not os.path.exists(self.default_save_folder):
            os.makedirs(self.default_save_folder)

        csv_filename = os.path.join(self.default_save_folder, filename)

        # Write to CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=list(all_keys))
            dict_writer.writeheader()
            for row in flattened_list:
                if isinstance(row, dict):  # Ensure row is a dictionary
                    # Write only the keys present in fieldnames
                    filtered_row = {key: row.get(key, "") for key in dict_writer.fieldnames}
                    dict_writer.writerow(filtered_row)

        print(f"Data successfully written to {csv_filename}")