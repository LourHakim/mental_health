# -*- coding: utf-8 -*-
"""MentalHealth.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TrETkWHPxFgA63sqZoVT296GI1wTT2yD
"""

!pip install missingno

import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn as skl
import missingno as msno
from scipy.stats import chi2_contingency
import scipy.stats as stats
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error

"""## first session"""

# Assuming mentalhealth.csv and gdp.csv are in the current working directory
# If they are in a different location, provide the full path
try:
    mental_health_df = pd.read_csv('mentalhealth.csv')
    gdp_df = pd.read_csv('gdp.csv')
    print("Files loaded successfully.")
    print("Mental Health DataFrame:")
    print(mental_health_df)
    print("\nGDP DataFrame:")
    print(gdp_df.head())  # Display the first few rows
except FileNotFoundError:
    print("Error: One or both of the files were not found.  Please ensure they are in the correct location.")
except Exception as e:
    print(f"An error occurred: {e}")

"""### Initial Data Cleaning"""

for col in mental_health_df.columns:
  if mental_health_df[col].nunique() <=1:
    print(col, mental_health_df[col].nunique())

columns_to_drop = [col for col in mental_health_df.columns if mental_health_df[col].nunique() <= 1]
mental_health_df = mental_health_df.drop(columns=columns_to_drop)
mental_health_df = mental_health_df.drop(columns=['sitecode'])
mental_health_df

# Count original rows
original_row_count = mental_health_df.shape[0]

# Add temporary column
mental_health_df['missing_values_count'] = mental_health_df.isnull().sum(axis=1)

# Drop rows with too many missing values
mental_health_df = mental_health_df[mental_health_df['missing_values_count'] <= 60]

# Drop helper column
mental_health_df.drop(columns=['missing_values_count'], inplace=True)

# Print results
print(f"Rows dropped: {original_row_count - mental_health_df.shape[0]}")
print(f"Remaining rows: {mental_health_df.shape[0]}")

msno.matrix(mental_health_df)

numeric_columns = ['stheight', 'stweight', 'bmi', 'bmipct']
mental_health_df[numeric_columns].describe()

# Get all other columns as categorical (excluding numeric ones)
categorical_columns = [col for col in mental_health_df.columns if col not in numeric_columns]

# Create a summary DataFrame for categorical variables
cat_info = []

for col in categorical_columns:
    cat_info.append([
        col,
        mental_health_df[col].nunique(dropna=False),
        mental_health_df[col].unique(),
        mental_health_df[col].dtype
    ])

df_categorical_info = pd.DataFrame(cat_info, columns=['column_name', 'unique_count', 'unique_values', 'data_type'])

# Show the summary table
print("===== Categorical Variable Summary =====")
print(df_categorical_info)

# Step 3: Print value counts for each categorical variable
print("\n===== Value Counts for Each Categorical Variable =====")
for col in categorical_columns:
    print(f"\n--- {col} ---")
    print(mental_health_df[col].value_counts(dropna=False))

gdp_df

gdp_df.columns

gdp_df_edited = gdp_df.drop(columns=[
       'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3',  'Unnamed: 5',
       'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9'])

gdp_df_edited = gdp_df_edited[5:]
gdp_df_edited

# prompt: rename first column to 'state' second column to 'gdp 2023' in gdp_df_edited

gdp_df_edited = gdp_df_edited.rename(columns={gdp_df_edited.columns[0]:'state', gdp_df_edited.columns[1]:'gdp 2023'})
gdp_df_edited

mental_health_df['sitename'].unique()

cities_states = {
    "Albuquerque": "New Mexico",
    "Chicago": "Illinois",
    "Los Angeles": "California",
    "New York City": "New York",
    "Oakland": "California",
    "Philadelphia": "Pennsylvania",
    "Portland": "Oregon",
    "San Diego": "California",
    "Seattle": "Washington",
    "Spartanburg County": "South Carolina"
}

df_mental_health_with_gdp = mental_health_df.copy()

gdp_df_edited

