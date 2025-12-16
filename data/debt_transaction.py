import pandas as pd
import numpy as np

df = pd.read_csv("Debt securities Net Transactions(Market Value) QoQ.csv", header=[0,1])

# Extract header levels
level0 = pd.Series(df.columns.get_level_values(0))
level1 = pd.Series(df.columns.get_level_values(1))

# Replace 'Unnamed' and blanks with NaN
level0_clean = level0.replace(
    ["", " ", None, np.nan] + list(level0[level0.str.contains("Unnamed", na=False)].unique()),
    pd.NA
).ffill()

# Build final cleaned column names
df.columns = [f"{g} - {s}" if pd.notna(g) else s for g, s in zip(level0_clean, level1)]
df.rename(columns={"date - Unnamed: 0_level_1": "date"}, inplace=True)
print(df.head())

df.to_csv("Debt securities Net Transactions(Market Value) QoQ.csv", index=False)