import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍫",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #fafafa;
}

h1 {
    color: #4A2C2A;
}

h2, h3 {
    color: #5C4033;
}

[data-testid="stMetric"] {
    background-color: blue;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid #e6e6e6;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

DATA_PATH = "output/clean_nassau_candy.csv"

df = pd.read_csv(DATA_PATH)

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True,
    errors="coerce"
)

df["Gross Margin %"] = (
    df["Gross Profit"] / df["Sales"]
) * 100

df["Profit per Unit"] = (
    df["Gross Profit"] / df["Units"]
)


# ============================================================
# TITLE
# ============================================================

st.title("🍫 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

st.markdown(
    "An interactive dashboard for evaluating product profitability, "
    "margin performance, division efficiency, cost pressure, "
    "profit concentration and product-level business actions."
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

# Date filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Division filter
divisions = sorted(
    df["Division"].dropna().unique()
)

selected_divisions = st.sidebar.multiselect(
    "Division",
    divisions,
    default=divisions
)

# Margin threshold
margin_threshold = st.sidebar.slider(
    "Minimum Gross Margin (%)",
    min_value=0,
    max_value=100,
    value=20,
    step=5
)

# Product search
product_search = st.sidebar.text_input(
    "Search Product",
    placeholder="Enter product name..."
)


# ============================================================
# APPLY FILTERS
# ============================================================

if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered_df = df[
        (df["Order Date"] >= start_date) &
        (df["Order Date"] <= end_date)
    ].copy()

else:

    filtered_df = df.copy()


filtered_df = filtered_df[
    filtered_df["Division"].isin(selected_divisions)
]


if product_search:

    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            product_search,
            case=False,
            na=False
        )
    ]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered_df.empty:

    st.warning(
        "No records match the selected filters. "
        "Please change the date range, division, margin threshold "
        "or product search."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_cost = filtered_df["Cost"].sum()
total_units = filtered_df["Units"].sum()

overall_margin = (
    total_profit / total_sales * 100
    if total_sales > 0 else 0
)

product_count = filtered_df["Product Name"].nunique()


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown("## Executive Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "Gross Profit",
    f"${total_profit:,.2f}"
)

col3.metric(
    "Gross Margin",
    f"{overall_margin:.2f}%"
)

col4.metric(
    "Units Sold",
    f"{total_units:,}"
)

col5.metric(
    "Products",
    f"{product_count}"
)


# ============================================================
# PRODUCT PROFITABILITY OVERVIEW
# ============================================================

st.markdown("---")
st.header("1. Product Profitability Overview")

product_summary = (
    filtered_df
    .groupby(
        ["Product Name", "Division"],
        as_index=False
    )
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
        Units=("Units", "sum")
    )
)

product_summary["Gross Margin %"] = (
    product_summary["Gross_Profit"] /
    product_summary["Sales"] * 100
)

product_summary["Profit per Unit"] = (
    product_summary["Gross_Profit"] /
    product_summary["Units"]
)


# Margin-filtered view
margin_view = product_summary[
    product_summary["Gross Margin %"] >= margin_threshold
].copy()


# ============================================================
# TOP PRODUCTS BY GROSS PROFIT
# ============================================================

if not margin_view.empty:

    top_products = (
        margin_view
        .sort_values(
            "Gross_Profit",
            ascending=False
        )
        .head(10)
        .sort_values("Gross_Profit")
    )

    fig_top = px.bar(
        top_products,
        x="Gross_Profit",
        y="Product Name",
        orientation="h",
        color="Division",
        title="Top Products by Gross Profit",
        labels={
            "Gross_Profit": "Gross Profit ($)",
            "Product Name": "Product"
        }
    )

    fig_top.update_layout(
        height=500,
        legend_title_text="Division"
    )

    st.plotly_chart(
        fig_top,
        width="stretch"
    )

else:

    st.info(
        "No products meet the selected minimum gross margin."
    )


# ============================================================
# PRODUCT MARGIN CHART
# ============================================================