df_mental_health_with_gdp['state'] = df_mental_health_with_gdp['sitename'].apply(lambda x: cities_states[x.split(', ')[0]] if x.split(', ')[0] in cities_states else None)

df_mental_health_with_gdp['gdp 2023'] = df_mental_health_with_gdp['state'].apply(lambda x: gdp_df_edited[gdp_df_edited['state'] == x]['gdp 2023'].values[0] if x is not None else None)

df_mental_health_with_gdp.to_csv('mental_health_with_gdp.csv', index=False)

df_mental_health_with_gdp['gdp 2023']

"""## second session"""

df = pd.read_csv('mental_health_with_gdp.csv')

df.head()

col_info=[]

for col in df.columns:
  col_info.append([col,df[col].nunique(),df[col].unique(),df[col].dtype])

df_cols = pd.DataFrame(col_info, columns=['column_name','unique_num','unique_values','data_type'])
df_cols.head()

df_cols.sort_values(by='unique_num', ascending=False)

df_states= pd.read_csv('joined_state_data.csv')

df_states

df = df.merge(df_states, how='left', on='state')
df.to_csv('mental_health_with_socioeconomic_indicators.csv', index=False)
df

"""## Handling Missing Data"""

df = pd.read_csv('mental_health_with_socioeconomic_indicators.csv')
plt.figure(figsize=(12, 6))
sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
plt.title("Missing Values Heatmap")
plt.show()

missing_summary = df.isnull().sum()
missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)
print(missing_summary)

# Set threshold for high missingness (70%)
threshold = 0.70

# Calculate fraction of missing values per column
missing_fraction = df.isnull().mean()

# Identify columns exceeding the threshold
high_missing_cols = missing_fraction[missing_fraction > threshold].index.tolist()

# Print summary
print(f"Columns with >{int(threshold * 100)}% missing values:")
print(high_missing_cols)

# Drop them from the DataFrame
df.drop(columns=high_missing_cols, inplace=True)

print(f"\nDropped {len(high_missing_cols)} columns due to high missingness.")
print(f"Remaining columns: {df.shape[1]}")

missing_summary = df.isnull().sum()
missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)
print(missing_summary)

# Step 1: Define numeric columns
numeric_columns = ['stheight', 'stweight', 'bmi', 'bmipct']

# Step 2: Identify categorical columns (everything else)
categorical_columns = [col for col in df.columns if col not in numeric_columns]

# Step 3: Fill missing values in categorical columns with "-1"
for col in categorical_columns:
    if df[col].isnull().any():
        df[col] = df[col].fillna(-1)

# Fill each with its mean
for col in numeric_columns:
    mean_value = df[col].mean()
    df[col] = df[col].fillna(mean_value)
    print(f"Filled missing values in '{col}' with mean: {mean_value:.2f}")

missing_summary = df.isnull().sum()
missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)
print(missing_summary)

df.to_csv('mental_health_full.csv', index=False)

"""## Third session"""

full_df = pd.read_csv('mental_health_full.csv')
full_df

# --- Basic Info ---
print("Shape of dataset:", full_df.shape)
print("\nInfo:")
print(full_df.info())
print("\nSummary statistics:")
print(full_df.describe())

# --- Missing Values ---
print("\nMissing values (sorted):")
missing_percent = full_df.isnull().mean() * 100
print(missing_percent[missing_percent > 0].sort_values(ascending=False))

