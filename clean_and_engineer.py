import pandas as pd

RAW_PATH = "Afficionado Coffee Roasters.xlsx - Transactions.csv"
CLEAN_PATH = "afficionado_clean.csv"


def load_data(path):
    print(f"Loading data from {path} ...")
    df = pd.read_csv(path)
    print(f"  Loaded {len(df):,} rows, {df.shape[1]} columns")
    return df


def validate_data(df):
    print("\nValidating data...")
    issues = []

    # Missing values
    missing = df.isnull().sum()
    total_missing = missing.sum()
    if total_missing > 0:
        issues.append(f"{total_missing} missing values found")
        print(f"  WARNING: missing values found:\n{missing[missing > 0]}")
    else:
        print("  OK: no missing values")

    # Duplicate transaction IDs
    dupes = df["transaction_id"].duplicated().sum()
    if dupes > 0:
        issues.append(f"{dupes} duplicate transaction_id values")
        print(f"  WARNING: {dupes} duplicate transaction_id values")
    else:
        print("  OK: no duplicate transaction_id values")

    # Logical consistency: positive quantities and prices
    bad_qty = (df["transaction_qty"] <= 0).sum()
    bad_price = (df["unit_price"] <= 0).sum()
    if bad_qty > 0:
        issues.append(f"{bad_qty} rows with non-positive transaction_qty")
        print(f"  WARNING: {bad_qty} rows with non-positive transaction_qty")
    else:
        print("  OK: all transaction_qty values are positive")
    if bad_price > 0:
        issues.append(f"{bad_price} rows with non-positive unit_price")
        print(f"  WARNING: {bad_price} rows with non-positive unit_price")
    else:
        print("  OK: all unit_price values are positive")

    # Validate transaction_time parses correctly
    try:
        pd.to_datetime(df["transaction_time"], format="%H:%M:%S")
        print("  OK: transaction_time values are valid HH:MM:SS")
    except Exception as e:
        issues.append(f"transaction_time parsing failed: {e}")
        print(f"  WARNING: transaction_time parsing failed: {e}")

    # Confirm no date column exists (documented limitation)
    date_like_cols = [c for c in df.columns if "date" in c.lower()]
    if date_like_cols:
        print(f"  NOTE: found date-like column(s): {date_like_cols} -> re-check whether day-of-week analysis is possible")
    else:
        print("  NOTE: no date column present -> day-of-week / daily-trend analysis will be skipped (documented limitation)")

    if issues:
        print(f"\n{len(issues)} data quality issue(s) found. Review before proceeding.")
    else:
        print("\nAll validation checks passed.")

    return issues


def engineer_features(df):
    print("\nEngineering features...")
    df = df.copy()

    # Revenue per transaction
    df["revenue"] = df["transaction_qty"] * df["unit_price"]

    # Parse transaction_time into a proper time object, then extract hour
    parsed_time = pd.to_datetime(df["transaction_time"], format="%H:%M:%S")
    df["hour"] = parsed_time.dt.hour
    df["minute"] = parsed_time.dt.minute

    # Time-of-day bucket, per assignment spec:
    # Morning 6-11, Afternoon 12-16, Evening 17-21, Late 22-5
    def bucket(hour):
        if 6 <= hour <= 11:
            return "Morning"
        elif 12 <= hour <= 16:
            return "Afternoon"
        elif 17 <= hour <= 21:
            return "Evening"
        else:
            return "Late Hours"

    df["time_bucket"] = df["hour"].apply(bucket)

    print("  Added columns: revenue, hour, minute, time_bucket")
    print(f"  Time bucket distribution:\n{df['time_bucket'].value_counts()}")

    return df


def summarize(df):
    print("\n--- Quick Summary ---")
    print(f"Total revenue: ${df['revenue'].sum():,.2f}")
    print(f"Total transactions: {len(df):,}")
    print(f"Total quantity sold: {df['transaction_qty'].sum():,}")
    print(f"Average transaction revenue: ${df['revenue'].mean():.2f}")
    print(f"Stores: {df['store_location'].nunique()} -> {sorted(df['store_location'].unique())}")
    print(f"Hour range in data: {df['hour'].min()}:00 - {df['hour'].max()}:00")


def main():
    df = load_data(RAW_PATH)
    issues = validate_data(df)
    df = engineer_features(df)
    summarize(df)

    df.to_csv(CLEAN_PATH, index=False)
    print(f"\nCleaned dataset saved to: {CLEAN_PATH}")
    print(f"Final shape: {df.shape}")

    if issues:
        print("\nReminder: the following data quality issues were found and NOT auto-fixed:")
        for i in issues:
            print(f"  - {i}")


if __name__ == "__main__":
    main()