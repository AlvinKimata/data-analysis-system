import gradio as gr
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

class DataAnalysisApp:
    def __init__(self):
        self.original_data = None
        self.processed_data = None
        self.current_data = None
    
    def load_csv_files(self, activity_log, user_log, component_codes):
        """
        Load initial CSV files
        """
        try:
            # Validate file uploads
            if not all([activity_log, user_log, component_codes]):
                return "Please upload all three CSV files.", None, None, None
            
            # Read CSV files
            activity_df = pd.read_csv(activity_log)
            user_df = pd.read_csv(user_log)
            component_df = pd.read_csv(component_codes)
            
            # Store original data
            self.original_data = {
                'activity': activity_df,
                'user': user_df,
                'component': component_df
            }
            
            return (
                "Files loaded successfully!",
                activity_df.head().to_html(),
                user_df.head().to_html(),
                component_df.head().to_html()
            )
        except Exception as e:
            return f"Error loading files: {str(e)}", None, None, None
    
    def clean_and_transform_data(self):
        """
        Apply data cleaning and transformation
        """
        try:
            if not self.original_data:
                return "Please load data first.", None
            
            # 1. REMOVE: Remove System and Folder components
            activity_log = self.original_data['activity'].copy()
            activity_log = activity_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})
            activity_log = activity_log[~activity_log['Component'].isin(['System', 'Folder'])]
            
            # 2. Rename columns in user log
            user_log = self.original_data['user'].copy()
            user_log = user_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})
            

            # 3. Check for duplicate combinations
            print("\nChecking for duplicate combinations:")
            print("User Log unique User IDs:", user_log['User_ID'].nunique())
            print("Activity Log unique User IDs:", activity_log['User_ID'].nunique())

            # 4. Convert date columns to datetime, handling the time information
            user_log['Date'] = pd.to_datetime(user_log['Date'].str.split().str[0], format='%d/%m/%Y')

            # 5. Ensure unique combinations in activity log
            activity_log = activity_log.drop_duplicates(subset=['User_ID', 'Component', 'Action', 'Target'])

            # 6. Ensure unique combinations in user log
            user_log = user_log.drop_duplicates(subset=['Date', 'Time', 'User_ID'])

            # 7. Merge and process data
            merged_data = user_log.merge(activity_log, on='User_ID', how='left')
            merged_data['Month'] = merged_data['Date'].dt.to_period('M')

            # 8. Count interactions
            interaction_counts = merged_data.groupby(['User_ID', 'Component', 'Month']).size().reset_index(name='Interaction_Count')

            # 9. Pivot the data
            pivoted_data = interaction_counts.pivot_table(
                index=['User_ID', 'Month'], 
                columns='Component', 
                values='Interaction_Count', 
                fill_value=0
            ).reset_index()

            # 10. Flatten column names
            pivoted_data.columns.name = None
            pivoted_data = pivoted_data.rename(
                columns={col: f'{col}_Interactions' if col not in ['User_ID', 'Month'] else col for col in pivoted_data.columns}
            )

            # 11. Convert Month to string
            pivoted_data['Month'] = pivoted_data['Month'].astype(str)

            # 12. Store processed data
            self.processed_data = pivoted_data
            self.current_data = pivoted_data

            return "Data processed successfully!", pivoted_data.head().to_html()

        except Exception as e:
            return f"Error processing data: {str(e)}", None
    
    def generate_statistics(self, columns_to_analyze, stat_type):
        """
        Generate descriptive statistics
        """
        try:
            if self.current_data is None:
                return "Please process data first.", None
            
            # Validate columns
            available_columns = self.current_data.columns.tolist()
            columns_to_analyze = [col for col in columns_to_analyze if col in available_columns]
            
            if not columns_to_analyze:
                return "No valid columns selected.", None
            
            # Generate statistics based on type
            if stat_type == 'Descriptive':
                stats = self.current_data[columns_to_analyze].describe()
            elif stat_type == 'Correlation':
                stats = self.current_data[columns_to_analyze].corr()
            
            return f"{stat_type} Statistics", stats.to_html()
        except Exception as e:
            return f"Error generating statistics: {str(e)}", None
    
    def generate_visualization(self, x_column, y_column, plot_type):
        """
        Generate visualizations
        """
        try:
            if self.current_data is None:
                return "Please process data first.", None
            
            # Clear any existing plots
            plt.clf()
            
            # Create plot based on type
            if plot_type == 'Scatter':
                plt.figure(figsize=(10, 6))
                plt.scatter(self.current_data[x_column], self.current_data[y_column])
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                plt.title(f'Scatter Plot: {x_column} vs {y_column}')
            
            elif plot_type == 'Line':
                plt.figure(figsize=(10, 6))
                self.current_data.groupby('Month')[y_column].mean().plot(kind='line')
                plt.xlabel('Month')
                plt.ylabel(y_column)
                plt.title(f'Line Plot: Average {y_column} by Month')
            
            elif plot_type == 'Histogram':
                plt.figure(figsize=(10, 6))
                plt.hist(self.current_data[y_column], bins=20)
                plt.xlabel(y_column)
                plt.ylabel('Frequency')
                plt.title(f'Histogram of {y_column}')
            
            # Convert plot to base64 for Gradio
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return "Visualization generated!", f"data:image/png;base64,{image_base64}"
        except Exception as e:
            return f"Error generating visualization: {str(e)}", None
    
    def filter_data(self, filter_column, min_val, max_val):
        """
        Filter data based on specified range
        """
        try:
            if self.processed_data is None:
                return "Please process data first.", None
            
            # Filter data
            filtered_data = self.processed_data[
                (self.processed_data[filter_column] >= min_val) & 
                (self.processed_data[filter_column] <= max_val)
            ]
            
            # Update current data
            self.current_data = filtered_data
            
            return "Data filtered successfully!", filtered_data.head().to_html()
        except Exception as e:
            return f"Error filtering data: {str(e)}", None