# --- Mapping dictionaries for key categorical variables ---
mapping_dicts = {
    'q26': {1: 'Yes', 2: 'No'},
    'q27': {1: 'Yes', 2: 'No'},
    'q84': {
        1: 'Never',
        2: 'Rarely',
        3: 'Sometimes',
        4: 'Most of the time',
        5: 'Always'
    },
    'age': {
        1: '12 yo or younger',
        2: '13 yo',
        3: '14 yo',
        4: '15 yo',
        5: '16 yo',
        6: '17 yo',
        7: '18 yo or older'
    },
    'sex': {
        1: 'Female',
        2: 'Male'
    },
    'grade': {
        1: '9th grade',
        2: '10th grade',
        3: '11th grade',
        4: '12th grade',
        5: 'Ungraded or other grade'
    },
    'race4': {
        1: 'White',
        2: 'Black or African American',
        3: 'Hispanic/Latino',
        4: 'All Other Races'
    },
    'race7': {
        1: 'American Indian/Alaska Native',
        2: 'Asian',
        3: 'Black or African American',
        4: 'Hispanic/Latino',
        5: 'Native Hawaiian/Other Pacific Islander',
        6: 'White',
        7: 'Multiple Races (Non-Hispanic)'
    },
    'q24': {
        1: 'Yes',
        2: 'No'
    },
      'q75': {
        1: '0 days',
        2: '1 day',
        3: '2 days',
        4: '3 days',
        5: '4 days',
        6: '5 days',
        7: '6 days',
        8: '7 days'
    }
}

# --- Targets Distribution ---
import matplotlib.pyplot as plt
target_vars = ['q26', 'q27', 'q84']

for target in target_vars:
    if target in full_df.columns:
        if target in mapping_dicts:
            mapped_series = full_df[target].map(mapping_dicts[target])
        else:
            mapped_series = full_df[target]

        if mapped_series.dropna().shape[0] > 0:
            plt.figure(figsize=(5, 4))
            mapped_series.value_counts(normalize=True).sort_index().plot(kind='bar', color='#f4169b')
            plt.title(f'Distribution of {target}')
            plt.xlabel('Answer')
            plt.ylabel('Proportion')
            plt.xticks(rotation=45)
            plt.grid(axis='y')
            plt.show()
        else:
            print(f"Warning: {target} exists but has no non-missing values. Skipping plot.")
    else:
        print(f"Warning: {target} not found in dataset. Skipping plot.")

# --- Additional Categorical Variables Distribution ---
categorical_vars = ['sex', 'race4', 'race7', 'age', 'grade', 'q24', 'q75']

for var in categorical_vars:
    if var in full_df.columns:
        if var in mapping_dicts:
            mapped_series = full_df[var].map(mapping_dicts[var])
        else:
            mapped_series = full_df[var]

        if mapped_series.dropna().shape[0] > 0:
            plt.figure(figsize=(6, 4))
            mapped_series.value_counts(normalize=True).sort_index().plot(kind='bar', color='#f7bf0a')
            plt.title(f'Distribution of {var}')
            plt.xlabel('Answer')
            plt.ylabel('Proportion')
            plt.xticks(rotation=90)
            plt.grid(axis='y')
            plt.show()
        else:
            print(f"Warning: {var} exists but has no non-missing values. Skipping plot.")
    else:
        print(f"Warning: {var} not found in dataset. Skipping plot.")

import matplotlib.pyplot as plt

# Clean the numeric columns if they contain commas or percentage signs (only run once)
full_df['gdp 2023'] = full_df['gdp 2023'].astype(str).str.replace(',', '').astype(float)
full_df['Unemployment Rate(Percent)'] = full_df['Unemployment Rate(Percent)'].astype(str).str.replace('%', '').astype(float)
full_df['Mean household income (dollars)'] = full_df['Mean household income (dollars)'].astype(str).str.replace(',', '').astype(float)

# Columns to plot
columns_to_plot = ['gdp 2023', 'Unemployment Rate(Percent)', 'Mean household income (dollars)']

# Plot each variable
for column in columns_to_plot:
    plt.figure(figsize=(12, 6))
    full_df.groupby('state')[column].mean().sort_values().plot(kind='bar', color='#7ac590')
    plt.title(f"{column} by State")
    plt.xlabel("State")
    plt.ylabel(column)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.grid(axis='y')
    plt.show()


# --- Histogram for BMI ---
if 'bmi' in full_df.columns:
    plt.figure(figsize=(6, 4))
    plt.hist(full_df['bmi'].dropna(), bins=30, color='#ffa8d3')
    plt.title('Distribution of BMI')
    plt.xlabel('BMI')
    plt.ylabel('Frequency')
    plt.grid(axis='y')
    plt.show()
else:
    print("Feature 'bmi' not found.")

"""## Outliers"""