if not margin_view.empty:

    top_margin = (
        margin_view
        .sort_values(
            "Gross Margin %",
            ascending=False
        )
        .head(10)
        .sort_values("Gross Margin %")
    )

    fig_product_margin = px.bar(
        top_margin,
        x="Gross Margin %",
        y="Product Name",
        orientation="h",
        color="Division",
        title="Top Products by Gross Margin",
        labels={
            "Gross Margin %": "Gross Margin (%)",
            "Product Name": "Product"
        }
    )

    fig_product_margin.update_xaxes(
        range=[0, 100]
    )

    st.plotly_chart(
        fig_product_margin,
        width="stretch"
    )


# ============================================================
# PRODUCT TABLE
# ============================================================

st.subheader("Product Profitability Leaderboard")

display_products = (
    margin_view
    .sort_values(
        "Gross_Profit",
        ascending=False
    )
    .copy()
)

display_products["Sales"] = (
    display_products["Sales"].round(2)
)

display_products["Gross_Profit"] = (
    display_products["Gross_Profit"].round(2)
)

display_products["Cost"] = (
    display_products["Cost"].round(2)
)

display_products["Gross Margin %"] = (
    display_products["Gross Margin %"].round(2)
)

display_products["Profit per Unit"] = (
    display_products["Profit per Unit"].round(2)
)

st.dataframe(
    display_products,
    width="stretch",
    hide_index=True
)


# ============================================================
# DOWNLOAD PRODUCT ANALYSIS
# ============================================================

st.download_button(
    label="Download Product Profitability CSV",
    data=display_products.to_csv(index=False),
    file_name="filtered_product_profitability.csv",
    mime="text/csv"
)


# ============================================================
# DIVISION PERFORMANCE
# ============================================================

st.markdown("---")
st.header("2. Division Performance")

division_summary = (
    filtered_df
    .groupby(
        "Division",
        as_index=False
    )
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Cost=("Cost", "sum"),
        Units=("Units", "sum"),
        Products=("Product Name", "nunique")
    )
)

division_summary["Gross Margin %"] = (
    division_summary["Gross_Profit"] /
    division_summary["Sales"] * 100
)

division_summary["Revenue Contribution %"] = (
    division_summary["Sales"] /
    division_summary["Sales"].sum() * 100
)

division_summary["Profit Contribution %"] = (
    division_summary["Gross_Profit"] /
    division_summary["Gross_Profit"].sum() * 100
)


col1, col2 = st.columns(2)


with col1:

    fig_division = px.bar(
        division_summary,
        x="Division",
        y=["Sales", "Gross_Profit"],
        barmode="group",
        title="Revenue vs Gross Profit by Division",
        labels={
            "value": "Amount ($)",
            "variable": "Metric"
        }
    )

    st.plotly_chart(
        fig_division,
        width="stretch"
    )


with col2:

    fig_margin = px.bar(
        division_summary,
        x="Division",
        y="Gross Margin %",
        title="Gross Margin by Division"
    )

    fig_margin.update_yaxes(
        range=[0, 100]
    )

    st.plotly_chart(
        fig_margin,
        width="stretch"
    )


st.subheader("Division Summary")

st.dataframe(
    division_summary.round(2),
    width="stretch",
    hide_index=True
)


st.download_button(
    label="Download Division Summary CSV",
    data=division_summary.to_csv(index=False),
    file_name="filtered_division_summary.csv",
    mime="text/csv"
)


# ============================================================
# COST VS MARGIN DIAGNOSTICS
# ============================================================

st.markdown("---")
st.header("3. Cost vs Margin Diagnostics")

diagnostic = (
    filtered_df
    .groupby(
        ["Product Name", "Division"],
        as_index=False
    )
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
)

diagnostic["Gross Margin %"] = (
    diagnostic["Gross_Profit"] /
    diagnostic["Sales"] * 100
)

diagnostic["Profit per Unit"] = (
    diagnostic["Gross_Profit"] /
    diagnostic["Units"]
)


# Risk classification
def risk_category(margin):

    if margin < 10:
        return "Critical Risk"

    elif margin < 20:
        return "High Risk"

    elif margin < 30:
        return "Moderate Risk"

    else:
        return "Healthy"


diagnostic["Margin Risk"] = (
    diagnostic["Gross Margin %"]
    .apply(risk_category)
)


# ============================================================
# COST VS SALES SCATTER
# ============================================================

