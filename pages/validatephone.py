import streamlit as st
import pandas as pd
from io import StringIO
import io
import re
import phonenumbers
from phonenumbers import NumberParseException
import matplotlib.pyplot as plt
import pycountry

# pip install matplotlib
# pip install phonenumbers
# pip install pycountry
# records for testing: +8613912345678,  +8615012345678,  18612345678, +6591234567,  87654321, +60123456789, 191234567, +12025550123 , +13105550123, +14155550123

st.title("Validate Phone Numbers")

st.markdown(""" ### 🚀 Getting Started
1. **Select the region** you want to validate against.  
2. **Enter phone numbers manually** or **upload one or more CSV files** for validation.
""")

# Function: Normalize phone numbers to a standard format
def normalize_phone_number(phone_number):
    # Remove non-numeric characters
    normalized_number = re.sub(r'\D', '', phone_number)
    return normalized_number

# Function: Validate phone number where default region is None and to specify in the later part
def validate_phone_number(phone_number, default_region='US'):
    try:
        if default_region:
            phone_number_obj = phonenumbers.parse(phone_number, default_region)
        else:
            phone_number_obj = phonenumbers.parse(phone_number)
    
        if phonenumbers.is_valid_number(phone_number_obj):
            # return valid phone numbers with standardized E164 format
            # return True, phonenumbers.format_number(phone_number_obj, phonenumbers.PhoneNumberFormat.E164)
            return 'valid'
        else:
            # return original phone number
            return 'invalid'
    except NumberParseException:
        # return original phone number
        return 'invalid'

def normalize_visualize(final_df):

    # Custom function for count + percentage
    def make_autopct(sizes):
        def autopct(pct):
            count = int(round(pct * total / 100.0))
            return f'{count} ({pct:.1f}%)'
        return autopct

    # Normalize each phone number and replace value in the column
    final_df['normalized_phone_number'] = [normalize_phone_number(num) for num in final_df['phone_number']]

    #  Validate phone number using phonenumbers library
    st.header('Normalized and Validated Records (De-dup)')
    final_df['valid'] = [validate_phone_number(num, default_region=selected_code) for num in final_df['normalized_phone_number']]
    final_df

    # Convert DataFrame to CSV
    csv = final_df.to_csv(index=False).encode('utf-8')

    # Download button
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='output_data.csv',
        mime='text/csv',
        key='text_download'
    )

    st.header("Valid vs Invalid Status Visualization")

    # Value counts
    value_counts = final_df['valid'].value_counts(dropna=False)
    labels = value_counts.index
    sizes = value_counts.values
    total = sum(sizes)

    # Pie chart
    fig, ax = plt.subplots(figsize=(3, 3))
    colors = ['green' if val == 'valid' else 'red' for val in labels]
    ax.pie(
        sizes,
        labels=labels,
        autopct=make_autopct(sizes),
        startangle=90,
        colors=colors,
        textprops={'fontsize': 8})

    # Equal aspect ratio ensures pie is circular
    ax.axis('equal')

    plt.tight_layout()  # Trim whitespace

    # Layout in narrow column
    col1, col2, _ = st.columns([2, 1, 1])  # Left-aligned smaller box
    with col1:
        st.pyplot(fig)

# Get supported region codes from phonenumbers
region_codes = sorted(phonenumbers.SUPPORTED_REGIONS)

# Map codes to full country names
region_names = []
code_to_name = {}

for code in region_codes:
    country = pycountry.countries.get(alpha_2=code)
    name = country.name if country else "Unknown"
    display = f"{name} ({code})"
    region_names.append(display)
    code_to_name[display] = code  # mapping display to code

# Streamlit dropdown
st.markdown(""" ### 🌍 Choose a Region """)
selected_region = st.selectbox("Select a region before proceeding (default: 'US')", region_names)

# Show selected region and code
st.write(f"You selected: {selected_region}")
selected_code = code_to_name[selected_region]

st.markdown(""" ### 📞 Input Phone Numbers """)
field_name = st.text_input('Manually enter Phone Numbers (separated with commas)')
# Split by comma and strip whitespace
phone_list = [s.strip() for s in field_name.split(',')]

if field_name:
    df = pd.DataFrame(phone_list, columns=['phone_number'])

    # Remove duplicated records
    final_df = df.drop_duplicates()

    normalize_visualize(final_df)

st.markdown(""" ### 📂 CSV Upload """)
st.write('Note: You can upload multi-part datasets, but ensure all parts use the same schema to merge them correctly.')

