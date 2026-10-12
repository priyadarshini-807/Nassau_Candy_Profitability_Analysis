import pandas as pd
import numpy as np
import os

# ============================================================
# 1. LOAD DATA
# ============================================================

file_path = "data/Nassau Candy Distributor.csv"

df = pd.read_csv(file_path)

print("=" * 70)
print("NASSAU CANDY DISTRIBUTOR")
print("PRODUCT LINE PROFITABILITY & MARGIN PERFORMANCE ANALYSIS")
print("=" * 70)

print(f"\nOriginal Rows    : {df.shape[0]}")
print(f"Original Columns : {df.shape[1]}")


# ============================================================
# 2. CREATE OUTPUT FOLDER
# ============================================================

os.makedirs("output", exist_ok=True)


# ============================================================
# 3. CHECK COLUMN NAMES
# ============================================================

print("\n" + "=" * 70)
print("COLUMN NAMES")
print("=" * 70)

for column in df.columns:
    print("-", column)


# ============================================================
# 4. CHECK MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

missing = df.isnull().sum()

if missing.sum() == 0:
    print("No missing values found.")
else:
    print(missing[missing > 0])


# ============================================================
# 5. CONVERT DATE COLUMNS
# ============================================================

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

df["Ship Date"] = pd.to_datetime(
    df["Ship Date"],
    format="%d-%m-%Y",
    errors="coerce"
)


# ============================================================
# 6. CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Sales",
    "Units",
    "Gross Profit",
    "Cost"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 7. VALIDATE NUMERIC VALUES
# ============================================================

print("\n" + "=" * 70)
print("INVALID / ZERO VALUES")
print("=" * 70)

print("Sales <= 0       :", (df["Sales"] <= 0).sum())
print("Units <= 0       :", (df["Units"] <= 0).sum())
print("Cost < 0         :", (df["Cost"] < 0).sum())
print("Gross Profit < 0 :", (df["Gross Profit"] < 0).sum())


# ============================================================
# 8. VALIDATE GROSS PROFIT
# ============================================================

df["Calculated Profit"] = (
    df["Sales"] - df["Cost"]
)

df["Profit Difference"] = (
    df["Gross Profit"] -
    df["Calculated Profit"]
).abs()

profit_errors = (
    df["Profit Difference"] > 0.01
).sum()

print("\n" + "=" * 70)
print("GROSS PROFIT VALIDATION")
print("=" * 70)

print(
    "Records where Gross Profit != Sales - Cost:",
    profit_errors
)

print(
    "Maximum profit calculation difference:",
    round(df["Profit Difference"].max(), 4)
)


# ============================================================
# 9. DUPLICATE CHECK
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATE CHECK")
print("=" * 70)

print(
    "Duplicate rows:",
    df.duplicated().sum()
)


# ============================================================
# 10. STANDARDIZE TEXT COLUMNS
# ============================================================

text_columns = [
    "Division",
    "Product Name",
    "Product ID",
    "Region",
    "Ship Mode"
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )


# ============================================================
# 11. CREATE CLEAN DATASET
# ============================================================

clean_df = df.copy()

clean_df = clean_df[
    (clean_df["Sales"] > 0) &
    (clean_df["Units"] > 0) &
    (clean_df["Cost"] >= 0) &
    (clean_df["Gross Profit"] >= 0)
].copy()


# ============================================================
# 12. CREATE PROFITABILITY KPIs
# ============================================================

clean_df["Gross Margin %"] = np.where(
    clean_df["Sales"] != 0,
    (
        clean_df["Gross Profit"] /
        clean_df["Sales"]
    ) * 100,
    0
)

clean_df["Profit per Unit"] = np.where(
    clean_df["Units"] != 0,
    clean_df["Gross Profit"] /
    clean_df["Units"],
    0
)


# ============================================================
# 13. FINAL DATASET SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CLEAN DATASET")
print("=" * 70)

print("Original records :", len(df))
print("Clean records    :", len(clean_df))
print(
    "Removed records  :",
    len(df) - len(clean_df)
)


# ============================================================
# 14. BASIC BUSINESS SUMMARY
# ============================================================

total_sales = clean_df["Sales"].sum()
total_profit = clean_df["Gross Profit"].sum()
total_cost = clean_df["Cost"].sum()
total_units = clean_df["Units"].sum()

overall_margin = (
    total_profit /
    total_sales
) * 100

print("\n" + "=" * 70)
print("BUSINESS SUMMARY")
print("=" * 70)

print(f"Total Sales        : ${total_sales:,.2f}")
print(f"Total Gross Profit : ${total_profit:,.2f}")
print(f"Total Cost         : ${total_cost:,.2f}")
print(f"Total Units        : {total_units:,.0f}")
print(f"Overall Gross Margin: {overall_margin:.2f}%")


# ============================================================
# 15. DIVISION SUMMARY
# ============================================================

division_summary = (
    clean_df
    .groupby("Division")
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
        Units=("Units", "sum"),
        Products=("Product ID", "nunique")
    )
    .reset_index()
)

