import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. SETTINGS

CLEAN_PATH = "afficionado_clean.csv"
OUTPUT_DIR = "analysis_outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. LOAD DATA

df = pd.read_csv(CLEAN_PATH)

print("=" * 70)
print("AFFICIONADO COFFEE ROASTERS - SALES ANALYSIS")
print("=" * 70)

print(f"\nDataset shape: {df.shape}")
print(f"Total transactions: {df['transaction_id'].nunique():,}")
print(f"Total revenue: ${df['revenue'].sum():,.2f}")

# 3. HOURLY DEMAND ANALYSIS

def hourly_demand_analysis():

    print("\n" + "=" * 70)
    print("HOURLY DEMAND ANALYSIS")
    print("=" * 70)

    hourly = (
        df.groupby("hour")
        .agg(
            transactions=("transaction_id", "nunique"),
            revenue=("revenue", "sum"),
            quantity=("transaction_qty", "sum")
        )
        .reset_index()
        .sort_values("hour")
    )

    hourly["avg_transaction_value"] = (
        hourly["revenue"] / hourly["transactions"]
    )

    # Save summary table
    hourly.to_csv(
        os.path.join(OUTPUT_DIR, "hourly_summary.csv"),
        index=False
    )

    # Peak and slowest hours
    peak_transaction = hourly.loc[
        hourly["transactions"].idxmax()
    ]

    peak_revenue = hourly.loc[
        hourly["revenue"].idxmax()
    ]

    slowest_transaction = hourly.loc[
        hourly["transactions"].idxmin()
    ]

    print("\nHourly Summary:")
    print(hourly.to_string(index=False))

    print("\nPeak transaction hour:")
    print(
        f"{int(peak_transaction['hour']):02d}:00 "
        f"({int(peak_transaction['transactions']):,} transactions)"
    )

    print("\nPeak revenue hour:")
    print(
        f"{int(peak_revenue['hour']):02d}:00 "
        f"(${peak_revenue['revenue']:,.2f})"
    )

    print("\nSlowest transaction hour:")
    print(
        f"{int(slowest_transaction['hour']):02d}:00 "
        f"({int(slowest_transaction['transactions']):,} transactions)"
    )

    # Chart 1: Hourly Transactions

    plt.figure(figsize=(10, 6))

    plt.plot(
        hourly["hour"],
        hourly["transactions"],
        marker="o"
    )

    plt.title("Hourly Transaction Demand")
    plt.xlabel("Hour of Day")
    plt.ylabel("Number of Transactions")
    plt.xticks(hourly["hour"])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "chart_hourly_transactions.png"
        ),
        dpi=200
    )

    plt.close()

    # Chart 2: Hourly Revenue

    plt.figure(figsize=(10, 6))

    plt.plot(
        hourly["hour"],
        hourly["revenue"],
        marker="o"
    )

    plt.title("Hourly Revenue")
    plt.xlabel("Hour of Day")
    plt.ylabel("Revenue ($)")
    plt.xticks(hourly["hour"])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "chart_hourly_revenue.png"
        ),
        dpi=200
    )

    plt.close()

    return hourly

# 4. TIME-BUCKET ANALYSIS

def time_bucket_analysis():

    print("\n" + "=" * 70)
    print("TIME-BUCKET ANALYSIS")
    print("=" * 70)

    bucket_order = [
        "Morning",
        "Afternoon",
        "Evening",
        "Late Hours"
    ]

    bucket = (
        df.groupby("time_bucket")
        .agg(
            transactions=("transaction_id", "nunique"),
            revenue=("revenue", "sum"),
            quantity=("transaction_qty", "sum")
        )
        .reindex(bucket_order)
        .fillna(0)
        .reset_index()
    )

    bucket["avg_transaction_value"] = (
        bucket["revenue"] /
        bucket["transactions"].replace(0, pd.NA)
    )

    bucket["avg_transaction_value"] = (
        bucket["avg_transaction_value"].fillna(0)
    )

    bucket.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "time_bucket_summary.csv"
        ),
        index=False
    )

    print("\nTime-Bucket Summary:")
    print(bucket.to_string(index=False))

    # Chart: Revenue by Time Bucket

    plt.figure(figsize=(9, 6))

    sns.barplot(
        data=bucket,
        x="time_bucket",
        y="revenue"
    )

    plt.title("Revenue by Time of Day")
    plt.xlabel("Time Bucket")
    plt.ylabel("Revenue ($)")
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "chart_time_bucket_revenue.png"
        ),
        dpi=200
    )

    plt.close()

    return bucket

# 5. STORE ANALYSIS

