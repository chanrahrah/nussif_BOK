import pandas as pd
import numpy as np

df_bok = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\BOK Base rate MoM.csv')
df_cpi = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Consumer Price indices MoM.csv')
df_cts = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Consumer Tendency Survey MoM.csv')
df_debt = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Debt securities Net Transactions(Market Value) QoQ.csv')
df_fx = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Exchange Rate of Won against USD, China, Japan Daily.csv')
df_npish = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Final Consumption Expenditure of NPISH by Purpose QoQ.csv')
df_gdp = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\GDP and GNI by Economic Activities QoQ.csv')
df_house = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\House Price Index(KB) MoM.csv')
df_nps = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\nps_asset_allocation YoY.csv')
df_ktb = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Trade of KTB Bond MoM.csv')
df_kospi = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Transactions in KOSPI KOSDAQ Index MoM.csv')
df_tax = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Tax collection YoY.csv')
df_expense = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Expenditures on GDP QoQ.csv')

# clean nps data
df_nps["date"] = pd.to_datetime(df_nps["date"].astype(str), format="%Y")
df_nps_percent = df_nps.pivot(index="date", columns="asset_class", values="weight_percent").sort_index()
df_nps_aum = df_nps.pivot(index="date", columns="asset_class", values="aum_billion_krw").sort_index()

# clean data type 
yearly_data = [df_nps, df_tax]
quarterly_data = [df_debt, df_npish, df_gdp, df_expense]
monthly_data = [df_bok, df_cpi, df_cts, df_house, df_ktb, df_kospi]
daily_data = [df_fx]
full_data = yearly_data + quarterly_data + monthly_data + daily_data

# Helper cleaning function
def clean_data(data: pd.DataFrame):
    # clean date column, then move to index
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"].astype(str), format="mixed")
        data.set_index("date", inplace=True)
    # ensure datetime index
    data.index = pd.to_datetime(data.index)

    # clean numeric columns
    data[:] = (
        data.astype(str)
            .replace({",": "", " ": ""}, regex=True)
            .replace({"-": None, "": None, "nan": None})
            .apply(pd.to_numeric, errors="coerce")
    )

    # clean column names
    data.columns = (
        data.columns
        .str.strip()        # remove leading/trailing spaces
    ) 
    return data

# --------------------------------------------
# Clean data
for df in quarterly_data:
    df["date"] = (
        df["date"]
        .astype(str)
        .str.replace("/", "", regex=False)
    )
    df["date"] = pd.PeriodIndex(df["date"], freq="Q").to_timestamp()

for df in full_data:
    df = clean_data(df)

# clean data into monthly frequency
# daily to monthly
df_fx_monthly    = df_fx.resample("MS").mean()
# quarterly to monthly
df_debt_monthly  = df_debt.resample("MS").ffill()
df_npish_monthly = df_npish.resample("MS").ffill()
df_gdp_monthly   = df_gdp.resample("MS").ffill()
df_expense_monthly = df_expense.resample("MS").ffill()
# yearly to monthly
df_nps_percent_monthly   = df_nps_percent.resample("MS").interpolate()
df_tax = df_tax.infer_objects(copy=False)
df_tax_monthly = df_tax.resample("MS").interpolate()

# --------------------------------------------
# Data Merging
new_df_list = [
    df_bok, df_cpi, df_cts, df_debt_monthly, df_fx_monthly, df_npish_monthly,
    df_gdp_monthly, df_house, df_nps_percent_monthly, df_ktb, df_kospi,
    df_tax_monthly, df_expense_monthly
]

# Concatenate all DataFrames along columns (axis=1), joining on indices
full_df = pd.concat(new_df_list, axis=1, join="outer")
full_df.sort_index(inplace=True)

df = full_df.copy()

# Feature Engineering: Debt Calculations
df["govt_debt_total"] = (
    df["Central Government -   Domestic Market"] +
    df["Central Government -   Foreign Market"]
)

df["govt_debt_domestic"] = df["Central Government -   Domestic Market"]
df["govt_debt_foreign"] = df["Central Government -   Foreign Market"]
df["govt_debt_fx"] = df["Central Government -   Foreign Currency"]
df["govt_debt_short"] = df["Central Government -   Short Term"]
df["bank_absorption"] = df["Depository Corporations -   Domestic Market"]
df["institutional_absorption"] = df["Insurance Corporations and Pension Funds -   Domestic Market"]
df["bok_holdings"] = df["Bank of Korea -   Domestic Market"]

# Calculate debt-to-GDP ratio
df["govt_debt_to_gdp"] = df["govt_debt_total"] / df["Gross domestic product at market prices(GDP)"]

# Assign the engineered DataFrame back to the main variable name
full_df_monthly = df


# Final Data Filtering and Export
full_df_monthly = full_df_monthly.loc["2018-01-01":"2025-12-31"]
full_df_monthly = full_df_monthly.dropna()

# Save the final cleaned DataFrame to a CSV file
full_df_monthly.to_csv("cleaned_full_data.csv", index=True)

print(full_df_monthly.columns.tolist())
