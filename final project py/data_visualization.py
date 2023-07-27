# To display graphs
import matplotlib.pyplot as plt
# To get the percentages from the data_processing
from data_processing import calculate_percentages

# To see table in new window
import tkinter as tk
from tkinter import ttk


#
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
    # year  month  tremps_count
    tremps_by_year_month = tremps_df.groupby(['year', 'month']).size().reset_index(name='tremps_count')
    print(tremps_by_year_month)
    plt.figure()
    plt.bar(range(len(tremps_by_year_month)), tremps_by_year_month['tremps_count'])
    plt.xlabel('Year - Month')
    plt.ylabel('Number of Tremps')
    plt.title('Number of Tremps in Each Month, Sorted by Years')
    # The function is used to set the tick locations and labels on the x-axis of a plot.
    plt.xticks(range(len(tremps_by_year_month)), [f"{month}\\{year % 100}" for year, month in
                                                  zip(tremps_by_year_month['year'], tremps_by_year_month['month'])],
               rotation=90)
    plt.show()


def plot_top_5_drivers(top_5_drivers_df):
    print(top_5_drivers_df)
    plt.figure()
    plt.bar(top_5_drivers_df['Driver'], top_5_drivers_df['Number of Rides'])
    plt.xlabel('Driver name')
    plt.ylabel('Number of Rides')
    plt.title('Top 5 Drivers with the Most Rides')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


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


def plot_gender_count(users_df, as_percentage=False):
    # male value  female value
    gender_counts = users_df['gender'].value_counts()
    total_users = len(users_df)
    if as_percentage:
        gender_percentages = (gender_counts / total_users) * 100
        labels = ['Male', 'Female']  # Custom labels for the pie chart
        colors = ['#FFD700', '#FFA500']
        plt.figure()
        # male  value | female  value
        plt.pie([gender_percentages['male'], gender_percentages['female']], labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True)
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


def plot_top_hours(top_hours_df):
    # Create a new DataFrame with the desired structure

    # Create the bar plot
    plt.bar(top_hours_df['Index'], top_hours_df['Occurrences'])

    # Customize the plot
    plt.xlabel('Hour')
    plt.ylabel('Occurrences')
    plt.title('Top 5 Hours')
    plt.xticks(top_hours_df['Index'], top_hours_df['Hour Value'], rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def display_dataframe(dataframe):
    root = tk.Tk()
    root.title("TrempBoss Dataframe")

    # ['tremp_id', 'tremp_type', 'date', 'tremp_time', 'seats_amount',
    # 'from_route', 'to_route', 'full_name', 'users_in_tremp', 'creator'
    tree = ttk.Treeview(root)
    tree["columns"] = dataframe.columns.tolist()
    # Set column headings
    for column in dataframe.columns:
        tree.heading(column, text=column)
        tree.column(column, width=100, anchor="center")  # Set the column width and anchor to "center"
    # Insert data into the Treeview
    for index, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))

    # Add Treeview to the window
    tree.pack(expand=True, fill="both")

    root.mainloop()
