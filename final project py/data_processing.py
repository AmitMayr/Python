# To make downloads with the date
from datetime import datetime
# Used to create directories for storing the output files and navigating through file paths.
import os
# Used to read files ,deal with merges
import pandas as pd


# Reads an Excel file and returns three specific sheets from the file.
def load_data(file_path: str):
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    return all_sheets['tremps'], all_sheets['users'], all_sheets['users_in_tremps']


# Merges three dataframes and performs various transformations and aggregations to create a combined table.
def get_combined_table(tremps_df: pd.DataFrame, users_df: pd.DataFrame, users_in_tremp_df: pd.DataFrame):
    # Merge users_in_tremp_df and tremps_df by the tremp_id
    merged_df = pd.merge(users_in_tremp_df, tremps_df, on='tremp_id', how='left')
    # Merge the result with users_df based on 'user_id'
    final_merged_df = pd.merge(merged_df, users_df, on='user_id', how='left')
    # Concatenate 'full_name' for users_in_tremp 
    final_merged_df['users_in_tremp'] = \
        final_merged_df[~final_merged_df['is_tremp_creator']].groupby(['tremp_id', 'is_tremp_creator'])[
            'full_name'].transform(
            lambda x: ', '.join(x))
    # It is assigning the values from the 'full_name' column to the 'creator' column for rows where the
    # 'is_tremp_creator' column is True. This is done to ensure that the 'creator' column contains the
    # full name of the tremp creator for those specific rows.
    final_merged_df.loc[final_merged_df['is_tremp_creator'], 'creator'] = final_merged_df.loc[
        final_merged_df['is_tremp_creator'], 'full_name']
    # Group by 'tremp_id' and aggregate columns with the 'first' aggregation
    grouped_df = final_merged_df.groupby('tremp_id').agg({
        'tremp_type': 'first',
        'date': 'first',
        'tremp_time': 'first',
        'seats_amount': 'first',
        'from_route': 'first',
        'to_route': 'first',
        'full_name': 'first',
        'users_in_tremp': 'first',
        'creator': 'first'
    }).reset_index()  # To make new indexes
    return grouped_df


# change file , gets the new path and return the new tables
def change_file(file_path: str):
    tremps_df, users_df, users_in_tremp_df = load_data(file_path)

    # Extract year and month from the 'date' column
    tremps_with_year_month = tremps_df.copy()
    tremps_with_year_month['month'] = tremps_with_year_month['date'].dt.month
    tremps_with_year_month['year'] = tremps_with_year_month['date'].dt.year

    # Convert 'date' column to string format to remove the hours from the date
    tremps_df['date'] = tremps_df['date'].dt.strftime('%Y-%m-%d')
    tremps_with_year_month['date'] = tremps_with_year_month['date'].dt.strftime('%Y-%m-%d')

    # Merge users_in_tremp_df with tremps_df

    return tremps_df, users_df, users_in_tremp_df, tremps_with_year_month


def calc_total_hitchhikers(tremps_df: pd.DataFrame, users_in_tremp_df: pd.DataFrame):
    non_creator_users_in_tremp = users_in_tremp_df[~users_in_tremp_df['is_tremp_creator']]
    total_hitchhikers = non_creator_users_in_tremp.shape[0]
    hitchhiker_tremps_with_non_creators = tremps_df[
        (tremps_df['tremp_id'].isin(non_creator_users_in_tremp['tremp_id'].unique())) &
        (tremps_df['tremp_type'] == 'hitchhiker')
        ]

    # Add the seats_amount from these tremps to total_hitchhikers
    total_hitchhikers += hitchhiker_tremps_with_non_creators['seats_amount'].sum()
    return total_hitchhikers


def calc_total_tremps(users_in_tremp_df: pd.DataFrame):
    non_creator_users_in_tremp = users_in_tremp_df[~users_in_tremp_df['is_tremp_creator']]
    # Calculate the total number of tremps with non-creator users
    total_tremps = non_creator_users_in_tremp['tremp_id'].nunique()
    return total_tremps


def calc_avg_people_per_tremp(tremps_df: pd.DataFrame, users_in_tremp_df: pd.DataFrame):
    # Calculate the average people per tremp
    total_hitchhikers = calc_total_hitchhikers(tremps_df, users_in_tremp_df)
    total_tremps = calc_total_tremps(users_in_tremp_df)
    avg_people_per_tremp = total_hitchhikers / total_tremps
    # Format average people per tremp to two decimal places
    avg_people_per_tremp = "{:.2f}".format(avg_people_per_tremp)

    return avg_people_per_tremp


