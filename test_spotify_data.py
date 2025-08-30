from data_tool.data_processor import process_spotify_data

if __name__ == "__main__":
    # Define the date range for testing
    start_date = "2023-12-24"
    end_date = "2023-12-31"

    # Call the function to process Spotify data
    process_spotify_data(start_date, end_date)
