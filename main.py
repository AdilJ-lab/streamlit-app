import streamlit as st
import pandas as pd
import numpy as np
import time

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="CSV Health Inspector",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------

def calculate_metrics(df):
    """Calculate high-level dataset metrics."""

    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = total_rows * total_columns

    missing_cells = df.isna().sum().sum()
    complete_cells = total_cells - missing_cells

    completeness = (
        complete_cells / total_cells * 100
        if total_cells > 0
        else 0
    )

    duplicate_rows = df.duplicated().sum()

    return {
        "rows": total_rows,
        "columns": total_columns,
        "missing_cells": missing_cells,
        "complete_cells": complete_cells,
        "completeness": completeness,
        "duplicates": duplicate_rows
    }


def create_missing_summary(df):
    """Create missing-value summary for each column."""

    missing_counts = df.isna().sum()

    missing_summary = pd.DataFrame({
        "Missing Count": missing_counts,
        "Percentage (%)": (
            missing_counts / len(df) * 100
        ).round(2)
    })

    return missing_summary.sort_values(
        by="Missing Count",
        ascending=False
    )


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📊 CSV Health Inspector")

st.caption(
    "Need to audit or analyze your data file to ensure it is "
    "providing HIGH-QUALITY data? Use this simple tool to "
    "understand your datasets better."
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Your .csv File For Inspection",
    type=["csv"]
)


# --------------------------------------------------
# DATA PROCESSING
# --------------------------------------------------

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

    except Exception as error:
        st.error(f"Unable to read this CSV file: {error}")
        st.stop()

    metrics = calculate_metrics(df)

    # --------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------

    st.markdown("---")
    st.subheader("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Rows",
        f"{metrics['rows']:,}"
    )

    col2.metric(
        "Total Columns",
        f"{metrics['columns']:,}"
    )

    col3.metric(
        "Missing Cells",
        f"{metrics['missing_cells']:,}"
    )

    col4.metric(
        "Duplicate Rows",
        f"{metrics['duplicates']:,}"
    )

    st.metric(
        "Dataset Completeness",
        f"{metrics['completeness']:.2f}%"
    )

    # --------------------------------------------------
    # DETAILED ANALYSIS
    # --------------------------------------------------

    st.markdown("---")
    st.subheader("Detailed Analysis")

    tab1, tab2, tab3 = st.tabs([
        "🔍 Missing Value Breakdown",
        "👯 Duplicate Explorer",
        "👀 Raw Data Preview"
    ])

    # --------------------------------------------------
    # TAB 1 — MISSING VALUES
    # --------------------------------------------------

    with tab1:

        st.markdown("#### Missing Data per Column")

        missing_df = create_missing_summary(df)

        st.dataframe(
            missing_df.style.background_gradient(
                cmap="Reds",
                subset=["Missing Count"]
            ),
            use_container_width=True
        )

    # --------------------------------------------------
    # TAB 2 — DUPLICATES
    # --------------------------------------------------

    with tab2:

        st.markdown("#### Duplicate Rows Found")

        duplicate_rows = metrics["duplicates"]

        if duplicate_rows > 0:

            st.warning(
                f"Found {duplicate_rows:,} exact duplicate rows."
            )

            duplicate_data = df[
                df.duplicated(keep=False)
            ]

            st.dataframe(
                duplicate_data,
                use_container_width=True
            )

            if st.button("Preview Data with Duplicates Removed"):

                cleaned_df = df.drop_duplicates()

                st.success(
                    f"Duplicates removed. "
                    f"{len(cleaned_df):,} rows remaining."
                )

                st.dataframe(
                    cleaned_df,
                    use_container_width=True
                )

        else:

            st.success(
                "🎉 No duplicate rows found in this dataset!"
            )

    # --------------------------------------------------
    # TAB 3 — RAW DATA
    # --------------------------------------------------

    with tab3:

        st.markdown("#### First 50 Rows")

        st.dataframe(
            df.head(50),
            use_container_width=True
        )

