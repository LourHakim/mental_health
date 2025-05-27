## Data Retrieval

- Youth Risk Behavior Survey (YRBS),  (YRBSS)   
    *   The CSV files were manually downloaded from https://www.cdc.gov/yrbs/data/index.html 
    *   Retreval date:17-4-2025. No automated retrieval script was used.
    *   This data is relevent to 2023 as per the website
    *   Navigate to: Combined High School > 2023 > Access > District (ZIP)
- GDP by state
    *   The CSV file was manually downloaded from https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas 
    *   Retreval date: 18-4-2025. No automated retrieval script was used.
    *   This data is relevent to 2023 as per the website
- Mean income and employment rate by state 
    *   The CSV files were manually downloaded from: https://data.census.gov/advanced
    *   This data is relevent to 2023 as per the website
    *   Retreval date: 18-4-2025.No automated retrieval script was used.
    *   filtered by: 
            state
            employment
            filter by employment and labor force status
            DP03 | Selected Economic Characteristics

# Mental Health Risk Factors in U.S. High School Students (YRBS 2023)

This project investigates behavioral, demographic, and socioeconomic factors associated with mental health outcomes among U.S. high school students. The analysis uses data from the 2023 Youth Risk Behavior Survey (YRBS) and state-level economic indicators.

## Project Overview

Adolescent mental health is a growing public concern. This project aims to identify individual and environmental predictors of poor mental health, including persistent sadness, suicidal thoughts, and frequent emotionally unhealthy days. The findings may support data-driven strategies for early detection and prevention.

## Data Integration

The datasets were merged using the `sitename` variable, which maps each student to their home district and corresponding state. Columns with only one unique value or unrelated metadata were removed. The final dataset includes both student-level and state-level predictors.

## Statistical Population and Variables

- Each row represents a single student from a U.S. high school
- The YRBS uses a stratified, cluster-based sampling design
- Responses are weighted to generalize to the U.S. high school population
- All variables are treated as random variables

### Target Variables

- `Q26`: Felt sad or hopeless (binary)
- `Q27`: Seriously considered suicide (binary)
- `Q84`: Days of poor mental health (ordinal: Never to Always)

### Variable Types

- Categorical: sex, race, grade
- Ordinal: Q84, breakfast frequency
- Numeric: age, BMI, GDP, income