def store_analysis():

    print("\n" + "=" * 70)
    print("STORE PERFORMANCE ANALYSIS")
    print("=" * 70)

    store_summary = (
        df.groupby("store_location")
        .agg(
            transactions=("transaction_id", "nunique"),
            revenue=("revenue", "sum"),
            quantity=("transaction_qty", "sum")
        )
        .reset_index()
    )

    store_summary["avg_transaction_value"] = (
        store_summary["revenue"] /
        store_summary["transactions"]
    )

    store_summary = store_summary.sort_values(
        "revenue",
        ascending=False
    )

    store_summary.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "store_summary.csv"
        ),
        index=False
    )

    print("\nStore Summary:")
    print(store_summary.to_string(index=False))

    # Peak Hour for Each Store

    store_hour = (
        df.groupby(
            ["store_location", "hour"]
        )
        .agg(
            transactions=("transaction_id", "nunique"),
            revenue=("revenue", "sum")
        )
        .reset_index()
    )

    store_hour.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "store_hour_summary.csv"
        ),
        index=False
    )

    print("\nPeak Hour by Store:")

    peak_rows = []

    for store in store_hour["store_location"].unique():

        store_data = store_hour[
            store_hour["store_location"] == store
        ]

        peak = store_data.loc[
            store_data["transactions"].idxmax()
        ]

        peak_rows.append({
            "store_location": store,
            "peak_hour": int(peak["hour"]),
            "transactions": int(peak["transactions"]),
            "revenue": float(peak["revenue"])
        })

        print(
            f"{store}: "
            f"{int(peak['hour']):02d}:00 "
            f"({int(peak['transactions']):,} transactions)"
        )

    peak_store_hours = pd.DataFrame(peak_rows)

    peak_store_hours.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "peak_hour_by_store.csv"
        ),
        index=False
    )

    # Chart: Store Revenue
    
    plt.figure(figsize=(9, 6))

    sns.barplot(
        data=store_summary,
        x="store_location",
        y="revenue"
    )

    plt.title("Revenue by Store Location")
    plt.xlabel("Store Location")
    plt.ylabel("Revenue ($)")
    plt.xticks(rotation=15)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "chart_store_revenue.png"
        ),
        dpi=200
    )

    plt.close()

    return store_summary, store_hour

# 6. CROSS-LOCATION HEATMAP

def cross_location_heatmap(store_hour):

    print("\n" + "=" * 70)
    print("CROSS-LOCATION HOURLY ANALYSIS")
    print("=" * 70)

    # Transaction Heatmap

    transaction_pivot = store_hour.pivot(
        index="store_location",
        columns="hour",
        values="transactions"
    ).fillna(0)

    transaction_pivot.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "store_hour_transactions.csv"
        )
    )

    plt.figure(figsize=(12, 5))

    sns.heatmap(
        transaction_pivot,
        annot=True,
        fmt=".0f"
    )

    plt.title("Hourly Transactions by Store")
    plt.xlabel("Hour of Day")
    plt.ylabel("Store Location")
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "chart_heatmap_transactions.png"
        ),
        dpi=200
    )

    plt.close()

    # Revenue Heatmap

    revenue_pivot = store_hour.pivot(
        index="store_location",
        columns="hour",
        values="revenue"
    ).fillna(0)

    revenue_pivot.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "store_hour_revenue.csv"
        )
    )

    plt.figure(figsize=(12, 5))

    sns.heatmap(
        revenue_pivot,
        annot=True,
        fmt=".0f"
    )

    plt.title("Hourly Revenue by Store")
    plt.xlabel("Hour of Day")
    plt.ylabel("Store Location")
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "chart_heatmap_revenue.png"
        ),
        dpi=200
    )

    plt.close()

    # Check Peak-Hour Alignment

    peak_hours = {}

    for store in transaction_pivot.index:

        peak_hour = transaction_pivot.loc[
            store
        ].idxmax()

        peak_hours[store] = int(peak_hour)

    print("\nPeak transaction hour by store:")

    for store, hour in peak_hours.items():
        print(f"{store}: {hour:02d}:00")

    unique_peak_hours = set(peak_hours.values())

    if len(unique_peak_hours) == 1:
        print("\nResult: All stores have the same peak transaction hour.")
    else:
        print("\nResult: Peak transaction hours differ across stores.")

# 7. PRODUCT CATEGORY ANALYSIS

def product_analysis():

    print("\n" + "=" * 70)
    print("PRODUCT CATEGORY ANALYSIS")
    print("=" * 70)

    category_summary = (
        df.groupby("product_category")
        .agg(
            transactions=("transaction_id", "nunique"),
            revenue=("revenue", "sum"),
            quantity=("transaction_qty", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    category_summary["avg_transaction_value"] = (
        category_summary["revenue"] /
        category_summary["transactions"]
    )

    category_summary.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "product_category_summary.csv"
        ),
        index=False
    )

    print("\nProduct Category Summary:")
    print(category_summary.to_string(index=False))

    return category_summary

# 8. MAIN PROGRAM

def main():

    hourly_demand_analysis()

    time_bucket_analysis()

    store_summary, store_hour = store_analysis()

    cross_location_heatmap(store_hour)

    product_analysis()

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print(
        f"\nAll charts and summary tables were saved in:"
        f"\n{OUTPUT_DIR}"
    )

    print(
        "\nNOTE:"
        "\nThe dataset contains no transaction date column."
        "\nTherefore, day-of-week, weekday/weekend, daily,"
        "\nand weekly sales trends cannot be calculated reliably."
    )


# RUN

if __name__ == "__main__":
    main()