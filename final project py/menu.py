from data_processing import calc_total_hitchhikers, calc_total_tremps, calc_avg_people_per_tremp, \
    get_top_hour_df, calculate_top_hours, calc_top_5_drivers, change_file, download_Dataframe, get_combined_table
from data_visualization import (
    plot_tremps_by_month, plot_tremps_by_year_month, plot_top_5_drivers,
    plot_top_5_routes, plot_percentage_by_tremp_id, plot_gender_count,
    plot_top_hours, display_dataframe
)


def display_menu(tremps_df, users_df, users_in_tremp_df, tremps_with_year_month, combined_table):
    main_menu = """Choose an option:
1. Display total tremps
2. Display total hitchhikers
3. Display average users per tremp
4. Display tremps by year and month / month
5. Display top 5 drivers
6. Display top 5 routes
7. Display top 5 hours
8. Tremp types percentages
9. Display gender statistics
10.Show table
~. To change File
0. Exit"""
    while True:
        print(main_menu)
        choice = input("Enter your choice (0-10): ")
        if choice == '~':
            file_path_choice = input("""1.Python TrempBoss file.xlsx
2.second TrempBoss file.xlsx
Enter your choice (1-2):""")
            if file_path_choice == '1':
                file_path = './exel file/Python TrempBoss file.xlsx'
            elif file_path_choice == '2':
                file_path = './exel file/second TrempBoss file.xlsx'
            tremps_df, users_df, users_in_tremp_df, tremps_with_year_month = change_file(file_path)
            combined_table = get_combined_table(tremps_df, users_df, users_in_tremp_df)

            # tremps_df.shape[0]
            print("File path changed to ", file_path)
        elif choice == '1':
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
            print("""1. by year and month
2. by month""")
            statistics_choice = input("Enter your choice (1 or 2): ")
            if statistics_choice == "1":
                plot_tremps_by_year_month(tremps_with_year_month)
            elif statistics_choice == "2":
                plot_tremps_by_month(tremps_with_year_month)
        elif choice == '5':
            top_5_drivers_df = calc_top_5_drivers(tremps_df, users_in_tremp_df, users_df)
            plot_top_5_drivers(top_5_drivers_df)  # Display top 5 drivers on a bar plot
        elif choice == '6':
            plot_top_5_routes(tremps_df)  # Display top 5 routes on a bar plot
        elif choice == '7':
            top_hours = calculate_top_hours(tremps_df)
            top_hour_df = get_top_hour_df(top_hours)
            plot_top_hours(top_hour_df)
        elif choice == '8':
            plot_percentage_by_tremp_id(tremps_df, users_in_tremp_df)  # Display top 5 routes on a bar plot
        elif choice == '9':
            print("""1. Display percentages
2. Display normal bar""")
            gender_choice = input("Enter your choice (1 or 2): ")
            if gender_choice == "1":
                plot_gender_count(users_df, as_percentage=True)
            else:
                plot_gender_count(users_df)
        elif choice == '10':
            print("""1.Combined table
2. Tremps table
3. Users table
4. Users in tremps table""")
            table_choice = input("Enter your choice (1 - 4): ")
            if table_choice == "1":
                table_picked = combined_table
                file_name = "combined_table"
            elif table_choice == "2":
                table_picked = tremps_df
                file_name = "tremps_df"
            elif table_choice == "3":
                table_picked = users_df
                file_name = "users_df"
            elif table_choice == "4":
                table_picked = users_in_tremp_df
                file_name = "users_in_tremp_df"
            else:
                continue
            how_to_display = input("Enter your choice (D [To download] or W [To show in new window]): ")
            if how_to_display == "D":
                output_folder = f'./{file_name}_files'
                download_Dataframe(table_picked, output_folder)
            elif how_to_display == "W":
                display_dataframe(table_picked)
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
