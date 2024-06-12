from src.paths import config
import json
import csv
import os


def save_json(data, filepath, mode="w", indent=4):
    """Saves data in a json file"""
    with open(filepath, mode) as file:
        json.dump(data, file, indent=indent)


def save_csv(file, mode="a", **data):
    """Gets data in a dictionary type format and stores it in a csv file"""
    file_path = os.path.abspath(file)

    with open(file_path, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)  # Creating a CSV writer object
        file_size = os.path.getsize(file_path)

        if file_size == 0:  # Write headers if not already
            writer.writerow(data.keys())

        # Writing a row for each trade
        writer.writerow(data.values())


def edit_json(file=config, **kwargs):
    """Updates config.json variables"""
    config_file = file

    # Reading the data
    with open(config_file, "r") as f:
        config_data = json.load(f)

    # Editing variables
    for variable, value in kwargs.items():
        if variable in config_data:
            config_data[variable] = value

    # Updating the file with changes
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=4)


def read_json(*variables, file=config):
    """Reads the JSON file and returns the value(s)"""
    with open(file, "r") as data_file:
        config_data = json.load(data_file)

    values = {}
    for variable in variables:
        values[variable] = config_data.get(variable)  # Using '.get' for safe access

    return values
