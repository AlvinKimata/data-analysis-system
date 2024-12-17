### System Design for Advanced Programming Assessment

---

#### **1. Overview**
The system aims to process, analyze, and visualize data from anonymized online activity logs. It includes a user-friendly interface for data manipulation and analysis. The design aligns with the requirements outlined in the assessment brief, leveraging Python libraries and adhering to the constraints specified.

---

#### **2. Architecture**
##### **2.1 Components**
1. **Data Layer**:
   - **Input**: Three CSV files (USER_LOG, ACTIVITY_LOG, COMPONENT_CODES).
   - **Storage**: JSON/XML file or SQLite database for processed data.
   - **Output**: Processed and analyzed data, ready for visualization.

2. **Processing Layer**:
   - **Loading**: Import CSV files into Pandas DataFrames.
   - **Cleaning**: Handle missing values, inconsistencies, and irrelevant components.
   - **Transformation**: Rename columns, merge datasets, and reshape using pivot operations.
   - **Analysis**: Calculate statistics and correlations.

3. **Interface Layer**:
   - **GUI**: Built with Tkinter, providing user interaction for loading, cleaning, and analyzing data.
   - **Visualization**: Graphs and statistics displayed using Seaborn and Matplotlib.

##### **2.2 Workflow**
- **Input**: Load CSV files.
- **Processing**:
  - Clean data (e.g., remove unnecessary components).
  - Transform and reshape data.
  - Analyze data for statistical insights and correlations.
- **Output**: Display results in GUI and provide downloadable files if required.

---

#### **3. Data Flow Diagram (DFD)**

1. **Level 0**
   - Input: CSV Files.
   - Output: Visualizations and statistical insights.

2. **Level 1**
   - Input Data > Data Cleaning > Data Transformation > Data Analysis > Output Data.

---

#### **4. Functional Requirements**
1. **Data Operations**:
   - Load data from CSV files.
   - Translate to JSON/XML/Database.
   - Back up and reload translated data.
   - Perform data cleaning, transformation, and reshaping.

2. **Analysis and Outputs**:
   - Calculate statistics (mean, mode, median).
   - Generate monthly and semester-based reports.
   - Visualize correlations between user interactions and components.

3. **GUI Interactions**:
   - Load initial and prepared datasets.
   - Trigger data transformations and analyses.
   - Display outputs with feedback for user actions.

---

#### **5. Non-Functional Requirements**
- **Usability**: Intuitive GUI with clear feedback mechanisms.
- **Error Handling**: Robust error messages for invalid actions or inputs.
- **Performance**: Efficient handling of up to 152 students' data.
- **Scalability**: Adaptable to similar datasets with the same structure.

---

#### **6. Technical Design**
##### **6.1 Data Layer**
- **Input**:
  - CSV files read into Pandas DataFrames.
- **Storage**:
  - JSON/XML or SQLite database.
  - Backup mechanism triggered at program exit.

##### **6.2 Processing Layer**
- **Cleaning**:
  - Drop rows with missing critical values.
  - Remove components: System, Folder.

  **Pseudocode**:
  ```python
  def clean_data(df):
      # Drop rows with missing critical values
      df = df.dropna(subset=['critical_column'])
      
      # Remove rows where Component is 'System' or 'Folder'
      df = df[~df['Component'].isin(['System', 'Folder'])]
      return df
  ```

- **Transformation**:
  - Rename columns (`User Full Name` to `User_ID`).
  - Merge ACTIVITY_LOG with USER_LOG based on `User_ID`.
  - Pivot table for user interactions per component.

  **Pseudocode**:
  ```python
  def transform_data(user_log, activity_log):
      # Rename column
      user_log.rename(columns={'User Full Name': 'User_ID'}, inplace=True)
      
      # Merge datasets
      merged_df = activity_log.merge(user_log, on='User_ID')
      
      # Pivot table
      pivot_df = merged_df.pivot_table(
          index='User_ID', 
          columns='Component', 
          values='Interactions', 
          aggfunc='sum'
      ).fillna(0)
      return pivot_df
  ```
- **Cleaning**:
  - Drop rows with missing critical values.
  - Remove components: System, Folder.
- **Transformation**:
  - Rename columns (`User Full Name` to `User_ID`).
  - Merge ACTIVITY_LOG with USER_LOG based on `User_ID`.
  - Pivot table for user interactions per component.
- **Analysis**:
  - Compute mean, mode, median for components.
  - Visualize correlations using scatter plots and heatmaps.

##### **6.3 Interface Layer**
- **GUI (Tkinter)**:
  - Buttons for each operation: Load, Clean, Transform, Analyze.
  - Visual outputs embedded in the interface.
  - Logs or status messages for user feedback.

---

#### **7. Tools and Libraries**
- **Python Core**: For data processing and file operations.
- **NumPy**: Statistical analysis.
- **Pandas**: Data manipulation and transformation.
- **Seaborn/Matplotlib**: Graphical visualizations.
- **SQLite**: Data storage (if database option is used).
- **Tkinter**: GUI development.

---

#### **8. Implementation Plan**
1. **Phase 1: Data Layer**
   - Develop data loading and storage functions.
   - Implement cleaning and transformation.

2. **Phase 2: Analysis Layer**
   - Create statistical analysis functions.
   - Develop visualization components.

3. **Phase 3: Interface Layer**
   - Build GUI for interactive operations.
   - Integrate data and analysis layers with GUI.

4. **Phase 4: Testing**
   - Test individual modules.
   - Perform end-to-end testing with sample data.

---

#### **9. Reporting and Documentation**
- Include code snippets and screenshots in the report appendix.
- Document design decisions, challenges, and justifications.
- Reflect on ethical, moral, and legal considerations.

---

