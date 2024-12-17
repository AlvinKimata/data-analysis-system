#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[4]:


import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency


# In[5]:


# Read CSV files
activity_log = pd.read_csv('../input/data-analysis-dataset/ACTIVITY_LOG.csv')
component_codes = pd.read_csv('../input/data-analysis-dataset/COMPONENT_CODES.csv')
user_log = pd.read_csv('../input/data-analysis-dataset/USER_LOG.csv')

# Print initial row counts for debugging
print("Initial row counts:")
print(f"User Log rows: {len(user_log)}")
print(f"Activity Log rows: {len(activity_log)}")

# Check for duplicate combinations
print("\nChecking for duplicate combinations:")
print("User Log unique User IDs:", user_log['User Full Name *Anonymized'].nunique())
print("Activity Log unique User IDs:", activity_log['User Full Name *Anonymized'].nunique())

# Rename columns
activity_log = activity_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})
user_log = user_log.rename(columns={'User Full Name *Anonymized': 'User_ID'})

# Remove System and Folder components
activity_log = activity_log[~activity_log['Component'].isin(['System', 'Folder'])]

# Convert date columns to datetime, handling the time information
user_log['Date'] = pd.to_datetime(user_log['Date'].str.split().str[0], format='%d/%m/%Y')

# Ensure unique combinations in activity log
activity_log = activity_log.drop_duplicates(subset=['User_ID', 'Component', 'Action', 'Target'])

# Ensure unique combinations in user log
user_log = user_log.drop_duplicates(subset = ['Date', 'Time', 'User_ID'])


# In[6]:


# Print row counts after deduplication
print(f"\nActivity Log rows after deduplication: {len(activity_log)}")

# Merge user log with activity log
# Use left merge to keep all user log entries
merged_data = user_log.merge(activity_log, on='User_ID', how='left')

# Print merged data information
print(f"\nMerged data rows: {len(merged_data)}")


# In[7]:


merged_data.head(2)


# In[8]:


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


# In[29]:


user_component_interactions = merged_data.groupby(['User_ID', 'Component', 'Month']).size().reset_index(name='User_Component_Interactions')
user_component_interactions


# In[9]:


pivoted_data.head()


# In[20]:


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
    print(monthly_interactions)
    
# #     # Store the statistics for each month
# #     monthly_stats[component] = monthly_interactions

# # # Convert monthly statistics to DataFrame
# # monthly_stats_df = pd.DataFrame.from_dict(monthly_stats).fillna(0)
# # monthly_stats_df


# In[21]:


# Filter for specific components of interest
target_components = ['Quiz', 'Lecture', 'Assignment', 'Attendence', 'Survey']
filtered_data = merged_data[merged_data['Component'].isin(target_components)]

# Add Month column
filtered_data['Month'] = filtered_data['Date'].dt.to_period('M')

# Calculate statistics per month for each component
semester_stats = {}
for component in target_components:
    comp_data = filtered_data[filtered_data['Component'] == component]
    
    # Group by month and count interactions
    monthly_interactions = comp_data.groupby('Month').size()
    
    # Calculate statistics
    semester_stats[component] = {
        'mean': monthly_interactions.mean(),
        'median': monthly_interactions.median(),
        'mode': monthly_interactions.mode().values[0] if len(monthly_interactions.mode()) > 0 else np.nan
    }
    # print(f"Monthly_stats {monthly_stats}")

# # Prepare output for monthly statistics
semester_stats_df = pd.DataFrame.from_dict(semester_stats, orient='index')
print("Smester Statistics:")
print(semester_stats_df)


# In[28]:


import numpy as np
import pandas as pd

# Filter for specific components of interest
target_components = ['Quiz', 'Lecture', 'Assignment', 'Attendence', 'Survey']
filtered_data = merged_data[merged_data['Component'].isin(target_components)]

# Add Month column
filtered_data['Month'] = filtered_data['Date'].dt.to_period('M')

# Initialize a dictionary to store metrics for each month and component
monthly_stats = {}

# Iterate through the components
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

# Convert the nested dictionary into a DataFrame for better readability
flattened_stats = []
for month, components in monthly_stats.items():
    for component, metrics in components.items():
        flattened_stats.append({'Month': month, 'Component': component, **metrics})

# Create a DataFrame
monthly_stats_df = pd.DataFrame(flattened_stats)

# Print and save the monthly statistics DataFrame
print("Monthly Statistics:")
print(monthly_stats_df)
monthly_stats_df.to_csv('monthly_component_statistics.csv', index=False)


# In[27]:


# Components of interest
target_components = ['Assignment', 'Quiz', 'Lecture', 'Book', 'Project', 'Course']
filtered_data = merged_data[merged_data['Component'].isin(target_components)]

# Create a pivot table of interaction counts between User_ID and Component
interaction_matrix = filtered_data.pivot_table(
    index='User_ID', 
    columns='Component', 
    aggfunc='size', 
    fill_value=0
)

# Calculate correlation matrix
correlation_matrix = interaction_matrix.corr()

# Visualize correlation using a heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(
    correlation_matrix, 
    annot=True, 
    cmap='seismic', 
    center=0, 
    cbar=True
)
plt.title('Correlation of User Interactions Across Components')
plt.tight_layout()
plt.savefig('component_correlation_heatmap.png')
plt.show()

# Chi-square test for independence between User_ID and Component
contingency_table = pd.crosstab(filtered_data['User_ID'], filtered_data['Component'])
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

# Output chi-square results
print("\nChi-square Test for Independence:")
print(f"Chi-square statistic: {chi2}")
print(f"p-value: {p_value}")
print(f"Degrees of freedom: {dof}")


# In[31]