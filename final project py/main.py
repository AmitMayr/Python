import pandas as pd
import matplotlib.pyplot as plt


def load_data(file_path):
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    return all_sheets['tremps'], all_sheets['users'], all_sheets['users_in_tremps']


def calc_total_hitchhikers(tremps_df, users_in_tremp_df):
    non_creator_users_in_tremp = users_in_tremp_df[~users_in_tremp_df['is_tremp_creator']]
    total_hitchhikers = non_creator_users_in_tremp.shape[0]
    hitchhiker_tremps_with_non_creators = tremps_df[
        (tremps_df['tremp_id'].isin(non_creator_users_in_tremp['tremp_id'].unique())) &
        (tremps_df['tremp_type'] == 'hitchhiker')
        ]

    # Add the seats_amount from these tremps to total_hitchhikers
    total_hitchhikers += hitchhiker_tremps_with_non_creators['seats_amount'].sum()
    return total_hitchhikers


def calc_total_tremps(users_in_tremp_df):
    non_creator_users_in_tremp = users_in_tremp_df[~users_in_tremp_df['is_tremp_creator']]
    # Calculate the total number of tremps with non-creator users
    total_tremps = non_creator_users_in_tremp['tremp_id'].nunique()
    return total_tremps


def calc_avg_people_per_tremp(tremps_df, users_in_tremp_df):
    # Calculate the average people per tremp
    total_hitchhikers = calc_total_hitchhikers(tremps_df, users_in_tremp_df)
    total_tremps = calc_total_tremps(users_in_tremp_df)
    avg_people_per_tremp = total_hitchhikers / total_tremps
    # Handle NaN average people per tremp
    if pd.isna(avg_people_per_tremp):
        avg_people_per_tremp = 0

    # Format average people per tremp to two decimal places
    avg_people_per_tremp = "{:.2f}".format(avg_people_per_tremp)

    return avg_people_per_tremp


def plot_tremps_by_month(tremps_df):
    tremps_by_month = tremps_df.groupby('month').size()

    plt.figure()
    tremps_by_month.plot(kind='bar')
    plt.xlabel('Month')
    plt.ylabel('Number of Tremps')
    plt.title('Number of Tremps in Each Month')
    plt.xticks(rotation=0)
    plt.show()


def plot_tremps_by_year_month(tremps_df):
    tremps_by_year_month = tremps_df.groupby(['year', 'month']).size().reset_index(name='tremps_count')
    plt.figure()
    plt.bar(range(len(tremps_by_year_month)), tremps_by_year_month['tremps_count'])
    plt.xlabel('Year - Month')
    plt.ylabel('Number of Tremps')
    plt.title('Number of Tremps in Each Month, Sorted by Years')
    plt.xticks(range(len(tremps_by_year_month)), [f"{month}\\{year % 100}" for year, month in
                                                  zip(tremps_by_year_month['year'], tremps_by_year_month['month'])],
               rotation=90)
    plt.show()


def plot_top_5_drivers(top_5_drivers_df):
    plt.figure()
    plt.bar(top_5_drivers_df['Driver'], top_5_drivers_df['Number of Rides'])
    plt.xlabel('Driver name')
    plt.ylabel('Number of Rides')
    plt.title('Top 5 Drivers with the Most Rides')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def get_top_5_drivers(tremps_df, users_in_tremp_df, users_df):
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


def plot_top_5_routes(tremps_df):
    # from_route   to_route  Count
    top_5_routes = tremps_df.groupby(['from_route', 'to_route']).size().nlargest(5).reset_index(name='Count')
    plt.figure()
    plt.bar(range(len(top_5_routes)), top_5_routes['Count'])
    plt.xlabel('Route (From - To)')
    plt.ylabel('Number of Tremps')
    plt.title('Top 5 Routes with the Most Tremps')
    plt.xticks(range(len(top_5_routes)), [f"{from_route} - {to_route}" for from_route, to_route in
                                          zip(top_5_routes['from_route'], top_5_routes['to_route'])], rotation=45,
               ha='right')
    plt.tight_layout()
    plt.show()


def calculate_percentages(tremps_df, users_in_tremp_df):
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