# File uploader (allowing multiple files to be uploaded)
uploaded_files = st.file_uploader("Upload CSV files for Validation", type=["csv"], accept_multiple_files=True)

try:

    if uploaded_files:
        dfs = []
        for uploaded_file in uploaded_files:

            # st.write(f"Reading file: {uploaded_file.name}")
            df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
            dfs.append(df)

        # Merge all DataFrames
        final_df = pd.concat(dfs, ignore_index=True)

        # Remove duplicated records
        final_df = final_df.drop_duplicates()

        # Create a narrow layout using columns
        col1, col2, _ = st.columns([3, 2, 1])  # Adjust ratios as needed
        with col1:
            st.write("📋 Preview of Uploaded File(s) (De-dup)")
            st.dataframe(final_df.head(10), use_container_width=False)

        # Try to access 'phone' column
        if 'phone_number' not in df.columns:
            raise ValueError("'phone_number' column not found")
        else:
            # Normalize each phone number and replace value in the column
            final_df['normalized_phone_number'] = [normalize_phone_number(num) for num in final_df['phone_number']]

            #  Validate phone number using phonenumbers library
            st.text('Normalized and Validated Records (De-dup)')
            final_df['valid'] = [validate_phone_number(num, default_region=selected_code) for num in final_df['normalized_phone_number']]
            st.dataframe(final_df)

            # Convert DataFrame to CSV
            csv = final_df.to_csv(index=False).encode('utf-8')

            # Download button
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name='output_data.csv',
                mime='text/csv',
                key='fileupload1_download'
            )

            st.header("Valid vs Invalid Status Visualization")

            # Value counts
            value_counts = final_df['valid'].value_counts(dropna=False)
            labels = value_counts.index
            sizes = value_counts.values
            total = sum(sizes)

            # Pie chart
            fig, ax = plt.subplots(figsize=(3, 3))
            colors = ['green' if val == 'valid' else 'red' for val in labels]
            ax.pie(
                sizes,
                labels=labels,
                autopct=make_autopct(sizes),
                startangle=90,
                colors=colors,
                textprops={'fontsize': 8})

            # Equal aspect ratio ensures pie is circular
            ax.axis('equal')

            plt.tight_layout()  # Trim whitespace

            # Layout in narrow column
            col1, col2, _ = st.columns([2, 1, 1])  # Left-aligned smaller box
            with col1:
                st.pyplot(fig)

except Exception as e:
        
    # Text Box to copy and paste list of phone numbers
    field_name = st.text_input('Specify Field Name to be renamed as phone_number:')

    if field_name:
        if field_name in final_df.columns:
            # Rename column name to phone_numbers
            final_df.rename(columns={field_name: 'phone_number'}, inplace=True)
            st.success(f"✅ Column '{field_name}' renamed to 'phone_number'.")
            
            # Normalize each phone number and replace value in the column
            final_df['normalized_phone_number'] = [normalize_phone_number(num) for num in final_df['phone_number']]

            #  Validate phone number using phonenumbers library
            st.text('Normalized and Validated Records (De-dup)')
            final_df['valid'] = [validate_phone_number(num, default_region=selected_code) for num in final_df['normalized_phone_number']]
            st.dataframe(final_df)

            # Convert DataFrame to CSV
            csv = final_df.to_csv(index=False).encode('utf-8')

            # Download button
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name='output_data.csv',
                mime='text/csv',
                key='fileupload2_download'
            )

            st.header("Valid vs Invalid Status Visualization")

            # Value counts
            value_counts = final_df['valid'].value_counts(dropna=False)
            labels = value_counts.index
            sizes = value_counts.values
            total = sum(sizes)

            # Pie chart
            fig, ax = plt.subplots(figsize=(3, 3))
            colors = ['green' if val == 'valid' else 'red' for val in labels]
            ax.pie(
                sizes,
                labels=labels,
                autopct=make_autopct(sizes),
                startangle=90,
                colors=colors,
                textprops={'fontsize': 8})

            # Equal aspect ratio ensures pie is circular
            ax.axis('equal')

            plt.tight_layout()  # Trim whitespace

            # Layout in narrow column
            col1, col2, _ = st.columns([2, 1, 1])  # Left-aligned smaller box
            with col1:
                st.pyplot(fig)
            
        else:
            st.warning(f"⚠️ Column '{field_name}' not found in the file.")