division_summary["Gross Margin %"] = (
    division_summary["Gross_Profit"] /
    division_summary["Sales"]
) * 100

division_summary["Profit per Unit"] = (
    division_summary["Gross_Profit"] /
    division_summary["Units"]
)

division_summary["Revenue Contribution %"] = (
    division_summary["Sales"] /
    total_sales
) * 100

division_summary["Profit Contribution %"] = (
    division_summary["Gross_Profit"] /
    total_profit
) * 100

print("\n" + "=" * 70)
print("DIVISION PERFORMANCE")
print("=" * 70)

print(
    division_summary
    .sort_values(
        "Gross_Profit",
        ascending=False
    )
    .to_string(index=False)
)


# ============================================================
# 16. PRODUCT-LEVEL PROFITABILITY
# ============================================================

product_summary = (
    clean_df
    .groupby(
        [
            "Division",
            "Product ID",
            "Product Name"
        ]
    )
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
        Units=("Units", "sum"),
        Orders=("Order ID", "nunique")
    )
    .reset_index()
)

product_summary["Gross Margin %"] = np.where(
    product_summary["Sales"] != 0,
    (
        product_summary["Gross_Profit"] /
        product_summary["Sales"]
    ) * 100,
    0
)

product_summary["Profit per Unit"] = np.where(
    product_summary["Units"] != 0,
    product_summary["Gross_Profit"] /
    product_summary["Units"],
    0
)

product_summary["Revenue Contribution %"] = (
    product_summary["Sales"] /
    total_sales
) * 100

product_summary["Profit Contribution %"] = (
    product_summary["Gross_Profit"] /
    total_profit
) * 100


# ============================================================
# 17. PRODUCT RANKINGS
# ============================================================

product_summary["Profit Rank"] = (
    product_summary["Gross_Profit"]
    .rank(
        method="dense",
        ascending=False
    )
    .astype(int)
)

product_summary["Margin Rank"] = (
    product_summary["Gross Margin %"]
    .rank(
        method="dense",
        ascending=False
    )
    .astype(int)
)


# ============================================================
# 18. MARGIN VOLATILITY
# ============================================================

# Margin volatility is measured using the standard deviation
# of monthly product-level gross margins.

