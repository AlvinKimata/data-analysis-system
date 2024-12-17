import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt

# Read CSV files
activity_log = pd.read_csv('inputs/ACTIVITY_LOG.csv')
component_codes = pd.read_csv('inputs/COMPONENT_CODES.csv')
user_log = pd.read_csv('inputs/USER_LOG.csv')


# Rename columns
activity_log = activity_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})
user_log = user_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})

# Remove System and Folder components
activity_log = activity_log[~activity_log['Component'].isin(['System', 'Folder'])]

# Convert date columns to datetime, handling the time information
user_log['Date'] = pd.to_datetime(user_log['Date'].str.split().str[0], format='%d/%m/%Y')

# Ensure unique combinations in activity log
activity_log = activity_log.drop_duplicates(subset=['User_ID', 'Component', 'Action', 'Target'])

# Merge user log with activity log
# Use left merge to keep all user log entries
merged_data = user_log.merge(activity_log, on='User_ID', how='left')


# Group by User_ID, Component, and month
merged_data['Month'] = merged_data['Date'].dt.to_period('M')

# Count interactions per user per component per month
interaction_counts = merged_data.groupby(['User_ID', 'Component', 'Month']).size().reset_index(name='Interaction_Count')

# Pivot the data to create a more structured view
pivoted_data = interaction_counts.pivot_table(
index=['User_ID', 'Month'], 
columns='Component', 
values='Interaction_Count', 
fill_value=0
).reset_index()

# Flatten the multi-level column names
pivoted_data.columns.name = None
pivoted_data = pivoted_data.rename(columns={col: f'{col}_Interactions' if col not in ['User_ID', 'Month'] else col for col in pivoted_data.columns})

# Convert Month to string for readability
pivoted_data['Month'] = pivoted_data['Month'].astype(str)

# Save the processed data
# pivoted_data.to_csv('processed_user_interactions.csv', index=False)


# Ensure unique combinations in activity log
activity_log = activity_log.drop_duplicates(subset=['User_ID', 'Component', 'Action', 'Target'])

# Convert date columns to datetime, handling the time information
user_log['Date'] = pd.to_datetime(user_log['Date'].str.split().str[0], format='%d/%m/%Y')

# Merge user log with activity log
merged_data = user_log.merge(activity_log, on='User_ID', how='left')

# Filter for specific components of interest
target_components = ['Quiz', 'Lecture', 'Assignment', 'Attendance', 'Survey']
filtered_data = merged_data[merged_data['Component'].isin(target_components)]

# Add Month column
filtered_data['Month'] = filtered_data['Date'].dt.to_period('M')

# Calculate statistics per month for each component
monthly_stats = {}
for component in target_components:
    comp_data = filtered_data[filtered_data['Component'] == component]
    
    # Group by month and count interactions
    monthly_interactions = comp_data.groupby('Month').size()
    
    # Calculate statistics
    monthly_stats[component] = {
        'mean': monthly_interactions.mean(),
        'median': monthly_interactions.median(),
        'mode': monthly_interactions.mode().values[0] if len(monthly_interactions.mode()) > 0 else np.nan
    }

# Prepare output for monthly statistics
monthly_stats_df = pd.DataFrame.from_dict(monthly_stats, orient='index')
monthly_stats_df.to_csv('monthly_component_statistics.csv')
print("Monthly Component Statistics:")
print(monthly_stats_df)

# Correlation Analysis
# Create interaction count matrix
interaction_matrix = filtered_data.pivot_table(
    index='User_ID', 
    columns='Component', 
    aggfunc='size', 
    fill_value=0
)

# Calculate correlation matrix
correlation_matrix = interaction_matrix.corr()

# Visualize correlation using heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation of User Interactions Across Components')
plt.tight_layout()
# plt.savefig('component_interaction_correlation.png')
# plt.close()
plt.show()

# Chi-square test for independence between User_ID and Component
contingency_table = pd.crosstab(filtered_data['User_ID'], filtered_data['Component'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

print("\nChi-square Test for Independence:")
print(f"Chi-square statistic: {chi2}")
print(f"p-value: {p_value}")

# Prepare final processed data
pivoted_data = filtered_data.groupby(['User_ID', 'Month', 'Component']).size().reset_index(name='Interaction_Count')
pivoted_data.to_csv('processed_user_interactions.csv', index=False)


# Execute the processing
processed_data = process_csv_files()
print("\nProcessed data sample:")
print(processed_data.head())
print("\nProcessed data saved to 'processed_user_interactions.csv'")