import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Smart Data Dashboard", layout="wide")

st.title("📊 Smart Data Analytics Dashboard")

# ---------------- File Upload ----------------

file = st.sidebar.file_uploader("Upload Dataset", type=["csv","xlsx","xls","json"])

if file:

    ext = file.name.split(".")[-1].lower()

    if ext == "csv":
        df = pd.read_csv(file)

    elif ext in ["xlsx","xls"]:
        df = pd.read_excel(file)

    elif ext == "json":
        df = pd.read_json(file)

    else:
        st.error("Unsupported file format")
        st.stop()

    st.success("Dataset Loaded Successfully")

    st.write("### Dataset Preview")
    st.dataframe(df.head())

    # ---------------- Column Detection ----------------

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]

    # ---------------- Filters ----------------

    st.sidebar.header("Filters")

    filtered_df = df.copy()

    for col in cat_cols:

        values = df[col].dropna().unique()

        if len(values) < 50:

            selected = st.sidebar.multiselect(col, values)

            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]

    # ---------------- Download ----------------

    st.sidebar.download_button(
        "Download Filtered Data",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_data.csv"
    )

    # ---------------- KPI CARDS ----------------

    st.write("## Key Metrics")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total Records", len(filtered_df))
    c2.metric("Columns", len(filtered_df.columns))
    c3.metric("Numeric Columns", len(num_cols))
    c4.metric("Categorical Columns", len(cat_cols))

    # ---------------- Tabs ----------------

    tab1,tab2,tab3,tab4 = st.tabs([
        "📈 Overview",
        "📊 Category Analysis",
        "📉 Correlation",
        "🧠 Insights"
    ])

# ---------------- Overview ----------------

    with tab1:

        st.subheader("Numerical Distributions")

        if num_cols:

            col = st.selectbox("Select column", num_cols)

            fig = px.histogram(
                filtered_df,
                x=col,
                nbins=30,
                color_discrete_sequence=["royalblue"]
            )

            st.plotly_chart(fig,use_container_width=True)

        # Trend chart

        if date_cols and num_cols:

            st.subheader("Trend Analysis")

            date_col = st.selectbox("Date column", date_cols)
            metric = st.selectbox("Metric", num_cols)

            try:

                filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])

                trend = filtered_df.groupby(date_col)[metric].sum().reset_index()

                fig = px.line(
                    trend,
                    x=date_col,
                    y=metric,
                    markers=True
                )

                st.plotly_chart(fig,use_container_width=True)

            except:
                st.warning("Date column format issue")

# ---------------- Category Analysis ----------------

    with tab2:

        if cat_cols:

            category = st.selectbox("Select Category", cat_cols)

            if num_cols:

                metric = st.selectbox("Select Metric", num_cols)

                data = filtered_df.groupby(category)[metric].mean().reset_index()

                fig = px.bar(
                    data,
                    x=category,
                    y=metric,
                    color=metric
                )

                st.plotly_chart(fig,use_container_width=True)

            else:

                fig = px.histogram(filtered_df,x=category)

                st.plotly_chart(fig,use_container_width=True)

        else:
            st.info("No categorical columns")

# ---------------- Correlation ----------------

    with tab3:

        if len(num_cols) > 1:

            corr = filtered_df[num_cols].corr()

            fig = px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale="RdBu_r"
            )

            st.plotly_chart(fig,use_container_width=True)

        else:
            st.info("Need more numeric columns")

# ---------------- Insights ----------------

    with tab4:

        insights = []

        insights.append(f"Dataset has {len(df)} rows")
        insights.append(f"Total columns: {len(df.columns)}")

        if num_cols:
            insights.append(f"{len(num_cols)} numeric columns detected")

        if cat_cols:
            insights.append(f"{len(cat_cols)} categorical columns detected")

        if date_cols:
            insights.append("Time based analysis possible")

        for col in num_cols[:3]:

            try:
                mean = filtered_df[col].mean()
                insights.append(f"Average {col} is {mean:.2f}")
            except:
                pass

        for i in insights:
            st.write("•",i)

else:

    st.info("Upload a dataset to generate dashboard")