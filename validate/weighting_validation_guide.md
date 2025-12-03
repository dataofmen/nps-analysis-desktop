# Weighting Validation & Risk Assessment Guide

This document outlines the methodology used to assess the reliability of statistical weighting in the NPS Analysis tool. It provides criteria for identifying "risky" weights and recommends strategies for mitigation.

## 1. Risk Assessment Criteria

We categorize weights into five levels based on their magnitude. High weights indicate that a small number of respondents are representing a large portion of the population, which increases the variance and potential for bias.

| Risk Level | Weight Range | Description | Action |
| :--- | :--- | :--- | :--- |
| **Best** | $w < 1.5$ | Ideal range. Minimal variance inflation. | None required. |
| **Good** | $1.5 \le w < 2.0$ | Acceptable range for most analyses. | None required. |
| **Acceptable** | $2.0 \le w < 3.0$ | High but often unavoidable in granular segmentation. | Monitor if sample size is small ($n < 30$). |
| **Risk** | $3.0 \le w < 5.0$ | **High Risk.** Significant variance inflation. | **Trimming or Merging recommended.** |
| **Critical** | $w \ge 5.0$ | **Critical.** Results are likely unstable and unreliable. | **Must Trim or Merge.** |

## 2. Why High Weights Are Dangerous

### A. Variance Inflation
High weights increase the "Design Effect" (DEFF). A weight of 4.0 means one respondent's opinion counts as much as 4 people. If that one person is an outlier, the entire segment's result is skewed.

### B. Effective Sample Size Reduction
As weights become more unequal, the "Effective Sample Size" ($n_{eff}$) decreases.
$$ n_{eff} = \frac{n}{1 + CV^2} $$
Where $CV$ is the coefficient of variation of the weights. Extreme weights drastically reduce the statistical power of the analysis.

## 3. Recommended Mitigation Strategies

If you encounter segments in the **Risk** or **Critical** categories, consider the following:

### A. Weight Trimming (Capping)
Set a maximum limit for weights.
*   **Recommendation**: Cap weights at **2.5**.
*   **Rationale**: Analysis of typical datasets shows that capping at 2.5 affects less than 5% of segments while significantly reducing the risk of outlier distortion.

### B. Cell Merging
Combine small segments with adjacent ones to increase the sample size ($n$).
*   **Example**: If "Jeju Male 20s" has $n=2$, merge it with "Jeju Male 30s" or "Jeonla Male 20s".
*   **Benefit**: Naturally reduces weights by increasing the sample count relative to the target proportion.

## 4. Implementation in NPS Analysis Tool

The tool automatically calculates the `risk_level` for each segment in the **Weighting Report**.
*   Check the `risk_level` column in the exported CSV.
*   Filter for "Risk" or "Critical" to identify problem areas.