def calculate_percentages(tremps_df: pd.DataFrame, users_in_tremp_df: pd.DataFrame):
    # Count the number of opened rides and opened tremps
    open_rides = tremps_df[tremps_df['tremp_type'] == "driver"].shape[0]
    open_tremps = tremps_df[tremps_df['tremp_type'] == "hitchhiker"].shape[0]

    # Merge the 'tremps' DataFrame with 'users_in_tremps' based on 'tremp_id' /only if is_tremp_creator is false.
    # tremp_id  tremp_type  date year  user_id is_tremp_creator
    merged_df = tremps_df.merge(users_in_tremp_df[~users_in_tremp_df['is_tremp_creator']], on='tremp_id')
    # Group by 'tremp_id' and 'tremp_type' and calculate the percentage of tremps for each 'tremp_id'
    # To see how many joined each tremps/rides
    # tremp_id  tremp_type  Number of Tremps
    tremps_percentage_df = (
        merged_df.groupby(['tremp_id', 'tremp_type'])
        .size()
        .reset_index(name='Number of Tremps')
    )
    # Calc the sum of users joined tremp/ride
    tremps_by_type = tremps_percentage_df.groupby('tremp_type')['Number of Tremps'].sum()
    join_drive = tremps_by_type['driver']
    join_tremp = tremps_by_type['hitchhiker']

    total_tremps = open_rides + open_tremps + join_drive + join_tremp
    # Calculate the percentages
    open_rides_percentage = (open_rides / total_tremps) * 100
    join_drive_percentage = (join_drive / total_tremps) * 100
    join_tremp_percentage = (join_tremp / total_tremps) * 100
    open_tremps_percentage = (open_tremps / total_tremps) * 100

    return open_rides_percentage, join_drive_percentage, join_tremp_percentage, open_tremps_percentage


def calculate_top_hours(tremps_df: pd.DataFrame):
    # Convert 'tremp_time' to datetime
    tremp_times = tremps_df['tremp_time']
    tremp_times = pd.to_datetime(tremp_times, format='%H:%M:%S')  # Convert 'tremp_time' to datetime format

    # Round hours
    rounded_hours = (tremp_times.dt.hour + (tremp_times.dt.minute >= 30)).mod(24)

    # Count the occurrences of each rounded hour and get the top 5 hours
    top_hours = rounded_hours.value_counts().nlargest(5).sort_values(ascending=False)

    return top_hours


def calc_top_5_drivers(tremps_df: pd.DataFrame, users_in_tremp_df: pd.DataFrame, users_df: pd.DataFrame):
    # Filter tremps_df to keep only rows where tremp_type is "driver"
    # tremp_id tremp_type date to_route  month  year
    driver_tremps_df = tremps_df[tremps_df['tremp_type'] == "driver"]
    # user_id  tremp_id  is_tremp_creator | only is_tremp_creator==true
    users_created_tremps_df = users_in_tremp_df[users_in_tremp_df['is_tremp_creator']]
    # tremp_id tremp_type date  month  year user_id
    merged_df = driver_tremps_df.merge(users_created_tremps_df[['tremp_id', 'user_id']], on='tremp_id')
    # Get the top 5 drivers with the highest number of rides using group by and nlargest.
    # Number of Rides  |  Driver name
    top_5_drivers_df = (
        merged_df
        .groupby('user_id')  # Group by 'user_id' to count the number of rides for each driver
        .size()
        .nlargest(5)
        .reset_index(name='Number of Rides')  # give the row new index , with the name Number of rides
        .merge(users_df[['user_id', 'full_name']], on='user_id')  # Merge with users_df to get 'full_name'
        .rename(columns={'full_name': 'Driver'})  # rename the column title name to driver
        # .drop(columns=['user_id'])  # remove the id field from the row
    )
    return top_5_drivers_df


def get_top_hour_df(top_hours):
    # The code is creating a new DataFrame called `top_hours_df` using the `pd.DataFrame()` function. It
    # is constructing the DataFrame with three columns: 'Index', 'Hour Value', and 'Occurrences'.
    top_hours_df = pd.DataFrame({
        'Index': range(1, len(top_hours) + 1),
        'Hour Value': top_hours.index,
        'Occurrences': top_hours.values
    })
    return top_hours_df


def download_Dataframe(table_choice, output_folder: str):
    # Get the styled version of the DataFrame
    styled_df = table_choice.style
    # Get the current timestamp in the format 'YYYY-MM-DD_HH-MM-SS'
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    # Define the Excel file name based on the timestamp
    excel_filename = f'{timestamp}.xlsx'
    output_path_excel = os.path.join(output_folder, excel_filename)
    # Save the DataFrame to an Excel file in the specified output folder
    styled_df.to_excel(output_path_excel, engine='openpyxl')
    # Define the HTML file name based on the timestamp
    html_filename = f'{timestamp}.html'
    output_path_html = os.path.join(output_folder, html_filename)
    # Save the DataFrame to an HTML file in the specified output folder
    styled_df.to_html(output_path_html)