# --- 1. Visualize BMI with a boxplot ---
plt.figure(figsize=(6, 4))
sns.boxplot(data=full_df, x='bmi', color='#feb312')
plt.title('Boxplot of BMI')
plt.grid(axis='x')
plt.tight_layout()
plt.show()

# --- 2. Detect outliers using IQR ---
Q1 = full_df['bmi'].quantile(0.25)
Q3 = full_df['bmi'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Boolean mask of outliers
bmi_outliers = (full_df['bmi'] < lower_bound) | (full_df['bmi'] > upper_bound)

# Print outlier count
outlier_count = bmi_outliers.sum()
print(f"Number of BMI outliers: {outlier_count} ({round(100 * outlier_count / len(full_df), 2)}%)")

# Prepare contingency table for q27 by BMI outlier status
# First, re-calculate IQR outlier flag for BMI
Q1 = full_df['bmi'].quantile(0.25)
Q3 = full_df['bmi'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
full_df['bmi_outlier'] = full_df['bmi'].apply(lambda x: 'Outlier' if x < lower_bound or x > upper_bound else 'Normal')

# Prepare the contingency table (drop missing q27 values)
contingency = pd.crosstab(full_df['bmi_outlier'], full_df['q27'])

# Run chi-square test
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"Chi² = {chi2:.2f}")
print(f"p-value = {p:.4f}")
print("Result: Significant association" if p < 0.05 else "Result: Not significant")

# Prepare data
suicide_map = {1: 'Yes', 2: 'No'}
temp = full_df[['bmi_outlier', 'q27']].copy()
temp['suicidal'] = temp['q27'].map(suicide_map)
temp.dropna(inplace=True)

# Calculate proportions
suicide_rate = pd.crosstab(temp['bmi_outlier'], temp['suicidal'], normalize='index')

colors = ['#82d49a', '#f5badb']

# Plot
ax = suicide_rate.plot(kind='bar', stacked=True, figsize=(8, 5), color=colors)
plt.title('Suicidal Thoughts (q27) by BMI Outlier Status')
plt.xlabel('BMI Category')
plt.ylabel('Proportion')
plt.ylim(0, 1)
plt.grid(axis='y')
plt.tight_layout()

# Add percentage labels
for i, bars in enumerate(ax.containers):
    for bar in bars:
        height = bar.get_height()
        if height > 0.01:  # skip very small bars
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + height / 2,
                f"{height:.1%}",
                ha='center',
                va='center',
                fontsize=10,
                color='black'
            )

plt.show()

"""## Bivariate/Multivariate Analysis"""

# Rewriting the entire block using 'full_df' instead of 'df'

# --- Mapping dictionary ---
smoking_drinking_mapping = {
    1: '0 days',
    2: '1-2 days',
    3: '3-5 days',
    4: '6-9 days',
    5: '10-19 days',
    6: '20-29 days',
    7: 'All 30 days'
}

# --- Map temporarily ---
q33_mapped = full_df['q33'].map(smoking_drinking_mapping)
q42_mapped = full_df['q42'].map(smoking_drinking_mapping)

# --- Calculate counts ---
smoking_counts = q33_mapped.value_counts().reindex(smoking_drinking_mapping.values(), fill_value=0)
alcohol_counts = q42_mapped.value_counts().reindex(smoking_drinking_mapping.values(), fill_value=0)

# --- Create dataframe ---
counts_df = pd.DataFrame({
    'Smoking': smoking_counts,
    'Alcohol': alcohol_counts
}, index=smoking_drinking_mapping.values())

colors1 = ['#fba9d6', '#fbbe5a']

# --- Plot Grouped Bar Plot ---
counts_df.plot(kind='bar', figsize=(10,6), color=colors1)
plt.title('Comparison of Smoking and Alcohol Use (Past 30 Days)')
plt.xlabel('Days of Use')
plt.ylabel('Number of Students')
plt.xticks(rotation=45)
plt.legend(title='Substance')
plt.grid(axis='y')
plt.show()

