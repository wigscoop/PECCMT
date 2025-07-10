import streamlit as st
import pandas as pd
import json

# Set the title of the app
st.title("CSV Column Matcher")

template_col, match_col = st.columns(2)

with template_col:
    # File uploader widget
    template_file = st.file_uploader("🧾 Choose a template CSV file", type="csv", key="template")

    # If a file is uploaded
    if template_file is not None:
        try:
            # Read the CSV file into a DataFrame
            template_dataframe = pd.read_csv(template_file, comment='#')

            # Display the DataFrame
            st.subheader("📊 Preview of template CSV")
            st.dataframe(template_dataframe)

            # Show basic info
            with st.expander("🧾 File Summary"):
                st.write(f"Number of rows: {template_dataframe.shape[0]}")
                st.write(f"Number of columns: {template_dataframe.shape[1]}")
                st.write("Column names:", list(template_dataframe.columns))
        except Exception as e:
            st.error(f"Error reading the CSV file: {e}")
    else:
        st.info("Please upload a template CSV file.")

with match_col:
    # File uploader widget
    file_to_match = st.file_uploader("🧾 Choose a CSV file to match", type="csv", key="to_match")

    # If a file is uploaded
    if file_to_match is not None:
        try:
            # Read the CSV file into a DataFrame
            match_dataframe = pd.read_csv(file_to_match, comment='#')
            
            # Display the DataFrame
            st.subheader("📊 Preview of CSV to match")
            st.dataframe(match_dataframe)

            # Show basic info
            with st.expander("🧾 File Summary"):
                st.write(f"Number of rows: {match_dataframe.shape[0]}")
                st.write(f"Number of columns: {match_dataframe.shape[1]}")
                st.write("Column names:", list(match_dataframe.columns))
        except Exception as e:
            st.error(f"Error reading the CSV file: {e}")
    else:
        st.info("Please upload a CSV file to match.")

if template_file is not None and file_to_match is not None:
    st.subheader("🔄 Match Columns and Export")

    # Get template and target column names
    template_columns = list(template_dataframe.columns)
    match_columns = list(match_dataframe.columns)

    st.markdown("### 🧮 Column Comparison")
    comparison_dataframe = pd.DataFrame({
        "Template Columns": template_columns,
        "To Match Columns": match_columns + [""] * (len(template_columns) - len(match_columns))
    })
    st.dataframe(comparison_dataframe)

    # Create a mapping interface
    with st.expander("### 🔧 Column Mapping"):
        column_mapping = {}
        saved_mapping = {}

        uploaded_mapping = st.file_uploader("🧾(OPTIONAL) Upload a saved column mapping", type="json")
        if uploaded_mapping:
            try:
                saved_mapping = json.load(uploaded_mapping)
                st.success("✅ Mapping downloaded successfully!")
            except Exception as e:
                st.error(f"Error reading the JSON file: {e}")

        # Create a mapping interface
        for col in template_columns:
            default_index = 0  # "-- None --"

            if col in saved_mapping and saved_mapping[col] in match_columns:
                default_index = match_columns.index(saved_mapping[col]) + 1  # +1 because of "-- None --"
            elif col in match_columns:
                # Preselect if there's an exact match
                default_index = match_columns.index(col) + 1  # +1 because of "-- None --"

            # Dropdown to select matching column from match_dataframe
            selected = st.selectbox(
                f"Match template column '{col}' with:",
                options=["-- None --"] + match_columns,
                key=f"map_{col}",
                index=default_index
            )
            if selected != "-- None --":
                column_mapping[col] = selected
    
    # Button to generate matched CSV
    if st.button("📤 Generate Matched CSV"):
        try:
            # Create a new DataFrame with matched columns
            matched_dataframe = pd.DataFrame()

            for template_col, source_col in column_mapping.items():
                matched_dataframe[template_col] = match_dataframe[source_col]

            # Show preview
            st.success("✅ Columns matched successfully!")
            st.dataframe(matched_dataframe)

            mapping_json = json.dumps(column_mapping)
            if st.download_button("💾 Download Mapping", mapping_json, file_name="column_mapping.json"):
                st.success("✅ Mapping downloaded successfully!")

            # Download button
            csv = matched_dataframe.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Matched CSV",
                data=csv,
                file_name="matched_output.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error generating matched CSV: {e}")