else:

    st.info(
        "👆 Upload a CSV file above to begin your data inspection."
    )
# --------------------------------------------------
# REQUIRED HEADER AUDIT
# --------------------------------------------------

st.markdown("---")
st.subheader("Required Headers Audit")

st.write(
    "Enter the column headers that your dataset is expected to contain."
)

required_headers_input = st.text_area(
    "Required Headers",
    placeholder="SKU, UPC, Product Description, Cost, MSRP, MAP, Category, Image URL",
    help="Separate each required header with a comma."
)

if required_headers_input:

    # Convert user input into a list
    required_headers = [
        header.strip()
        for header in required_headers_input.split(",")
        if header.strip()
    ]

    # Existing dataframe headers
    existing_headers = df.columns.tolist()

    # Compare required headers against dataframe headers
    header_results = []

    for header in required_headers:

        if header in existing_headers:
            status = "Found"
        else:
            status = "Missing"

        header_results.append({
            "Required Header": header,
            "Status": status
        })

    header_results_df = pd.DataFrame(header_results)

    # --------------------------------------------------
    # HEADER COUNTS
    # --------------------------------------------------

    found_count = (
        header_results_df["Status"] == "Found"
    ).sum()

    missing_count = (
        header_results_df["Status"] == "Missing"
    ).sum()

    total_required = len(required_headers)

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Required Headers",
        total_required
    )

    col2.metric(
        "Headers Found",
        found_count
    )

    col3.metric(
        "Headers Missing",
        missing_count
    )

    # --------------------------------------------------
    # COMPLETENESS
    # --------------------------------------------------

    header_completion = (
        found_count / total_required * 100
        if total_required > 0
        else 0
    )

    st.progress(
        header_completion / 100,
        text=f"Header Coverage: {header_completion:.1f}%"
    )

    # --------------------------------------------------
    # RESULTS TABLE
    # --------------------------------------------------

    display_df = header_results_df.copy()

    display_df["Status"] = display_df["Status"].map({
        "Found": "✅ Found",
        "Missing": "❌ Missing"
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # VISUAL SUMMARY
    # --------------------------------------------------

    chart_data = pd.DataFrame({
        "Status": ["Found", "Missing"],
        "Count": [found_count, missing_count]
    })

    st.bar_chart(
        chart_data.set_index("Status")
    )

    # --------------------------------------------------
    # MISSING HEADER LIST
    # --------------------------------------------------

    missing_headers = header_results_df.loc[
        header_results_df["Status"] == "Missing",
        "Required Header"
    ].tolist()

    if missing_headers:

        st.warning(
            f"{missing_count} required header(s) are missing."
        )

        st.write(
            "Missing headers:",
            ", ".join(missing_headers)
        )

    else:

        st.success(
            "🎉 All required headers are present!"
        )

#sidebar selection for user
analysis_type = st.sidebar.selectbox(
    "What are you analyzing data for today?",
    (
        "💼 Work",
        "🏠 Personal-use",
        "🧪 Just For Fun"
    )
)

if analysis_type == "💼 Work":
    st.info("Work analysis mode selected.")

elif analysis_type == "🏠 Personal-use":
    st.info("Personal-use analysis mode selected.")

elif analysis_type == "🧪 Just For Fun":
    st.info("Just For Fun mode selected.")
    
if analysis_type == "💼 Work":

    st.sidebar.success("✅ Work mode active")

    required_headers = [
        "Parent SKU",
        "Variant SKU",
        "Parent Description",
        "Size",
        "Color",
        "MSRP",
        "Cost",
        "MAP",
        "Weight",
        "UPC",
        "Category",
        "Image URLs",
        "Dimensions"
    ]

elif analysis_type == "🏠 Personal-use":

    st.sidebar.success("✅ Personal mode active")

    required_headers = [
        "Name",
        "Category",
        "Price",
        "Date"
    ]

else:

    st.sidebar.success("✅ Fun mode active")

    required_headers = [
        "Name",
        "Value"
    ]    