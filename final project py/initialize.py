from data_processing import change_file, get_combined_table


def initializer():
    file_path = './exel file/Python TrempBoss file.xlsx'
    tremps_df, users_df, users_in_tremp_df, tremps_with_year_month = change_file(file_path)
    combined_table = get_combined_table(tremps_df, users_df, users_in_tremp_df)
    return tremps_df, users_df, users_in_tremp_df, tremps_with_year_month, combined_table
