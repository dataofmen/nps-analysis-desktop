# Weighting Methodology: Iterative Proportional Fitting (Raking)

This application uses **Iterative Proportional Fitting (IPF)**, commonly known as **Raking**, to calculate weights for survey data. This method ensures that the weighted sample distribution matches the known population distribution across multiple demographic variables simultaneously.

## Why Raking?

In survey research, the sample collected often does not perfectly reflect the target population due to random sampling error or non-response bias. For example, you might have too many male respondents or too few respondents in their 20s compared to the actual population.

Simple **Cell Weighting** (dividing population % by sample %) works well for a single variable (e.g., just Gender). However, when you need to balance multiple variables (e.g., Gender, Age, Region) simultaneously, dividing the sample into every possible combination (cells) often results in:
1.  **Small or Empty Cells**: Some combinations (e.g., "Male, 20s, Jeju Island") might have zero respondents.
2.  **Unstable Weights**: Extremely high weights for cells with very few respondents.

**Raking** solves this by adjusting weights iteratively for one variable at a time until all distributions converge to the targets. It allows you to balance multiple variables without needing a respondent for every single cross-combination.

## How It Works

The algorithm follows these steps:

1.  **Initialization**: Assign an initial weight of 1.0 to all respondents.
2.  **Iteration**:
    *   **Step 1 (Variable A)**: Adjust weights so the distribution of Variable A matches the population target.
    *   **Step 2 (Variable B)**: Adjust the weights from Step 1 so the distribution of Variable B matches the population target. (This might slightly throw off Variable A).
    *   **Step 3 (Variable C)**: Adjust for Variable C...
3.  **Convergence**: Repeat the iteration process until the distributions for ALL variables match the targets within a very small margin of error (convergence).

## Weighting in This Application

### 1. Global Weighting
When you run a standard analysis, the application calculates a single "Global Weight" for each respondent based on the variables you select (e.g., Gender, Age).
*   **Input**: Survey Data, Population Proportions.
*   **Output**: A 'Weight' column added to your data.
*   **Usage**: All subsequent metrics (NPS, Top Box) are calculated using this global weight.

### 2. Subset Weighting (Group By Analysis)
When you analyze data by a specific group (e.g., "Analyze by Region"), the global weight might not be appropriate because the demographic distribution *within* that region might differ from the national average.

To address this, the application supports **Subset Weighting**:
*   The data is filtered for each group (e.g., just "Seoul" respondents).
*   The Raking algorithm is re-run *only* for that subset.
*   **Dynamic Targets**: The targets for the subset are recalculated based on the population data for that specific group (if provided) or assumed to follow the global structure depending on configuration.
*   **Result**: More accurate analysis for subgroups, as the weights are specifically optimized for that slice of data.

## References
*   [Iterative Proportional Fitting - Wikipedia](https://en.wikipedia.org/wiki/Iterative_proportional_fitting)
*   [Raking Survey Data (Pew Research Center)](https://www.pewresearch.org/methods/2018/01/26/how-different-weighting-methods-work/)