def create_gradio_interface():
    """
    Create Gradio interface for the data analysis application
    """
    # Initialize the application
    app = DataAnalysisApp()
    
    # Create Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("# Data Analysis Application")
        
        # Data Loading Tab
        with gr.Tab("Load Data"):
            with gr.Row():
                activity_log = gr.File(label="Activity Log CSV")
                user_log = gr.File(label="User Log CSV")
                component_codes = gr.File(label="Component Codes CSV")
            
            load_btn = gr.Button("Load Files")
            load_output = gr.Markdown()
            
            # Data Preview
            with gr.Accordion("Data Preview", open=False):
                activity_preview = gr.HTML()
                user_preview = gr.HTML()
                component_preview = gr.HTML()
            
            # Load Files Event
            load_btn.click(
                app.load_csv_files, 
                inputs=[activity_log, user_log, component_codes],
                outputs=[load_output, activity_preview, user_preview, component_preview]
            )
        
        # Data Processing Tab
        with gr.Tab("Process Data"):
            process_btn = gr.Button("Clean and Transform Data")
            process_output = gr.Markdown()
            process_preview = gr.HTML()
            
            process_btn.click(
                app.clean_and_transform_data, 
                outputs=[process_output, process_preview]
            )
        
        # Data Analysis Tab
        with gr.Tab("Analyze Data"):
            # Statistics Section
            with gr.Group():
                gr.Markdown("## Generate Statistics")
                stat_columns = gr.Dropdown(
                    label="Select Columns", 
                    multiselect=True,
                    choices=[]  # Will be populated dynamically
                )
                stat_type = gr.Dropdown(
                    label="Statistics Type", 
                    choices=['Descriptive', 'Correlation']
                )
                stat_btn = gr.Button("Generate Statistics")
                stat_output = gr.HTML()
                
                # Update column choices when data is processed
                process_btn.click(
                    lambda: gr.Dropdown(choices=app.processed_data.columns.tolist() if app.processed_data is not None else []),
                    outputs=[stat_columns]
                )
            
            # Visualization Section
            with gr.Group():
                gr.Markdown("## Generate Visualizations")
                x_column = gr.Dropdown(
                    label="X-Axis Column", 
                    choices=[]  # Will be populated dynamically
                )
                y_column = gr.Dropdown(
                    label="Y-Axis Column", 
                    choices=[]  # Will be populated dynamically
                )
                plot_type = gr.Dropdown(
                    label="Plot Type", 
                    choices=['Scatter', 'Line', 'Histogram']
                )
                plot_btn = gr.Button("Generate Visualization")
                plot_output = gr.Markdown()
                plot_image = gr.Image()
                
                # Update column choices when data is processed
                process_btn.click(
                    lambda: (
                        gr.Dropdown(choices=app.processed_data.columns.tolist() if app.processed_data is not None else []),
                        gr.Dropdown(choices=app.processed_data.columns.tolist() if app.processed_data is not None else [])
                    ),
                    outputs=[x_column, y_column]
                )
            
            # Statistics Generation Event
            stat_btn.click(
                app.generate_statistics,
                inputs=[stat_columns, stat_type],
                outputs=[plot_output, stat_output]
            )
            
            # Visualization Generation Event
            plot_btn.click(
                app.generate_visualization,
                inputs=[x_column, y_column, plot_type],
                outputs=[plot_output, plot_image]
            )
        
        # Data Filtering Tab
        with gr.Tab("Filter Data"):
            gr.Markdown("## Filter Processed Data")
            filter_column = gr.Dropdown(
                label="Column to Filter", 
                choices=[]  # Will be populated dynamically
            )
            min_val = gr.Number(label="Minimum Value")
            max_val = gr.Number(label="Maximum Value")
            filter_btn = gr.Button("Apply Filter")
            filter_output = gr.Markdown()
            filter_preview = gr.HTML()
            
            # Update column choices when data is processed
            process_btn.click(
                lambda: gr.Dropdown(choices=app.processed_data.columns.tolist() if app.processed_data is not None else []),
                outputs=[filter_column]
            )
            
            # Filter Data Event
            filter_btn.click(
                app.filter_data,
                inputs=[filter_column, min_val, max_val],
                outputs=[filter_output, filter_preview]
            )
    
    return demo

# Launch the Gradio interface
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(debug=True)