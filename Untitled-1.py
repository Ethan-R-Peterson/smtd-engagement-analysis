# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# %%
df = pd.read_csv("Filemaker_Dataset_Copy.csv")
df.head()

# %%
print(df.shape)
print(df.columns)

# %%
print(df.info(verbose=True, show_counts=True))

# %%
df.describe()

# %% [markdown]
# **Observations**
# 
# * Some columns have no non-null values. Several have very few non-null values. 
# * The dataset contains 41 columns, many of which are redundant/unnecessary (e.g. "unique participant"). 
# * Numerical information doesn't seem useful. 
# * Likely want to make a new column for semester, pulled out of entries like "FA 2019". 
# * Can track attendees by experience with Experience_fk.

# %% [markdown]
# Cleaning

# %%
# Drop unnecessary columns
df = df.drop(columns=["amount attributed", "Imported Department","Imported Grad Year", "Imported Minor", "Registrar Minor", "Status", "Registrar Grad Code", "Registrar Department", "Registrar Admit Code", "Registrar Minor", "Registrar Program"])

# Rename columns for clarity
df = df.rename(columns={
    "Experience_fk": "experience_id",
    "Person_fk": "Person_id",
    "Experiences:: Term": "term"
    })
df.head()

# %%
# Create term_season and year columns from "term"
df["term_season"] = df["term"].str[:2]
df["year"] = pd.to_numeric(df["term"].str[-4:], errors="coerce").astype("Int64")

# Combine sudent First + Last Name
df["student_name"] = df["Registrar First Name"] + " " + df["Registrar Last Name"]

df.head()

# %%
# Attempt forward filling missing values of different columns
df = df.ffill()
df.isna().sum().sort_values(ascending=False) # check if any nan values, make sure column names correct

df.head(20)

# %%
print(df["Person-fk"].nunique(), "unique people")
print(df["Record ID"].nunique(), "unique experiences")


