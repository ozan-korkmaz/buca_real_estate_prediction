# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd 

df = pd.read_csv("buca_emlak_detayli_SATILIK_veriler.csv")

#We check for duplicate values.
link_unique = df['Link'].nunique()
print(link_unique)



pattern = r'https://www.hepsiemlak.com/en/izmir-buca-(.*?)-satilik/'
df['Konum'] = df['Link'].str.extract(pattern, expand=False)

print("\nThe 'Konum' column was populated with the values retrieved from the 'Link' column.")
print(df)





print(df.isnull().sum())
#The 'Number Of Room + Hall' column has roughly fifty percent missing data, and we must first clean the NaN values in that column.
df.dropna(subset=['Number Of Room + Hall'], inplace=True)
print(df.isnull().sum())



NaN_values = df.isnull().sum()


Columns_to_be_dropped = NaN_values[NaN_values >= 300].index

print(f"Columns to be dropped: {Columns_to_be_dropped.tolist()}")

df = df.drop(columns=Columns_to_be_dropped)

print("\nThe process is finished.")
print(df.isnull().sum())


df.to_csv("1-NaN-values-dropped.csv", index=False, encoding="utf-8-sig")
print("File saved successfully: 1-NaN-values-dropped.csv")




















