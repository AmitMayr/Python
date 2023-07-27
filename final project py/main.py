from initialize import initializer
from menu import display_menu


def main():
    tremps_df, users_df, users_in_tremp_df, tremps_with_year_month, combined_table = initializer()
    display_menu(tremps_df, users_df, users_in_tremp_df, tremps_with_year_month, combined_table)


if __name__ == "__main__":
    main()
