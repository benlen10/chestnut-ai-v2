from data_tool.data_processor import process_all_data, process_apple_photos, process_location_history

if __name__ == "__main__":
    # Define the date range for testing
    start_date = "2023-12-24"
    end_date = "2023-12-31"

    # Call the function to process all data types
    process_all_data(start_date, end_date)

    # Call the function to process Apple Photos
    process_apple_photos(start_date, end_date)

    # Call the function to process location history
    process_location_history(start_date, end_date)