# --- Define mappings ---
social_media_mapping = {
    1: 'I do not use',
    2: 'Few times/month',
    3: 'Once/week',
    4: 'Few times/week',
    5: 'Once/day',
    6: 'Several times/day',
    7: 'Once/hour',
    8: 'More than once/hour'
}

sleep_mapping = {
    1: '4 or less',
    2: '5',
    3: '6',
    4: '7',
    5: '8',
    6: '9',
    7: '10+'
}

# --- Temporary dataframe ---
df_temp = full_df[['q80', 'q85']].copy()
df_temp['social_media'] = df_temp['q80'].map(social_media_mapping)
df_temp['sleep'] = df_temp['q85'].map(sleep_mapping)
df_temp.dropna(inplace=True)

# --- Define proper category orders ---
social_order = list(social_media_mapping.values())
sleep_order = list(sleep_mapping.values())

# --- Create cross-tabulation ---
cross_tab = pd.crosstab(df_temp['social_media'], df_temp['sleep'], normalize='index')
cross_tab = cross_tab.reindex(index=social_order, columns=sleep_order)

# --- Plot grouped bar chart ---
cross_tab.plot(kind='bar', figsize=(14,6))
plt.title('Sleep Duration Distribution by Social Media Use Frequency')
plt.xlabel('Social Media Use Frequency')
plt.ylabel('Proportion of Students')
plt.xticks(rotation=45)
plt.legend(title='Sleep Duration', bbox_to_anchor=(1.05, 1))
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# --- Mapping dictionaries ---
grades_mapping = {
    1: "Mostly A's",
    2: "Mostly B's",
    3: "Mostly C's",
    4: "Mostly D's",
    5: "Mostly F's",
    6: "None of these",
    7: "Not sure"
}

housing_mapping = {
    1: "Parent/Guardian's Home",
    2: "Someone else's home (unstable)",
    3: "Shelter/Emergency Housing",
    4: "Motel or Hotel",
    5: "Car/Park/Public Place",
    6: "No usual place",
    7: "Somewhere else"
}

# --- Map variables ---
df_temp = full_df[['q87', 'q86']].copy()
df_temp['grades'] = df_temp['q87'].map(grades_mapping)
df_temp['housing'] = df_temp['q86'].map(housing_mapping)
df_temp.dropna(inplace=True)

# --- Define display order ---
grade_order = list(grades_mapping.values())
housing_order = list(housing_mapping.values())

# --- Cross-tabulation normalized by row ---
cross_tab = pd.crosstab(df_temp['housing'], df_temp['grades'], normalize='index')
cross_tab = cross_tab[grade_order]
cross_tab = cross_tab.reindex(housing_order)

# --- Plot ---
cross_tab.plot(kind='bar', figsize=(14,6))
plt.title('Grades Distribution by Usual Sleeping Location (Unstable Housing)')
plt.xlabel('Usual Sleeping Location')
plt.ylabel('Proportion of Students')
plt.xticks(rotation=30, ha='right')
plt.legend(title='Grades', bbox_to_anchor=(1.05, 1))
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# --- Mapping ---
bullying_mapping = {1: 'Yes', 2: 'No'}
sadness_mapping = {1: 'Yes', 2: 'No'}

# --- Prepare Data ---
df_temp = full_df[['q24', 'q26']].copy()
df_temp['bullied'] = df_temp['q24'].map(bullying_mapping)
df_temp['sad'] = df_temp['q26'].map(sadness_mapping)
df_temp.dropna(inplace=True)

# --- Count and Normalize ---
grouped = df_temp.groupby(['bullied', 'sad']).size().reset_index(name='count')
grouped['proportion'] = grouped.groupby('bullied')['count'].transform(lambda x: x / x.sum())

# --- Plot Grouped Bar Chart ---
plt.figure(figsize=(8, 6))
sns.barplot(data=grouped, x='bullied', y='proportion', hue='sad', palette='Set2')
plt.title('Proportion of Students Feeling Sad by Bullying Status')
plt.xlabel('Bullied at School')
plt.ylabel('Proportion of Students')
plt.legend(title='Felt Sad or Hopeless (2+ weeks)')
plt.ylim(0, 1)
plt.grid(axis='y')
plt.tight_layout()
plt.show()