monthly_product = (
    clean_df
    .assign(
        Month=clean_df["Order Date"]
        .dt.to_period("M")
    )
    .groupby(
        [
            "Product ID",
            "Product Name",
            "Division",
            "Month"
        ]
    )
    .agg(
        Monthly_Sales=("Sales", "sum"),
        Monthly_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

monthly_product["Monthly Margin %"] = np.where(
    monthly_product["Monthly_Sales"] != 0,
    (
        monthly_product["Monthly_Profit"] /
        monthly_product["Monthly_Sales"]
    ) * 100,
    np.nan
)

margin_volatility = (
    monthly_product
    .groupby(
        [
            "Product ID",
            "Product Name",
            "Division"
        ]
    )
    .agg(
        Average_Margin=("Monthly Margin %", "mean"),
        Margin_Volatility=("Monthly Margin %", "std"),
        Minimum_Margin=("Monthly Margin %", "min"),
        Maximum_Margin=("Monthly Margin %", "max")
    )
    .reset_index()
)

margin_volatility["Margin_Volatility"] = (
    margin_volatility["Margin_Volatility"]
    .fillna(0)
)

product_summary = product_summary.merge(
    margin_volatility,
    on=[
        "Product ID",
        "Product Name",
        "Division"
    ],
    how="left"
)


# ============================================================
# 19. HIGH-SALES / LOW-MARGIN
# ============================================================

sales_median = product_summary["Sales"].median()

high_sales_low_margin = product_summary[
    (product_summary["Sales"] >= sales_median) &
    (product_summary["Gross Margin %"] < 20)
].copy()


# ============================================================
# 20. HIGH-PROFIT / HIGH-MARGIN
# ============================================================

profit_median = product_summary["Gross_Profit"].median()

high_profit_high_margin = product_summary[
    (product_summary["Gross_Profit"] >= profit_median) &
    (product_summary["Gross Margin %"] >= 50)
].copy()


# ============================================================
# 21. LOW-SALES / LOW-PROFIT
# ============================================================

low_sales_low_profit = product_summary[
    (product_summary["Sales"] < sales_median) &
    (product_summary["Gross_Profit"] < profit_median)
].copy()


# ============================================================
# 22. MARGIN RISK
# ============================================================

product_summary["Margin Risk"] = np.select(
    [
        product_summary["Gross Margin %"] < 10,
        product_summary["Gross Margin %"] < 20,
        product_summary["Gross Margin %"] < 30
    ],
    [
        "Critical Risk",
        "High Risk",
        "Moderate Risk"
    ],
    default="Healthy"
)


# ============================================================
# 23. BUSINESS ACTION FLAGS
# ============================================================

def business_action(row):

    margin = row["Gross Margin %"]
    sales = row["Sales"]
    profit = row["Gross_Profit"]

    if margin < 10:
        return "Reprice / Renegotiate"

    if (
        margin < 20 and
        sales >= sales_median
    ):
        return "Reprice / Renegotiate"

    if (
        sales < sales_median and
        profit < profit_median
    ):
        return "Review for Rationalization"

    if (
        margin >= 50 and
        profit >= profit_median
    ):
        return "Protect / Expand"

    return "Monitor"


product_summary["Business Action"] = (
    product_summary
    .apply(
        business_action,
        axis=1
    )
)


# ============================================================
# 24. REVENUE PARETO
# ============================================================

revenue_pareto = (
    product_summary
    .sort_values(
        "Sales",
        ascending=False
    )
    .copy()
)

revenue_pareto["Cumulative Revenue %"] = (
    revenue_pareto["Revenue Contribution %"]
    .cumsum()
)

revenue_80_count = (
    np.argmax(
        revenue_pareto["Cumulative Revenue %"]
        .values >= 80
    ) + 1
)

revenue_80_percentage = (
    revenue_80_count /
    len(revenue_pareto)
) * 100


# ============================================================
# 25. PROFIT PARETO
# ============================================================

profit_pareto = (
    product_summary
    .sort_values(
        "Gross_Profit",
        ascending=False
    )
    .copy()
)

profit_pareto["Cumulative Profit %"] = (
    profit_pareto["Profit Contribution %"]
    .cumsum()
)

profit_80_count = (
    np.argmax(
        profit_pareto["Cumulative Profit %"]
        .values >= 80
    ) + 1
)

profit_80_percentage = (
    profit_80_count /
    len(profit_pareto)
) * 100


# ============================================================
# 26. PRINT TOP PRODUCTS
# ============================================================

print("\n" + "=" * 70)
print("TOP 10 PRODUCTS BY GROSS PROFIT")
print("=" * 70)

print(
    product_summary
    .sort_values(
        "Gross_Profit",
        ascending=False
    )
    [
        [
            "Product Name",
            "Division",
            "Sales",
            "Gross_Profit",
            "Gross Margin %",
            "Profit per Unit"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


print("\n" + "=" * 70)
print("TOP 10 PRODUCTS BY GROSS MARGIN")
print("=" * 70)

print(
    product_summary
    .sort_values(
        "Gross Margin %",
        ascending=False
    )
    [
        [
            "Product Name",
            "Division",
            "Sales",
            "Gross_Profit",
            "Gross Margin %",
            "Profit per Unit"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 27. RISK ANALYSIS OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("MARGIN RISK DISTRIBUTION")
print("=" * 70)

print(
    product_summary["Margin Risk"]
    .value_counts()
    .to_string()
)


print("\n" + "=" * 70)
print("BUSINESS ACTION DISTRIBUTION")
print("=" * 70)

print(
    product_summary["Business Action"]
    .value_counts()
    .to_string()
)


# ============================================================
# 28. PARETO RESULTS
# ============================================================

print("\n" + "=" * 70)
print("PARETO / 80-20 ANALYSIS")
print("=" * 70)

print(
    f"Products contributing at least 80% of revenue: "
    f"{revenue_80_count}"
)

print(
    f"Percentage of products: "
    f"{revenue_80_percentage:.2f}%"
)

print(
    f"Products contributing at least 80% of profit: "
    f"{profit_80_count}"
)

print(
    f"Percentage of products: "
    f"{profit_80_percentage:.2f}%"
)


# ============================================================
# 29. SAVE OUTPUT FILES
# ============================================================

clean_df.to_csv(
    "output/clean_nassau_candy.csv",
    index=False
)

division_summary.to_csv(
    "output/division_summary.csv",
    index=False
)

product_summary.to_csv(
    "output/product_profitability.csv",
    index=False
)

product_summary.to_csv(
    "output/product_risk_analysis.csv",
    index=False
)

high_sales_low_margin.to_csv(
    "output/high_sales_low_margin.csv",
    index=False
)

high_profit_high_margin.to_csv(
    "output/high_profit_high_margin.csv",
    index=False
)

low_sales_low_profit.to_csv(
    "output/low_sales_low_profit.csv",
    index=False
)

revenue_pareto.to_csv(
    "output/revenue_pareto.csv",
    index=False
)

profit_pareto.to_csv(
    "output/profit_pareto.csv",
    index=False
)

margin_volatility.to_csv(
    "output/margin_volatility.csv",
    index=False
)


# ============================================================
# 30. FINAL OUTPUT MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("ALL ANALYSIS FILES CREATED SUCCESSFULLY")
print("=" * 70)

print("✓ clean_nassau_candy.csv")
print("✓ division_summary.csv")
print("✓ product_profitability.csv")
print("✓ product_risk_analysis.csv")
print("✓ high_sales_low_margin.csv")
print("✓ high_profit_high_margin.csv")
print("✓ low_sales_low_profit.csv")
print("✓ revenue_pareto.csv")
print("✓ profit_pareto.csv")
print("✓ margin_volatility.csv")

print("\nAnalysis completed successfully.")