fig_cost = px.scatter(
    diagnostic,
    x="Cost",
    y="Sales",
    size="Gross_Profit",
    color="Gross Margin %",
    hover_name="Product Name",
    hover_data=[
        "Division",
        "Gross_Profit",
        "Gross Margin %",
        "Profit per Unit"
    ],
    title="Cost vs Sales with Margin Performance",
    labels={
        "Cost": "Cost ($)",
        "Sales": "Sales ($)",
        "Gross Margin %": "Gross Margin (%)"
    }
)

st.plotly_chart(
    fig_cost,
    width="stretch"
)


# ============================================================
# RISK DISTRIBUTION
# ============================================================

risk_counts = (
    diagnostic["Margin Risk"]
    .value_counts()
    .reset_index()
)

risk_counts.columns = [
    "Margin Risk",
    "Products"
]

fig_risk = px.bar(
    risk_counts,
    x="Margin Risk",
    y="Products",
    title="Product Distribution by Margin Risk",
    labels={
        "Products": "Number of Products"
    }
)

st.plotly_chart(
    fig_risk,
    width="stretch"
)


# ============================================================
# RISK TABLE
# ============================================================

st.subheader("Margin Risk Analysis")

risk_table = (
    diagnostic
    .sort_values("Gross Margin %")
    [[
        "Product Name",
        "Division",
        "Sales",
        "Cost",
        "Gross_Profit",
        "Gross Margin %",
        "Profit per Unit",
        "Margin Risk"
    ]]
)

st.dataframe(
    risk_table.round(2),
    width="stretch",
    hide_index=True
)


st.download_button(
    label="Download Margin Risk CSV",
    data=risk_table.to_csv(index=False),
    file_name="margin_risk_analysis.csv",
    mime="text/csv"
)


# ============================================================
# PROFIT CONCENTRATION / PARETO
# ============================================================

st.markdown("---")
st.header("4. Profit & Revenue Concentration Analysis")


pareto = (
    filtered_df
    .groupby(
        "Product Name",
        as_index=False
    )
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
)


# ============================================================
# REVENUE PARETO
# ============================================================

revenue_pareto = (
    pareto
    .sort_values(
        "Sales",
        ascending=False
    )
    .copy()
)

revenue_pareto["Revenue Contribution %"] = (
    revenue_pareto["Sales"] /
    revenue_pareto["Sales"].sum() * 100
)

revenue_pareto["Cumulative Revenue %"] = (
    revenue_pareto["Revenue Contribution %"]
    .cumsum()
)


fig_revenue_pareto = go.Figure()

fig_revenue_pareto.add_trace(
    go.Bar(
        x=revenue_pareto["Product Name"],
        y=revenue_pareto["Sales"],
        name="Revenue"
    )
)

fig_revenue_pareto.add_trace(
    go.Scatter(
        x=revenue_pareto["Product Name"],
        y=revenue_pareto["Cumulative Revenue %"],
        name="Cumulative Revenue %",
        yaxis="y2",
        mode="lines+markers"
    )
)

fig_revenue_pareto.update_layout(
    title="Revenue Pareto Analysis",
    yaxis=dict(
        title="Revenue ($)"
    ),
    yaxis2=dict(
        title="Cumulative Revenue (%)",
        overlaying="y",
        side="right",
        range=[0, 110]
    ),
    height=550
)

st.plotly_chart(
    fig_revenue_pareto,
    width="stretch"
)


# ============================================================
# PROFIT PARETO
# ============================================================

profit_pareto = (
    pareto
    .sort_values(
        "Gross_Profit",
        ascending=False
    )
    .copy()
)

profit_pareto["Profit Contribution %"] = (
    profit_pareto["Gross_Profit"] /
    profit_pareto["Gross_Profit"].sum() * 100
)

profit_pareto["Cumulative Profit %"] = (
    profit_pareto["Profit Contribution %"]
    .cumsum()
)


fig_profit_pareto = go.Figure()

fig_profit_pareto.add_trace(
    go.Bar(
        x=profit_pareto["Product Name"],
        y=profit_pareto["Gross_Profit"],
        name="Gross Profit"
    )
)

fig_profit_pareto.add_trace(
    go.Scatter(
        x=profit_pareto["Product Name"],
        y=profit_pareto["Cumulative Profit %"],
        name="Cumulative Profit %",
        yaxis="y2",
        mode="lines+markers"
    )
)

fig_profit_pareto.update_layout(
    title="Profit Pareto Analysis",
    yaxis=dict(
        title="Gross Profit ($)"
    ),
    yaxis2=dict(
        title="Cumulative Profit (%)",
        overlaying="y",
        side="right",
        range=[0, 110]
    ),
    height=550
)

st.plotly_chart(
    fig_profit_pareto,
    width="stretch"
)


# ============================================================
# PARETO SUMMARY
# ============================================================

revenue_80_count = (
    revenue_pareto["Cumulative Revenue %"] >= 80
).idxmax() + 1

profit_80_count = (
    profit_pareto["Cumulative Profit %"] >= 80
).idxmax() + 1

total_products = len(pareto)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Products Driving ~80% Revenue",
        f"{revenue_80_count}"
    )

    st.caption(
        f"{(revenue_80_count / total_products * 100):.2f}% "
        "of products."
    )

with col2:

    st.metric(
        "Products Driving ~80% Profit",
        f"{profit_80_count}"
    )

    st.caption(
        f"{(profit_80_count / total_products * 100):.2f}% "
        "of products."
    )


# ============================================================
# MARGIN VOLATILITY
# ============================================================

st.markdown("---")
st.header("5. Margin Volatility Analysis")

volatility_df = filtered_df.copy()

