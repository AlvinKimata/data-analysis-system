import io
from PIL import Image
import gradio as gr
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class DataAnalysisApp:
    def __init__(self):
        self.original_data = None
        self.processed_data = None
        self.merged_data = None
    
    def load_csv_files(self, activity_log, user_log, component_codes):
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
    
    def clean_and_merge_data(self):
        try:
            if not self.original_data:
                return "Please load the data first.", None
            
            # Load data
            activity_log = self.original_data['activity'].copy()
            user_log = self.original_data['user'].copy()
            
            # Rename columns
            activity_log = activity_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})
            user_log = user_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})
            
            # Remove 'System' and 'Folder' components
            activity_log = activity_log[~activity_log['Component'].isin(['System', 'Folder'])]
            
            # Convert date columns to datetime
            user_log['Date'] = pd.to_datetime(user_log['Date'].str.split().str[0], format='%d/%m/%Y')
            
            # Drop duplicates
            activity_log = activity_log.drop_duplicates(subset=['User_ID', 'Component', 'Action', 'Target'])
            user_log = user_log.drop_duplicates(subset=['Date', 'Time', 'User_ID'])
            
            # Merge data
            merged_data = user_log.merge(activity_log, on='User_ID', how='left')
            merged_data['Month'] = merged_data['Date'].dt.to_period('M')
            
            self.merged_data = merged_data
            return "Data cleaned and merged successfully!", merged_data.head().to_html()
        except Exception as e:
            return f"Error during data processing: {str(e)}", None
        
    def generate_statistics(self, target_components):
        try:
            if self.merged_data is None:
                return "Please process data first.", None
            
            # Filter for target components
            filtered_data = self.merged_data[self.merged_data['Component'].isin(target_components)]
            
            # Add Month column
            filtered_data['Month'] = filtered_data['Date'].dt.to_period('M')
            
            # Overall semester statistics
            semester_stats = {}
            for component in target_components:
                comp_data = filtered_data[filtered_data['Component'] == component]
                semester_interactions = comp_data.groupby('Month').size()
                semester_stats[component] = {
                    'mean': semester_interactions.mean(),
                    'median': semester_interactions.median(),
                    'mode': semester_interactions.mode().values[0] if not semester_interactions.mode().empty else np.nan
                }
            
            semester_stats_df = pd.DataFrame(semester_stats).T.reset_index().rename(columns={'index': 'Component'})
            
            # Monthly statistics
            monthly_stats = {}
            for component in target_components:
                comp_data = filtered_data[filtered_data['Component'] == component]
                
                # Group by Month and compute metrics for each month
                for month, month_data in comp_data.groupby('Month'):
                    if month not in monthly_stats:
                        monthly_stats[month] = {}
                    
                    # Count interactions for the month
                    monthly_interactions = month_data.groupby('Component').size()
                    
                    # Compute statistics for this component in this month
                    monthly_stats[month][component] = {
                        'mean': monthly_interactions.mean(),
                        'median': monthly_interactions.median(),
                        'mode': monthly_interactions.mode().values[0] if len(monthly_interactions.mode()) > 0 else np.nan
                    }

            # Flatten the monthly statistics dictionary
            flattened_stats = []
            for month, components in monthly_stats.items():
                for component, metrics in components.items():
                    flattened_stats.append({'Month': month, 'Component': component, **metrics})
            
            monthly_stats_df = pd.DataFrame(flattened_stats)
            
            # Return both semester and monthly statistics as HTML
            semester_html = semester_stats_df.to_html()
            monthly_html = monthly_stats_df.to_html()

            data = "Semester statistics:\n\n" + semester_html + "Monthly statistics: \n\n\n" + monthly_html
            return "Statistics generated successfully:", data
        
        except Exception as e:
            return f"Error generating statistics: {str(e)}", None
    
    def generate_correlation_heatmap(self, target_components):
        try:
            if self.merged_data is None:
                return "Please process data first.", None
            
            # Filter for target components
            filtered_data = self.merged_data[self.merged_data['Component'].isin(target_components)]
            
            # Create interaction matrix
            interaction_matrix = filtered_data.pivot_table(
                index='User_ID', columns='Component', aggfunc='size', fill_value=0)
            
            # Calculate correlation matrix
            correlation_matrix = interaction_matrix.corr()
            print(f"correlation_matrix: {correlation_matrix}")
            
            # Plot heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
            plt.title("Component Interaction Correlation Heatmap")
            plt.tight_layout()  # Adjust layout to prevent cut-off labels

            save_path = "/home/kamikaze/Documents/projects/data-analysis-system/heatmap.png"
            try:
                plt.savefig(save_path, bbox_inches='tight')
                print(f"Heatmap saved to {save_path}")
            except Exception as e:
                print(f"Error saving heatmap: {e}")
            
            # # Save plot as a temporary image.
            # plt.savefig("./heatmap.png")
            plt.close()
            return save_path
        except Exception as e:
            return f"Error generating heatmap: {str(e)}", None

def create_gradio_interface():
    app = DataAnalysisApp()
    
    with gr.Blocks() as demo:
        gr.Markdown("# Data Analysis Application")
        
        with gr.Tab("Load Data"):
            activity_file = gr.File(label="Upload Activity Log CSV")
            user_file = gr.File(label="Upload User Log CSV")
            component_file = gr.File(label="Upload Component Codes CSV")
            load_btn = gr.Button("Load Files")
            load_output = gr.Markdown()
            activity_preview = gr.HTML()
            user_preview = gr.HTML()
            component_preview = gr.HTML()
            
            load_btn.click(
                app.load_csv_files, 
                inputs=[activity_file, user_file, component_file],
                outputs=[load_output, activity_preview, user_preview, component_preview]
            )
        
        with gr.Tab("Clean and Merge Data"):
            process_btn = gr.Button("Clean and Merge Data")
            process_output = gr.Markdown()
            merged_preview = gr.HTML()
            process_btn.click(
                app.clean_and_merge_data, 
                outputs=[process_output, merged_preview]
            )
        
        with gr.Tab("Generate Statistics"):
            components = gr.CheckboxGroup(
                label="Select Components", 
                choices=['Quiz', 'Lecture', 'Assignment', 'Attendence', 'Survey']
            )
            stats_btn = gr.Button("Generate Statistics")
            stats_output = gr.Markdown()
            stats_table = gr.HTML()
            stats_btn.click(
                app.generate_statistics, 
                inputs=[components], 
                outputs=[stats_output, stats_table]
            )
        
        with gr.Tab("Generate Heatmap"):
            gr.Markdown("### Generate a Heatmap with Component Correlations")

            # Textbox input for target components (comma-separated)
            components_input = gr.Textbox(label="Target Components", value="Quiz,Lecture,Assignment,Attendence,Survey")
            output = gr.Image(label="Correlation Heatmap")
            btn = gr.Button("Generate Heatmap")

            # Button click event
            btn.click(
                fn=lambda components: app.generate_correlation_heatmap(components.split(',')),
                inputs=components_input,
                outputs=output
            )

    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(debug=True)