# Step 1: Filter out rows with missing or invalid q26/state
filtered_df = full_df[(full_df['q26'].isin([1, 2])) & (full_df['state'].notnull())]

# Step 2: Calculate proportion of "Yes" answers per state
yes_proportion = (
    filtered_df.groupby('state')['q26']
    .apply(lambda x: (x == 1).mean())
    .sort_values()
)

# Step 3: Plot the result
plt.figure(figsize=(12, 6))
yes_proportion.plot(kind='bar', color='#95cd98')
plt.title('Proportion of Students Who Answered "Yes" to q26 (Sadness) by State')
plt.xlabel('State')
plt.ylabel('Proportion Answered Yes')
plt.xticks(rotation=90)
plt.ylim(0, 1)
plt.grid(axis='y')
plt.tight_layout()
plt.show()

"""## Fifth session"""

# Define predictors and target
predictors = ['q24', 'sex', 'race4', 'q15', 'q16', 'q18']
target = 'q26'  # Feeling sad or hopeless

# Human-readable labels for the variables
variable_labels = {
    'q24': 'Bullied at School',
    'sex': 'Sex',
    'race4': 'Race (4 Categories)',
    'q15': 'Threatened at School',
    'q16': 'Physical Fighting',
    'q18': 'Saw Violence in Neighborhood',
    'q26': 'Felt Sad or Hopeless'
}

# Drop rows with missing values
full_df_subset = full_df[predictors + [target]].dropna()

# Function to calculate Cramer's V
def cramers_v(confusion_matrix):
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    return np.sqrt(phi2 / min(k - 1, r - 1))

# Run chi-square tests and calculate Cramer's V
results = []
for predictor in predictors:
    contingency = pd.crosstab(full_df_subset[predictor], full_df_subset[target])
    chi2, p, dof, expected = chi2_contingency(contingency)
    v = cramers_v(contingency)
    results.append({
        'Predictor': variable_labels[predictor],
        'Target': variable_labels[target],
        'Chi2 Statistic': round(chi2, 2),
        'p-value': round(p, 5),
        'Cramer\'s V': round(v, 3),
        'Significant (p < 0.05)': 'Yes' if p < 0.05 else 'No'
    })

# Create and show the result DataFrame sorted by p-value
chi2_results_df = pd.DataFrame(results).sort_values(by='p-value')
chi2_results_df

# Define predictor list
predictors = ['q24', 'sex', 'race4', 'q15', 'q16', 'q18']

# Human-readable labels for each variable
variable_labels = {
    'q24': 'Bullied at School',
    'sex': 'Sex',
    'race4': 'Race (4 Categories)',
    'q15': 'Threatened at School',
    'q16': 'Physical Fighting',
    'q18': 'Saw Violence in Neighborhood'
}

# Function to calculate Cramer's V
def cramers_v(confusion_matrix):
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    return np.sqrt(phi2 / min(k - 1, r - 1))

# Generate all unique predictor pairs
predictor_pairs = list(combinations(predictors, 2))

# Calculate Cramer's V for each pair
v_results = []
for var1, var2 in predictor_pairs:
    sub_df = full_df[[var1, var2]].dropna()
    contingency = pd.crosstab(sub_df[var1], sub_df[var2])
    v = cramers_v(contingency)
    v_results.append({
        'Variable 1': variable_labels[var1],
        'Variable 2': variable_labels[var2],
        "Cramer's V": round(v, 3)
    })

# Show results as a DataFrame
cramers_v_df = pd.DataFrame(v_results).sort_values(by="Cramer's V", ascending=False)
cramers_v_df

"""## Simple Predictive Baseline"""

# 1. Constant Baseline

# --- Define target and drop non-predictive columns ---
target = 'q26'
exclude = ['q27', 'q84']
X = full_df.drop(columns=[target] + exclude)
y = full_df[target]

# --- One-hot encode categorical variables ---
X_encoded = pd.get_dummies(X, drop_first=True)

