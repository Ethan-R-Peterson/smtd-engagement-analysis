# EXCEL Lab Student Engagement Analysis

[Client Deliverables Slideshow](url)

A data pipeline and analytics project for understanding how students engage with the EXCEL Lab's career programming using longitudinal records from a FileMaker database and a Qualtrics exit survey.

---

## Project Overview

This project primarily answers three questions:

1. **Who engages, and how deeply?** — What share of students return after a first interaction, and does that vary by class year?
2. **What paths do students take?** — Which experience types tend to lead to others, and where does high-lift sequential behavior appear?
3. **What predicts sustained engagement?** — Which early experiences are most associated with students becoming "highly engaged" over time?

A supplementary Qualtrics analysis links self-reported resource usage to post-graduation outcomes.

---

## Data Sources

| File | Description |
|---|---|
| `Filemaker_Dataset_Copy.csv` | Raw export from the FileMaker participant database |
| `Filemaker_CLEAN.csv` | Cleaned version produced by `cleaning.ipynb`; used by all downstream scripts |
| `Qualtrics.csv` | Survey responses from graduating students |

> **Note:** Data files are not included in this repository. Place them in the project root before running any notebooks or scripts.

---

## Repository Structure

```
.
├── cleaning.ipynb           # Data cleaning and column normalization
├── visualizations.ipynb     # Time-series and volume charts by year/term/major
├── major_analytics.ipynb    # Engagement breakdowns by academic major and class year
├── high_engagement.ipynb    # First-touch analysis and high-engagement predictors
├── engagement_depth.py      # Stacked bar: engagement tier by class year
├── event_transitions.py     # Heatmap: experience transition probabilities and lift
└── qualtrics_analysis.ipynb # Postgrad plans vs. self-reported resource usage
```

---

## Module Details

### `cleaning.ipynb`
Loads the raw FileMaker export, drops low-signal columns, renames fields for clarity, cleans `major_department` to a canonical set of known programs, and parses term strings (e.g. `"FA 2019"`) into separate `year` and `term_season` columns. Outputs `Filemaker_CLEAN.csv`.

### `visualizations.ipynb`
Produces time-series charts of total engagement volume by year and term (WN vs. FA), average engagements per student per year, and major-level breakdowns filtered to programs with significant representation.

### `major_analytics.ipynb`
Breaks down engaged student counts and relative engagement rates by `major_department` and `class_year`. Filters majors below a frequency threshold to keep visuals legible.

### `high_engagement.ipynb`
Defines high engagement as the top quartile of total interactions per student (≥ 75th percentile). Computes three feature sets — raw ever-participated flags, early (first two interactions) flags, and collapsed sequence flags — then calculates lift scores showing how much more likely a student with a given experience type is to become highly engaged.

**Key finding:** Counseling appointments show the highest lift (≈ 4.8×), followed by Funding (≈ 3.1×) and Courses (≈ 2.9×). Even in the first two interactions, an early counseling touch doubles high-engagement likelihood.

Also performs first-touch analysis (what experience type brings students in?) and transition analysis using both raw and collapsed (consecutive-duplicate-removed) sequences.

### `engagement_depth.py`
Produces a stacked bar chart (`engagement_funnel.png`) showing the distribution of engagement depth tiers — one-and-done, 2 interactions, 3–5, and 6+ — broken out by the student's class year at first recorded interaction. Prints an advisor summary table with one-and-done and highly-engaged rates per class year.

### `event_transitions.py`
Builds a transition probability matrix across experience types using collapsed sequences, computes lift over baseline frequency, and renders a heatmap (`transition_heatmap.png`). Cells with lift ≥ 1.5× are outlined in red. Prints a ranked list of high-lift transitions for advisor reference.

### `qualtrics_analysis.ipynb`
Loads the Qualtrics survey export, drops metadata columns, and cross-tabulates self-reported resource usage frequency (Q55) against post-graduation plans (Q12). Cleans and recodes both variables, then produces stacked bar charts of the relationship.

---

## Requirements

```
pandas
numpy
matplotlib
seaborn
```

Install with:

```bash
pip install pandas numpy matplotlib seaborn
```

---

## Output Files

| File | Produced by |
|---|---|
| `Filemaker_CLEAN.csv` | `cleaning.ipynb` |
| `engagement_funnel.png` | `engagement_depth.py` |
| `transition_heatmap.png` | `event_transitions.py` |
