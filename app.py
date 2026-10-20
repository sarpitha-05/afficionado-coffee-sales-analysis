import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Afficionado Coffee Roasters - Sales Dashboard",
    layout="wide",
)

CLEAN_PATH = "afficionado_clean.csv"
BUCKET_ORDER = ["Morning", "Afternoon", "Evening", "Late Hours"]


@st.cache_data
def load_data():
    df = pd.read_csv(CLEAN_PATH)
    return df


df = load_data()

# ----------------------------------------------------------------------
# Sidebar controls
# ----------------------------------------------------------------------
st.sidebar.header("Filters")

stores = sorted(df["store_location"].unique())
selected_stores = st.sidebar.multiselect(
    "Store location", options=stores, default=stores
)

min_hour, max_hour = int(df["hour"].min()), int(df["hour"].max())
hour_range = st.sidebar.slider(
    "Hour range", min_value=min_hour, max_value=max_hour,
    value=(min_hour, max_hour)
)

selected_buckets = st.sidebar.multiselect(
    "Time of day", options=BUCKET_ORDER, default=BUCKET_ORDER
)

metric_label = st.sidebar.radio(
    "Metric", options=["Revenue", "Quantity", "Transactions"]
)
metric_col = {"Revenue": "revenue", "Quantity": "transaction_qty", "Transactions": "transaction_id"}[metric_label]

st.sidebar.caption(
    "Note: the dataset has no date field, only time-of-day. "
    "Day-of-week and daily-trend analysis are not available; "
    "use the Time of day filter instead."
)

# Apply filters
mask = (
    df["store_location"].isin(selected_stores)
    & df["hour"].between(hour_range[0], hour_range[1])
    & df["time_bucket"].isin(selected_buckets)
)
fdf = df[mask]

# ----------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------
st.title("☕ Afficionado Coffee Roasters")
st.subheader("Sales Performance & Hourly Demand Dashboard")
st.caption(
    "Explore revenue, transaction volume, product categories, and "
    "store performance by hour. Daily and day-of-week trends cannot "
    "be calculated because the supplied dataset has no transaction date."
)

if fdf.empty:
    st.warning("No data matches the current filters. Adjust the filters in the sidebar.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${fdf['revenue'].sum():,.0f}")
k2.metric("Transactions", f"{fdf['transaction_id'].nunique():,}")
k3.metric("Quantity Sold", f"{fdf['transaction_qty'].sum():,}")
avg_transaction_value = fdf["revenue"].sum() / fdf["transaction_id"].nunique()
k4.metric("Avg Transaction Value", f"${avg_transaction_value:.2f}")
k5.metric("Stores", f"{fdf['store_location'].nunique()}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Hourly Trend", "Time of Day", "Store Comparison", "Cross-Location Heatmap", "Products"]
)

# ----------------------------------------------------------------------
# Tab 1: Hourly trend (overall sales trend dashboard)
# ----------------------------------------------------------------------
with tab1:
    st.subheader(f"Hourly {metric_label} Trend")

    hourly = fdf.groupby("hour").agg(
        revenue=("revenue", "sum"),
        transaction_qty=("transaction_qty", "sum"),
        transaction_id=("transaction_id", "nunique"),
    ).reset_index()

    def hour_label(h):
        h = int(h)
        period = "AM" if h < 12 else "PM"
        display_h = h % 12
        if display_h == 0:
            display_h = 12
        return f"{display_h} {period}"

    y_col = metric_col
    fig = px.line(
        hourly, x="hour", y=y_col,
        markers=True, title=f"{metric_label} by Hour of Day"
    )
    fig.update_xaxes(
        title="Hour of Day",
        tickmode="array",
        tickvals=hourly["hour"],
        ticktext=[hour_label(h) for h in hourly["hour"]],
    )
    fig.update_yaxes(title=metric_label)
    st.plotly_chart(fig, use_container_width=True)

    peak_row = hourly.loc[hourly[y_col].idxmax()]
    peak_hour_display = hour_label(peak_row["hour"])
    if metric_label == "Revenue":
        peak_value_display = f"${peak_row[y_col]:,.2f}"
    elif metric_label == "Quantity":
        peak_value_display = f"{int(peak_row[y_col]):,} units sold"
    else:
        peak_value_display = f"{int(peak_row[y_col]):,} transactions"

    st.info(
        f"Peak {metric_label.lower()} hour: **{peak_hour_display}** "
        f"({int(peak_row['hour']):02d}:00) — {peak_value_display}"
    )