volatility_df["Month"] = (
    volatility_df["Order Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_margin = (
    volatility_df
    .groupby(
        ["Month", "Product Name"],
        as_index=False
    )
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
)

monthly_margin["Gross Margin %"] = (
    monthly_margin["Gross_Profit"] /
    monthly_margin["Sales"] * 100
)


overall_monthly_margin = (
    volatility_df
    .groupby("Month", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
)

overall_monthly_margin["Gross Margin %"] = (
    overall_monthly_margin["Gross_Profit"] /
    overall_monthly_margin["Sales"] * 100
)


fig_volatility = px.line(
    overall_monthly_margin,
    x="Month",
    y="Gross Margin %",
    markers=True,
    title="Monthly Gross Margin Trend",
    labels={
        "Month": "Month",
        "Gross Margin %": "Gross Margin (%)"
    }
)

fig_volatility.update_yaxes(
    range=[0, 100]
)

st.plotly_chart(
    fig_volatility,
    width="stretch"
)


# Product-level volatility

product_volatility = (
    monthly_margin
    .groupby("Product Name", as_index=False)
    .agg(
        Average_Margin=("Gross Margin %", "mean"),
        Margin_Volatility=("Gross Margin %", "std")
    )
)

product_volatility["Margin_Volatility"] = (
    product_volatility["Margin_Volatility"]
    .fillna(0)
)

product_volatility = (
    product_volatility
    .sort_values(
        "Margin_Volatility",
        ascending=False
    )
)


st.subheader("Product Margin Volatility")

st.dataframe(
    product_volatility.round(2),
    width="stretch",
    hide_index=True
)


st.download_button(
    label="Download Margin Volatility CSV",
    data=product_volatility.to_csv(index=False),
    file_name="margin_volatility.csv",
    mime="text/csv"
)


# ============================================================
# LOW SALES / LOW PROFIT PRODUCTS
# ============================================================

st.markdown("---")
st.header("6. Low-Sales / Low-Profit Products")

sales_median = product_summary["Sales"].median()
profit_median = product_summary["Gross_Profit"].median()

low_sales_low_profit = product_summary[
    (product_summary["Sales"] < sales_median) &
    (product_summary["Gross_Profit"] < profit_median)
].copy()

if not low_sales_low_profit.empty:

    fig_low = px.scatter(
        product_summary,
        x="Sales",
        y="Gross_Profit",
        color="Division",
        hover_name="Product Name",
        title="Sales vs Gross Profit by Product",
        labels={
            "Sales": "Sales ($)",
            "Gross_Profit": "Gross Profit ($)"
        }
    )

    st.plotly_chart(
        fig_low,
        width="stretch"
    )

    st.subheader("Products Requiring Rationalization Review")

    st.dataframe(
        low_sales_low_profit.round(2),
        width="stretch",
        hide_index=True
    )

    st.download_button(
        label="Download Low-Sales / Low-Profit CSV",
        data=low_sales_low_profit.to_csv(index=False),
        file_name="low_sales_low_profit.csv",
        mime="text/csv"
    )

else:

    st.info(
        "No products fall into the low-sales / low-profit category "
        "for the selected filters."
    )


# ============================================================
# BUSINESS ACTION ANALYSIS
# ============================================================

st.markdown("---")
st.header("7. Business Action Recommendations")


action_df = product_summary.copy()

median_profit = action_df["Gross_Profit"].median()

def business_action(row):

    margin = row["Gross Margin %"]
    sales = row["Sales"]
    profit = row["Gross_Profit"]

    if margin < 10:
        return "Reprice / Renegotiate"

    elif margin < 20 and sales >= sales_median:
        return "Reprice / Renegotiate"

    elif sales < sales_median and profit < median_profit:
        return "Review for Rationalization"

    elif margin >= 50 and profit >= median_profit:
        return "Protect / Expand"

    else:
        return "Monitor"


action_df["Business Action"] = (
    action_df.apply(
        business_action,
        axis=1
    )
)


action_counts = (
    action_df["Business Action"]
    .value_counts()
    .reset_index()
)

action_counts.columns = [
    "Business Action",
    "Products"
]


fig_actions = px.bar(
    action_counts,
    x="Business Action",
    y="Products",
    title="Recommended Business Actions by Product",
    labels={
        "Products": "Number of Products"
    }
)

st.plotly_chart(
    fig_actions,
    width="stretch"
)


st.subheader("Product-Level Business Actions")

action_display = (
    action_df
    .sort_values(
        ["Business Action", "Gross_Profit"],
        ascending=[True, False]
    )
    [[
        "Product Name",
        "Division",
        "Sales",
        "Cost",
        "Gross_Profit",
        "Gross Margin %",
        "Profit per Unit",
        "Business Action"
    ]]
)

st.dataframe(
    action_display.round(2),
    width="stretch",
    hide_index=True
)


st.download_button(
    label="Download Business Action Analysis CSV",
    data=action_display.to_csv(index=False),
    file_name="business_action_analysis.csv",
    mime="text/csv"
)


# ============================================================
# KEY BUSINESS INSIGHTS
# ============================================================

st.markdown("---")
st.header("8. Key Business Insights")


# Use complete product summary for insights
if not product_summary.empty:

    top_profit_product = (
        product_summary
        .sort_values(
            "Gross_Profit",
            ascending=False
        )
        .iloc[0]
    )

    top_margin_product = (
        product_summary
        .sort_values(
            "Gross Margin %",
            ascending=False
        )
        .iloc[0]
    )

    low_margin_product = (
        diagnostic
        .sort_values(
            "Gross Margin %"
        )
        .iloc[0]
    )

    best_division = (
        division_summary
        .sort_values(
            "Gross_Profit",
            ascending=False
        )
        .iloc[0]
    )

    st.markdown(
        f"""
### Profitability

**Highest Profit Product:**  
{top_profit_product['Product Name']} generated
**${top_profit_product['Gross_Profit']:,.2f}** in gross profit.

**Highest Margin Product:**  
{top_margin_product['Product Name']} achieved a gross margin of
**{top_margin_product['Gross Margin %']:.2f}%**.

### Division Performance

**Highest Profit Division:**  
{best_division['Division']} generated
**${best_division['Gross_Profit']:,.2f}** in gross profit and contributed
**{best_division['Profit Contribution %']:.2f}%** of total profit.

### Margin Risk

**Lowest Margin Product:**  
{low_margin_product['Product Name']} has a gross margin of
**{low_margin_product['Gross Margin %']:.2f}%** and should be reviewed
for pricing or cost-efficiency improvement.

### Concentration

Approximately **{revenue_80_count} products** account for 80% of revenue,
while approximately **{profit_80_count} products** account for 80% of profit.

This indicates that profitability is concentrated among a relatively
small portion of the product portfolio.
"""
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Nassau Candy Distributor | Product Line Profitability & Margin Performance Analysis"
)