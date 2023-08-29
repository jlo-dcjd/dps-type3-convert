import streamlit as st
import pandas as pd
import os

st.title('Separate Re-Arrest Data Into Type3 File')

file_name = st.text_input('Enter the file name for the re-arrest file (DO NOT include .txt extension)', key='file_name')

if st.button('Process'):
    # Record Type File Creation and Headers
    Type_3 = open('Type3.txt', "w", encoding="utf8")
    results = open('verify.txt', "w", encoding="utf8")

    # Original DPS Return file, Read Only
    try:
        File = open("{}.txt".format(file_name), "r", encoding="utf8")
    except FileNotFoundError:
        st.error("File not found. Please make sure the file is in the same directory.")

    Type1 = 0
    Type2 = 0
    Type3 = 0
    Type4 = 0
    Type5 = 0
    Type6 = 0
    Type7 = 0
    LineCount = 0
    type1_list = []
    type3_list = []

    for Line in File:
        if Line[0] == '1':  # Type 1 Record.
            Type1 += 1
            type1_list.append(Line)
        if Line[0] == '3':  # Type 3 Record.
            Type3 += 1
            Type_3.write(Line)
            type3_list.append(Line)

        if Line[0] == '2':
            Type2 += 1
        if Line[0] == '4':
            Type4 += 1
        if Line[0] == '5':
            Type5 += 1
        if Line[0] == '6':
            Type6 += 1
        if Line[0] == '7':
            Type7 += 1

        LineCount += 1

    TotalRecords = Type1 + Type2 + Type3 + Type4 + Type5 + Type6 + Type7

    # Output number of lines read and sorted
    results.write("Total Lines read: {} \n".format(LineCount))
    results.write("\n")
    results.write("File Type       Total \n")
    results.write("===================== \n")
    results.write("   1            {} \n".format(Type1))
    results.write("   2            {} \n".format(Type2))
    results.write("   3            {} \n".format(Type3))
    results.write("   4            {} \n".format(Type4))
    results.write("   5            {} \n".format(Type5))
    results.write("   6            {} \n".format(Type6))
    results.write("   7            {} \n".format(Type7))
    results.write("\n")
    results.write("Total number of records is: {} \n".format(TotalRecords))
    results.write("\n")
    results.write("First Row Name: {}".format(type1_list[0][35:60]))
    results.write("\n")
    results.write("Last Row Name: {}".format(type1_list[-1][35:60]))

    Type_3.close()
    results.close()

    # Make type3 finished
    File = open("Type3.txt", "r", encoding="utf8")  # Result from DPS_Return
    Type3 = open("Type3_Finished.txt", "w", encoding="utf8")  # New Type 3 file

    Type3.write("type;Sid;doa;seq_code;trs;doo;aon;aol;blank;lda;goc;adn;add;ada;prosec_ori;blank2;blank3;dm_viol;victim_age \n")

    for Line in File:
        i = 0
        LineHold = Line

        for Character in LineHold:
            if i == 1 or i == 9 or i == 17 or i == 18 or i == 22 or i == 30 or i == 38 or i == 84 or i == 101 or i == 103 or i == 104 or i == 107 or i == 139 or i == 147 or i == 156 or i == 157 or i == 158 or i == 159:
                Type3.write(";")

            Type3.write(LineHold[i])
            i += 1

    File.close()
    Type3.close()

    # Remove old files
    os.remove("Type3.txt")

    st.success("Processing completed!")

df = pd.read_csv('Type3_Finished.txt', delimiter=';')

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='type3.csv',
    mime='text/csv',
)

st.dataframe(df)