# ----------------------------------------------------------------------
# Tab 2: Time of day bucket performance
# ----------------------------------------------------------------------
with tab2:
    st.subheader("Performance by Time of Day")
    st.caption("Substitutes for day-of-week analysis (unavailable - no date column in source data).")

    bucket_summary = fdf.groupby("time_bucket").agg(
        revenue=("revenue", "sum"),
        transaction_qty=("transaction_qty", "sum"),
        transaction_id=("transaction_id", "nunique"),
    ).reindex(BUCKET_ORDER).fillna(0).reset_index()

    y_col = metric_col
    fig2 = px.bar(
        bucket_summary, x="time_bucket", y=y_col,
        title=f"{metric_label} by Time Bucket", text_auto=".2s"
    )
    fig2.update_xaxes(title="Time Bucket")
    fig2.update_yaxes(title=metric_label)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "Late Hours shows zero because the supplied dataset only contains "
        "transactions from 6:00 to 20:00. This reflects the data provided, "
        "not necessarily the store's actual operating hours."
    )
    st.dataframe(
        bucket_summary.style.format({
            "revenue": "${:,.2f}",
            "transaction_qty": "{:,.0f}",
            "transaction_id": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

# ----------------------------------------------------------------------
# Tab 3: Store comparison
# ----------------------------------------------------------------------
with tab3:
    st.subheader("Store Performance Comparison")

    store_summary = fdf.groupby("store_location").agg(
        revenue=("revenue", "sum"),
        transaction_qty=("transaction_qty", "sum"),
        transaction_id=("transaction_id", "nunique"),
    ).reset_index()
    store_summary["avg_transaction_value"] = store_summary["revenue"] / store_summary["transaction_id"]

    y_col = metric_col
    fig3 = px.bar(
        store_summary.sort_values(y_col, ascending=False),
        x="store_location", y=y_col, title=f"{metric_label} by Store", text_auto=".2s"
    )
    fig3.update_xaxes(title="Store")
    fig3.update_yaxes(title=metric_label)
    st.plotly_chart(fig3, use_container_width=True)
    st.dataframe(
        store_summary.style.format({
            "revenue": "${:,.2f}",
            "transaction_qty": "{:,.0f}",
            "transaction_id": "{:,.0f}",
            "avg_transaction_value": "${:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

# ----------------------------------------------------------------------
# Tab 4: Cross-location hourly heatmap
# ----------------------------------------------------------------------
with tab4:
    st.subheader(f"Hourly {metric_label} Heatmap by Store")

    if metric_col == "transaction_id":
        pivot = fdf.pivot_table(
            index="store_location", columns="hour", values="transaction_id",
            aggfunc="nunique", fill_value=0
        )
    else:
        pivot = fdf.pivot_table(
            index="store_location", columns="hour", values=metric_col,
            aggfunc="sum", fill_value=0
        )

    fig4 = px.imshow(
        pivot, text_auto=",.0f", aspect="auto",
        labels=dict(x="Hour of Day", y="Store", color=metric_label),
        color_continuous_scale="Oranges"
    )
    st.plotly_chart(fig4, use_container_width=True)

    peak_by_store = pivot.idxmax(axis=1)
    peak_table = peak_by_store.rename("peak_hour").reset_index()
    peak_table["peak_hour"] = peak_table["peak_hour"].apply(lambda hour: f"{int(hour):02d}:00")
    st.write("**Peak hour per store:**")
    st.dataframe(peak_table, use_container_width=True, hide_index=True)
    if peak_by_store.nunique() == 1:
        st.success("All stores share the same peak hour — demand is aligned across locations.")
    else:
        st.warning("Peak hours differ across stores — demand is location-specific.")

# ----------------------------------------------------------------------
# Tab 5: Product category (supporting analysis)
# ----------------------------------------------------------------------
with tab5:
    st.subheader("Product Category Breakdown (Supporting Analysis)")

    y_col = metric_col
    cat_summary = fdf.groupby("product_category").agg(
        revenue=("revenue", "sum"),
        transaction_qty=("transaction_qty", "sum"),
        transaction_id=("transaction_id", "nunique"),
    ).reset_index().sort_values("revenue", ascending=False)

    fig5 = px.bar(
        cat_summary, x="product_category", y=y_col,
        title=f"{metric_label} by Product Category", text_auto=".2s"
    )
    fig5.update_xaxes(title="Product Category")
    fig5.update_yaxes(title=metric_label)
    st.plotly_chart(fig5, use_container_width=True)
    st.dataframe(
        cat_summary.style.format({
            "revenue": "${:,.2f}",
            "transaction_qty": "{:,.0f}",
            "transaction_id": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )