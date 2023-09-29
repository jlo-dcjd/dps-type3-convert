import streamlit as st
import pandas as pd
import os
from io import StringIO

st.title('DPS Re-Arrest Data Into Type3 File')

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

    # Initialize counters and lists
    type_counts = {'Type1': 0, 'Type2': 0, 'Type3': 0, 'Type4': 0, 'Type5': 0, 'Type6': 0, 'Type7': 0}

    type3_lines = []

    for line in stringio:
        line_type = line[0]

        # Update counters and lists based on line type
        if line_type == '1':
            type_counts['Type1'] += 1
        elif line_type == '2':
            type_counts['Type2'] += 1
        elif line_type == '3':
            type_counts['Type3'] += 1
            type3_lines.append(line)
        elif line_type == '4':
            type_counts['Type4'] += 1
        elif line_type == '5':
            type_counts['Type5'] += 1
        elif line_type == '6':
            type_counts['Type6'] += 1
        elif line_type == '7':
            type_counts['Type7'] += 1

    df = pd.DataFrame(type_counts.items(), columns=['Type', 'Total'])

    st.dataframe(df)

    st.markdown(f"## Total Lines Read: {df.Total.sum()}")

    delimiter_positions = [1, 9, 17, 18, 22, 30, 38, 84, 101, 103, 104, 107, 139, 147, 156, 157, 158, 159]

    output_lines = ["type;Sid;doa;seq_code;trs;doo;aon;aol;blank;lda;goc;adn;add;ada;prosec_ori;blank2;blank3;dm_viol;victim_age\n"]

    for line in type3_lines:
        output_line = []
        for i, char in enumerate(line):
            if i in delimiter_positions:
                output_line.append(";")
            output_line.append(char)

        output_lines.append("".join(output_line))

    # Split the header and data lines
    header = output_lines[0]
    data_lines = output_lines[1:]

    # Split each data line by the delimiter (;) and create a list of lists
    data = [line.strip().split(';') for line in data_lines]

    # Create a Pandas DataFrame
    df = pd.DataFrame(data, columns=header.strip().split(';'))
    df['aol_lookup'] = ''
    df = df[['type', 'Sid', 'doa', 'doo', 'aon', 'aol', 'aol_lookup', 'lda', 'ada', 'prosec_ori']]
    df['doa'] = pd.to_datetime(df['doa'], format='%Y%m%d', errors='coerce').dt.strftime('%m/%d/%Y')
    df['doo'] = pd.to_datetime(df['doo'], format='%Y%m%d', errors='coerce').dt.strftime('%m/%d/%Y')
    df['ada'] = pd.to_datetime(df['ada'], format='%Y%m%d', errors='coerce').dt.strftime('%m/%d/%Y')

    # add missing offense descriptions
    tjjd = pd.read_excel('TJJD_OffenseCodes.xlsx', converters={'OffenseCode': str, 'TJPCCategory': str, 'TJPCAttemptedCategory': str})

    for index, row in df.iterrows():
        aon_value = row['aon']

        # Search for matching 'OffenseCode' in tjjd
        matching_row = tjjd[tjjd['OffenseCode'] == aon_value]

        # If a match is found, update 'aol' with 'OffenseDescription'
        if not matching_row.empty:
            df.at[index, 'aol_lookup'] = matching_row['OffenseDescription'].iloc[0]

    st.dataframe(df)

    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='type3.csv',
        mime='text/csv',
    )

    st.success("Processing completed!")
