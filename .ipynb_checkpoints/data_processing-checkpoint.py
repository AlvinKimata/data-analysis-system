import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class DataCleaner:
    def __init__(self):
        """Initialize the DataCleaner class."""
        self.cleaned_data = {}

    def load_csv(self, file_path):
        """
        Load a CSV file into a Pandas DataFrame.
        Args:
            file_path (str): Path to the CSV file.
        Returns:
            pd.DataFrame: Loaded DataFrame.
        """
        try:
            df = pd.read_csv(file_path)
            print(f"Successfully loaded: {file_path}")
            return df
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    def clean_data(self, df, file_name):
        """
        Clean the dataset by handling missing values and removing irrelevant rows.
        Args:
            df (pd.DataFrame): Input DataFrame.
            file_name (str): Name of the file being cleaned.
        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if df is None:
            print(f"No data to clean in {file_name}.")
            return None

        try:
            if file_name == "USER_LOG":
                df = df.dropna(subset=["Date", "Time"])

            elif file_name == "ACTIVITY_LOG":
                df = df.dropna(subset=["Component", "Action"])
                df = df[~df["Component"].isin(["System", "Folder"])]

            elif file_name == "COMPONENT_CODES":
                df = df.dropna(subset=["Component", "Code"])
            print(f"Data cleaning successful for {file_name}.")
            
            return df
        except Exception as e:
            print(f"Error during cleaning for {file_name}: {e}")
            return None

    def rename_columns(self, df, file_name):
        """
        Rename columns in the DataFrame.
        Args:
            df (pd.DataFrame): Input DataFrame.
            file_name (str): Name of the file being processed.
        Returns:
            pd.DataFrame: DataFrame with renamed columns.
        """
        if "User Full Name *Anonymized" in df.columns:
            df.rename(columns={"User Full Name *Anonymized": "User_ID"}, inplace=True)
            print(f"Columns renamed for {file_name}.")
        return df

    def merge_data(self, activity_log, user_log):
        """
        Merge activity log with user log for user interaction analysis.
        Args:
            activity_log (pd.DataFrame): Cleaned ACTIVITY_LOG DataFrame.
            user_log (pd.DataFrame): Cleaned USER_LOG DataFrame.
        Returns:
            pd.DataFrame: Merged DataFrame.
        """
        merged_df = pd.merge(activity_log, user_log, on="User_ID", how="inner")
        print("Data merged successfully.")
        return merged_df

    def reshape_data(self, df):
        """
        Reshape the data using a pivot operation.
        Args:
            df (pd.DataFrame): Merged DataFrame.
        Returns:
            pd.DataFrame: Pivoted DataFrame.
        """
        df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M")
        pivot_df = df.pivot_table(index="User_ID", columns="Component", values="Action", aggfunc="count", fill_value=0)
        print("Data reshaped successfully.")
        return pivot_df

    def calculate_statistics(self, df, components):
        """
        Calculate mean, mode, and median for specific components.
        Args:
            df (pd.DataFrame): Merged DataFrame.
            components (list): List of components to calculate statistics for.
        Returns:
            dict: Dictionary containing statistics.
        """
        stats = {}
        for component in components:
            if component in df.columns:
                stats[component] = {
                    "mean": df[component].mean(),
                    "mode": df[component].mode().iloc[0],
                    "median": df[component].median(),
                }
        print("Statistics calculated.")
        return stats

    def plot_correlation(self, df, components):
        """
        Plot a correlation heatmap for specific components.
        Args:
            df (pd.DataFrame): Merged DataFrame.
            components (list): List of components to analyze.
        """
        correlation_df = df[components]
        correlation_matrix = correlation_df.corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Correlation between Components")
        plt.show()

    def process_files(self, file_paths):
        """
        Load, clean, and process multiple files.
        Args:
            file_paths (dict): Dictionary of file names and paths.
        """
        for file_name, path in file_paths.items():
            df = self.load_csv(path)
            df = self.clean_data(df, file_name)
            df = self.rename_columns(df, file_name)
            self.cleaned_data[file_name] = df

    def display_cleaned_data(self):
        """
        Display the cleaned DataFrames.
        """
        for file_name, df in self.cleaned_data.items():
            print(f"\nCleaned {file_name}:")
            print(df.head())

# Example usage
if __name__ == "__main__":
    file_paths = {
        "USER_LOG": "USER_LOG.csv",
        "ACTIVITY_LOG": "ACTIVITY_LOG.csv",
        "COMPONENT_CODES": "COMPONENT_CODES.csv",
    }

    cleaner = DataCleaner()
    cleaner.process_files(file_paths)
    cleaner.display_cleaned_data()

    # Merge data
    merged_df = cleaner.merge_data(cleaner.cleaned_data["ACTIVITY_LOG"], cleaner.cleaned_data["USER_LOG"])

    # Reshape data
    pivot_df = cleaner.reshape_data(merged_df)

    # Calculate statistics
    components = ["Quiz", "Lecture", "Assignment", "Attendance", "Survey"]
    stats = cleaner.calculate_statistics(pivot_df, components)
    print("\nStatistics:")
    for component, stat in stats.items():
        print(f"{component}: {stat}")

    # Plot correlation
    components_to_analyze = ["Assignment", "Quiz", "Lecture", "Book", "Project", "Course"]
    cleaner.plot_correlation(pivot_df, components_to_analyze)