# --- Train/test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.3, random_state=42, stratify=y
)

# --- Constant baseline: always predict most frequent class ---
dummy = DummyClassifier(strategy='most_frequent')
dummy.fit(X_train, y_train)

# --- Predict on train and test sets ---
y_train_pred = dummy.predict(X_train)
y_test_pred = dummy.predict(X_test)

# --- Evaluation ---
print("Constant Baseline Results:")
print("Train Accuracy:", accuracy_score(y_train, y_train_pred))
print("Test Accuracy:", accuracy_score(y_test, y_test_pred))

# 2. Univariate Logistic Regression (One Predictor Only)

# Step 1: Filter only valid q26 values (1 = Yes, 2 = No)
df_uni = full_df[full_df['q26'].isin([1, 2])].copy()

# Step 2: Make target binary (1 = sadness, 0 = no sadness)
df_uni['sad'] = df_uni['q26'].map({1: 1, 2: 0})

# Step 3: Use q24 (bullied at school) as predictor, also binary encode it
df_uni['bullied'] = df_uni['q24'].map({1: 1, 2: 0})  # 1 = bullied, 0 = not bullied

# Step 4: Drop rows with NaNs (just in case)
df_uni = df_uni.dropna(subset=['sad', 'bullied'])

# Step 5: Prepare X and y
X = df_uni[['bullied']]
y = df_uni['sad']

# Step 6: Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Step 7: Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Step 8: Predictions
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# Step 9: Evaluate
print("Train Accuracy:", accuracy_score(y_train, y_train_pred))
print("Test Accuracy:", accuracy_score(y_test, y_test_pred))

test_mse = mean_squared_error(y_test, y_test_pred)
print("Test MSE:", test_mse)

# Labeled confusion matrix
cm = confusion_matrix(y_test, y_test_pred, labels=[0, 1])
cm_df = pd.DataFrame(cm,
                     index=["Actual 0 (No Sadness)", "Actual 1 (Yes Sadness)"],
                     columns=["Predicted 0 (No Sadness)", "Predicted 1 (Yes Sadness)"])
print("\nConfusion Matrix (Test):\n", cm_df)

"""## Sparse Logistic Regression"""

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, mean_squared_error
import pandas as pd

# Step 1: Filter and prepare dataset
df_sparse = full_df[full_df['q26'].isin([1, 2])].copy()
df_sparse['target'] = df_sparse['q26'].map({1: 1, 2: 0})  # Binary: 1 = sad, 0 = not sad

# Step 2: Drop unwanted columns
X = df_sparse.drop(columns=['q26', 'q27', 'q84', 'target', 'state', 'sitename', 'q30', 'q29', 'q28'])
y = df_sparse['target']

# Step 3: Rename variable names to human-readable labels
column_renames = {
    'gdp 2023': "GDP per state (2023)",
    'Mean household income (dollars)': "Mean household income",
    'Unemployment Rate(Percent)': "Unemployment rate (%)",
    'sexpart': "Sex of sexual contact(s)",
    'q18': "Witnessed physical attack in neighborhood",
    'sexpart2': "Collapsed sex of sexual contact(s)",
    'q23': "Felt unfair treatment at school due to race/ethnicity",
    'q24': "Bullied on school property (past 12 months)",
    'q85': "Hours of sleep on school night",
    'sex': "Sex",
    'qclose2people': "Feel close to people at school",
    'transg': "Transgender identity",
    'q75': "Days ate breakfast (past 7 days)",
    'sextrans': "Sexual and gender identity",
    'q14': "Missed school due to feeling unsafe (past 30 days)",
    'q49': "Non-prescribed pain med use (lifetime)",
    'q54': "Used ecstasy (lifetime)",
    'q78': "Sports teams played (past 12 months)",
    'q19': "Physically forced to have sex",
    'q8': "Seatbelt use when riding in car"
}
X = X.rename(columns=column_renames)

# Step 4: One-hot encode and scale
X_encoded = pd.get_dummies(X, drop_first=True)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_encoded)

# Step 5: Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