def plot_pie_chart(percentages):
    labels = ['Open Rides', 'Join Drive', 'Join Tremp', 'Open Tremps']
    colors = ['#FFD700', '#FFA500', 'blue', '#87CEFA']
    plt.figure()
    plt.pie(percentages, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
    plt.axis('equal')
    plt.title('Percentage of Each Category')
    plt.show()


def plot_percentage_by_tremp_id(tremps_df, users_in_tremp_df):
    percentages = calculate_percentages(tremps_df, users_in_tremp_df)
    plot_pie_chart(percentages)


def display_gender_count(users_df, as_percentage=False):
    gender_counts = users_df['gender'].value_counts()
    total_users = len(users_df)
    if as_percentage:
        gender_percentages = (gender_counts / total_users) * 100
        labels = ['Male', 'Female']  # Custom labels for the pie chart
        colors = ['#FFD700', '#FFA500']
        plt.figure()
        plt.pie(gender_percentages.values, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
        plt.axis('equal')  # Make it circle default ellipse
        plt.title('Percentage of Males and Females')
        plt.show()
    else:

        # Plot a single bar with two different colors for male and female counts

        plt.bar(gender_counts.index, gender_counts.values, color=['#87CEFA', 'pink'])
        plt.ylabel('Count')

        plt.title('Number of Females and Males')

        plt.xticks(rotation=45)

        plt.show()

def calc_top_5_hours(tremps_df):
    # Convert 'tremp_time' column to pandas datetime format
    tremps_df['tremp_time'] = pd.to_datetime(tremps_df['tremp_time'])

    # Extract the hour from 'tremp_time' and count occurrences
    hours_counts = tremps_df['tremp_time'].dt.hour.value_counts()

    # Sort the hours in descending order and get the top 5 hours
    top_5_hours = hours_counts.head(5)

    return top_5_hours

def main():
    file_path = './exel file/Python TrempBoss file.xlsx'
    tremps_df, users_df, users_in_tremp_df = load_data(file_path)
    tremps_df['month'] = tremps_df['date'].dt.month
    tremps_df['year'] = tremps_df['date'].dt.year
    while True:
        print("Choose an option:")
        print("1. Display total tremps")
        print("2. Display total hitchhikers")
        print("3. Display average users per tremp")
        print("4. Display tremps by month")
        print("5. Display tremps by year and month")
        print("6. Display top 5 drivers")
        print("7. Display top 5 routes")
        print("8. Tremp types percentages")
        print("9. Gender")
        print("0. Exit")

        choice = input("Enter your choice (0-9): ")

        if choice == '1':
            total_tremps = calc_total_tremps(users_in_tremp_df)
            # tremps_df.shape[0]
            print("Total tremps:", total_tremps)
        elif choice == '2':
            total_hitchhikers = calc_total_hitchhikers(tremps_df, users_in_tremp_df)
            print("Total hitchhikers:", total_hitchhikers)
        elif choice == '3':
            average_users_per_tremp = calc_avg_people_per_tremp(tremps_df, users_in_tremp_df)
            print("Average users per tremp:", average_users_per_tremp)
        elif choice == '4':
            plot_tremps_by_month(tremps_df)
        elif choice == '5':
            plot_tremps_by_year_month(tremps_df)
        elif choice == '6':
            top_5_drivers_df = get_top_5_drivers(tremps_df, users_in_tremp_df, users_df)
            plot_top_5_drivers(top_5_drivers_df)  # Display top 5 drivers on a bar plot
        elif choice == '7':
            plot_top_5_routes(tremps_df)  # Display top 5 routes on a bar plot
        elif choice == '8':
            plot_percentage_by_tremp_id(tremps_df, users_in_tremp_df)  # Display top 5 routes on a bar plot
        elif choice == '9':
            print("1. Display percentages")
            print("2. Display normal bar")

            sub_choice = input("Enter your choice (1 or 2): ")

            def switch(gender_choice):
                if gender_choice == "1":
                    display_gender_count(users_df, as_percentage=True)
                else:
                    display_gender_count(users_df)

            switch(sub_choice)

        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
