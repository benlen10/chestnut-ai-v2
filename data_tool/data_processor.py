import os
import pandas as pd
from datetime import datetime
from typing import List, Tuple
import json
from dotenv import load_dotenv
import shutil

def filter_data_by_date(file_path: str, start_date: str, end_date: str, date_column: str) -> pd.DataFrame:
    """
    Filters data from a file based on a date range.

    Args:
        file_path (str): Path to the data file.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        date_column (str): Name of the column containing dates.

    Returns:
        pd.DataFrame: Filtered data.
    """
    # Read the file into a DataFrame
    data = pd.read_csv(file_path)

    # Convert the date column to datetime
    data[date_column] = pd.to_datetime(data[date_column])

    # Filter the data based on the date range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    filtered_data = data[(data[date_column] >= start) & (data[date_column] <= end)]

    return filtered_data

def process_data_sources(sources: List[Tuple[str, str, str]], start_date: str, end_date: str):
    """
    Processes multiple data sources and filters data for the specified date range.

    Args:
        sources (List[Tuple[str, str, str]]): List of tuples containing file path, date column, and output path.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    """
    for file_path, date_column, output_path in sources:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        print(f"Processing file: {file_path}")
        filtered_data = filter_data_by_date(file_path, start_date, end_date, date_column)

        # Save the filtered data to the output path
        filtered_data.to_csv(output_path, index=False)
        print(f"Filtered data saved to: {output_path}")

def filter_spotify_data(file_path: str, start_date: str, end_date: str) -> list:
    """
    Filters Spotify JSON data based on a date range.

    Args:
        file_path (str): Path to the Spotify JSON file.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.

    Returns:
        list: Filtered JSON data.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    with open(file_path, "r") as file:
        data = json.load(file)

    filtered_data = [
        entry for entry in data
        if start <= datetime.strptime(entry["ts"], "%Y-%m-%dT%H:%M:%SZ") <= end
    ]

    return filtered_data

def save_spotify_data_for_journaling(filtered_data: list, output_dir: str, start_date: str, end_date: str):
    """
    Saves Spotify data in an optimized format for journaling.

    Args:
        filtered_data (list): Filtered Spotify data.
        output_dir (str): Directory to save the output file.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"spotify_journal_{start_date}_to_{end_date}.txt")

    with open(output_file, "w") as file:
        for entry in filtered_data:
            journal_entry = (
                f"Date: {entry['ts']}\n"
                f"Track: {entry['master_metadata_track_name']}\n"
                f"Artist: {entry['master_metadata_album_artist_name']}\n"
                f"Album: {entry['master_metadata_album_album_name']}\n"
                f"Platform: {entry['platform']}\n"
                f"Time Played: {entry['ms_played']} ms\n"
                "---\n"
            )
            file.write(journal_entry)

    print(f"Journal-ready Spotify data saved to: {output_file}")

def process_spotify_data(start_date: str, end_date: str):
    """
    Processes Spotify data for the specified date range and saves it for journaling.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    """
    load_dotenv()
    spotify_path = os.getenv("SPOTIFY_DATA_PATH")
    output_dir = os.getenv("OUTPUT_PATH")

    if not spotify_path or not os.path.exists(spotify_path):
        print("Spotify data path not found or not specified in .env file.")
        return
    if not output_dir:
        print("Output path not specified in .env file.")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Identify the correct JSON file based on naming convention
    for file_name in os.listdir(spotify_path):
        if file_name.startswith("Streaming_History_Audio") and file_name.endswith(".json"):
            file_path = os.path.join(spotify_path, file_name)
            print(f"Processing Spotify file: {file_path}")

            filtered_data = filter_spotify_data(file_path, start_date, end_date)

            # Save the filtered data in an optimized format for journaling
            save_spotify_data_for_journaling(filtered_data, output_dir, start_date, end_date)

def process_screenshots(start_date: str, end_date: str):
    """
    Processes screenshots for the specified date range by copying them to the output folder.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    """
    load_dotenv()
    screenshots_path = os.getenv("SCREENSHOTS_PATH")
    output_dir = os.getenv("OUTPUT_PATH")

    if not screenshots_path or not os.path.exists(screenshots_path):
        print("Screenshots path not found or not specified in .env file.")
        return
    if not output_dir:
        print("Output path not specified in .env file.")
        return

    screenshots_output_dir = os.path.join(output_dir, "screenshots")
    os.makedirs(screenshots_output_dir, exist_ok=True)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    for file_name in os.listdir(screenshots_path):
        file_path = os.path.join(screenshots_path, file_name)

        if os.path.isfile(file_path):
            try:
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                if start <= file_date <= end:
                    shutil.copy(file_path, screenshots_output_dir)
                    print(f"Copied screenshot: {file_name}")
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

def process_all_data(start_date: str, end_date: str):
    """
    Processes all data types (Spotify, screenshots, etc.) for the specified date range.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
    """
    process_spotify_data(start_date, end_date)
    process_screenshots(start_date, end_date)