# Step 6: Train sparse logistic regression
model = LogisticRegression(penalty='l1', solver='liblinear', max_iter=1000)
model.fit(X_train, y_train)

# Step 7: Evaluation
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

print("Train Accuracy:", accuracy_score(y_train, y_train_pred))
print("Test Accuracy:", accuracy_score(y_test, y_test_pred))

test_mse = mean_squared_error(y_test, y_test_pred)
print("Test MSE:", test_mse)

# Step 8: Confusion Matrix
cm = confusion_matrix(y_test, y_test_pred, labels=[0, 1])
cm_df = pd.DataFrame(cm,
                     index=["Actual 0 (No Sadness)", "Actual 1 (Yes Sadness)"],
                     columns=["Predicted 0 (No Sadness)", "Predicted 1 (Yes Sadness)"])
print("\nConfusion Matrix (Test):\n", cm_df)

# Step 9: Show non-zero features
coef_df = pd.DataFrame({
    'Feature': X_encoded.columns,
    'Coefficient': model.coef_[0]
})
non_zero = coef_df[coef_df['Coefficient'] != 0].sort_values(by='Coefficient', key=abs, ascending=False)
print("\nTop Non-Zero Coefficients (Selected Features):\n")
print(non_zero.head(20))

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, mean_squared_error
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Filter and prepare dataset
df_sparse = full_df[full_df['q26'].isin([1, 2])].copy()
df_sparse['target'] = df_sparse['q26'].map({1: 1, 2: 0})  # Binary: 1 = sad, 0 = not sad

# Step 2: Drop unwanted columns
X = df_sparse.drop(columns=['q26', 'q27', 'q84', 'target', 'state', 'sitename'])
y = df_sparse['target']

# Step 2.5: Rename variables for clarity
column_renames = {
    'sexpart': "Sex of sexual contact(s)",
    'q18': "Witnessed physical attack in neighborhood",
    'sexpart2': "Collapsed sex of sexual contact(s)",
    'q23': "Felt unfair treatment at school due to race/ethnicity",
    'q24': "Bullied on school property (past 12 months)",
    'q85': "Hours of sleep on school night",
    'sex': "Sex",
    'qclose2people': "Feel close to people at school",
    'transg': "Transgender identity",
    'q75': "Days ate breakfast (past 7 days)",
    'sextrans': "Sexual and gender identity",
    'q14': "Missed school due to feeling unsafe (past 30 days)",
    'q49': "Non-prescribed pain med use (lifetime)",
    'q54': "Used ecstasy (lifetime)",
    'q78': "Sports teams played (past 12 months)",
    'q19': "Physically forced to have sex",
    'q8': "Seatbelt use when riding in car",
    'gdp 2023': "GDP per capita (2023)",
    'Mean household income (dollars)': "Mean household income",
    'Unemployment Rate(Percent)': "Unemployment rate (%)"
}
X = X.rename(columns=column_renames)

# Step 3: One-hot encode and scale
X_encoded = pd.get_dummies(X, drop_first=True)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_encoded)

# Step 4: Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

# Step 5: Train sparse logistic regression
model = LogisticRegression(penalty='l1', solver='liblinear', max_iter=1000)
model.fit(X_train, y_train)

# Step 6: Extract non-zero coefficients
coef_df = pd.DataFrame({
    'Feature': X_encoded.columns,
    'Coefficient': model.coef_[0]
})
non_zero = coef_df[coef_df['Coefficient'] != 0].sort_values(by='Coefficient', key=abs, ascending=False)

# Step 7: Plot top 10 non-zero coefficients
top_features = non_zero.head(10).copy()
top_features = top_features.sort_values(by='Coefficient')  # for horizontal bar plot

plt.figure(figsize=(10, 6))
sns.barplot(x='Coefficient', y='Feature', data=top_features, palette='coolwarm')
plt.title('Top 10 Predictive Features – Sparse Logistic Regression')
plt.xlabel('Coefficient Value')
plt.ylabel('Feature')
plt.axvline(0, color='black', linestyle='--', linewidth=1)
plt.tight_layout()
plt.show()