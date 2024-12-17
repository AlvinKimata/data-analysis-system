import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

# Initialize a global variable to hold the data
data = None

# Function to load data
def load_data(file):
    global data
    data = pd.read_csv(file.name)
    return data.head()

# Function to clean and transform the dataset
def clean_and_transform(df, drop_columns, fill_missing):
    # Drop specified columns
    df_cleaned = df.drop(columns=drop_columns)
    
    # Fill missing values with the specified method (mean or median)
    if fill_missing == 'Mean':
        df_cleaned = df_cleaned.fillna(df_cleaned.mean())
    elif fill_missing == 'Median':
        df_cleaned = df_cleaned.fillna(df_cleaned.median())
    
    return df_cleaned.head()

# Function to load the cleaned dataset
def load_cleaned_data(file):
    global data
    data = pd.read_csv(file.name)
    return data.head()

# Function to generate statistics
def generate_statistics(df, column):
    if column not in df.columns:
        return "Column not found in dataset."
    
    stats_summary = {
        'Mean': df[column].mean(),
        'Median': df[column].median(),
        'Standard Deviation': df[column].std(),
        'Min': df[column].min(),
        'Max': df[column].max()
    }
    
    return stats_summary

# Function to generate correlation heatmap
def generate_correlation(df):
    correlation_matrix = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.show()

# Function to plot the distribution of a column
def plot_column_distribution(df, column):
    if column not in df.columns:
        return "Column not found in dataset."
    
    plt.figure(figsize=(8, 6))
    sns.histplot(df[column], kde=True)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.show()

# Function to perform Chi-square test for correlation analysis between two columns
def chi_square_test(df, column1, column2):
    if column1 not in df.columns or column2 not in df.columns:
        return "One or both columns not found in dataset."
    
    contingency_table = pd.crosstab(df[column1], df[column2])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    
    return f"Chi-square statistic: {chi2}\np-value: {p_value}\nDegrees of freedom: {dof}"

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("## Data Analysis and Visualization Tool")
    
    with gr.Tab("Load Data"):
        file_input = gr.File(label="Upload CSV File")
        load_button = gr.Button("Load Data")
        file_output = gr.Dataframe()

        load_button.click(fn=load_data, inputs=file_input, outputs=file_output)
    
    with gr.Tab("Data Cleaning and Transformation"):
        drop_columns = gr.Textbox(label="Columns to Drop (comma-separated)")
        fill_missing = gr.Dropdown(choices=["None", "Mean", "Median"], label="Fill Missing Data with")
        clean_button = gr.Button("Clean Data")
        clean_output = gr.Dataframe()

        clean_button.click(fn=clean_and_transform, inputs=[file_input, drop_columns, fill_missing], outputs=clean_output)
    
    with gr.Tab("Generate Statistics"):
        column_stat = gr.Dropdown(label="Select Column", choices=[], multiselect=False)
        stat_button = gr.Button("Generate Statistics")
        stat_output = gr.JSON()
        
        stat_button.click(fn=generate_statistics, inputs=[file_input, column_stat], outputs=stat_output)
    
    with gr.Tab("Correlation Analysis"):
        correlation_button = gr.Button("Generate Correlation Heatmap")
        correlation_output = gr.Plot()
        
        correlation_button.click(fn=generate_correlation, inputs=file_input, outputs=correlation_output)
    
    with gr.Tab("Plot Column Distribution"):
        column_dist = gr.Dropdown(label="Select Column", choices=[], multiselect=False)
        plot_button = gr.Button("Plot Distribution")
        plot_output = gr.Plot()
        
        plot_button.click(fn=plot_column_distribution, inputs=[file_input, column_dist], outputs=plot_output)
    
    with gr.Tab("Chi-Square Test"):
        column1 = gr.Dropdown(label="Select First Column", choices=[], multiselect=False)
        column2 = gr.Dropdown(label="Select Second Column", choices=[], multiselect=False)
        chi_square_button = gr.Button("Run Chi-Square Test")
        chi_square_output = gr.Textbox(label="Chi-Square Test Results")

        chi_square_button.click(fn=chi_square_test, inputs=[file_input, column1, column2], outputs=chi_square_output)

demo.launch()
