#*******************ACTIONS TAKEN*******************
# Dropped unnecessary columns: 'Link', 'Baslik', 'Listing No', and 'Listing status'.
# Filtered 'Residence Type' to keep only 'Apartment' and dropped the column as it became redundant.
# Dropped the 'Facade' column due to a high number of missing (NaN) values.
# Filtered 'Number Of Room + Hall' to keep only '1 + 1', '2 + 1', and '3 + 1' configurations.
# Removed rows where 'Number of Bathrooms' was equal to 3.
# Dropped the 'Loan Availability' column.
# Filtered out specific unwanted types from the 'Title Deed Status' column.
# Removed rows with 'Unspecified' values in the 'Usage Status' column.
# Dropped the 'Swap' column and saved the processed dataframe to a new CSV file.


import pandas as pd

df2 = pd.read_csv("1-NaN-values-dropped.csv")

#we used column 'Link' for column 'Konum'.
print("---------- LINK ----------")
df2 = df2.drop(columns=['Link'])
print("The 'Link' column was dropped.")

print("----------------------")

print("---------- BASLIK ----------")
df2 = df2.drop(columns=['Baslik'])
print("The 'Baslik' column was dropped.")

print("----------------------")

#We are looking for column 'Listing No'
print("---------- LISTING NO ----------")
listing_no_uniqeue_count = df2['Listing No'].nunique()
print("unique values count for column 'Listing No'-->",listing_no_uniqeue_count)
df2 = df2.drop(columns=['Listing No'])
print("The 'Listing No' column was dropped.")

print("----------------------")


#looking for column 'Listing status'
print("---------- LISTING STATUS ----------")
listing_status_unique_count = df2['Listing status'].nunique()
print("unique values count for column 'Listing status'-->",listing_status_unique_count)
df2 = df2.drop(columns=['Listing status'])
print("The 'Listing status' column was dropped.")

print("----------------------")

#looking for residence type
print("---------- RESIDENCE TYPE ----------")
residence_type_unique_count = df2['Residence Type'].nunique()
print("unique values count for column 'Residence Type':", residence_type_unique_count)
residence_type_unique_val = df2['Residence Type'].unique()
print("unique values for column 'Residence Type':", residence_type_unique_val)
residence_type_repeating_values = df2['Residence Type'].value_counts()
print("repeating counts for every values\n",residence_type_repeating_values)

print("Residence Types are cleaning except Apartment")
df2 = df2[df2['Residence Type'] == 'Apartment']
print("unique values for column 'Residence Type' after dropping\n",df2['Residence Type'].value_counts())
#we need to reset index
df2 = df2.reset_index(drop=True)


print("there is apartment for residence type. so we can drop this column")
df2 = df2.drop(columns=['Residence Type'])

print("----------------------")

print("NaN values for now-->\n",df2.isnull().sum())

print("----------------------")

print("---------- FACADE ----------")
print("The column 'Facade' has 1/3 NaN values")
print("Column 'Facade' is dropping")
df2 = df2.drop(columns=['Facade'])
print("Column 'Facade' dropped")

print("----------------------")

print("---------- NUMBER OF ROOM + HALL ----------")
print("unique values count for column 'Number Of Room + Hall'-->", df2['Number Of Room + Hall'].nunique())
print("repeating counts for every values\n", df2['Number Of Room + Hall'].value_counts())
print("preaparing for dropping 10 less rows...")


not_needed_rooms = ['3 + 1', '2 + 1', '1 + 1']
df2 = df2[df2['Number Of Room + Hall'].isin(not_needed_rooms)]

df2 = df2.reset_index(drop=True)

print(df2['Number Of Room + Hall'].value_counts())


print("----------------------")


print("---------- NUMBER OF BATHROOMS ----------")
print("unique values count for column 'Number of Bathrooms'-->", df2['Number of Bathrooms'].nunique())
print("repeating counts for every values\n", df2['Number of Bathrooms'].value_counts())
df2 = df2[df2['Number of Bathrooms'] != 3.0]
df2 = df2.reset_index(drop=True)
print(df2['Number of Bathrooms'].value_counts())


print("----------------------")

print("NaN values for now-->\n",df2.isnull().sum())

print("----------------------")

print("---------- GROSS / NET M2 ----------")
print("unique values count for column 'Gross / Net m²'-->", df2['Gross / Net m²'].nunique())
print("repeating counts for every values\n", df2['Gross / Net m²'].value_counts())
print("this column needs to be cleaning. so we will look later")

print("----------------------")

print("---------- HEATING TYPE ----------")
print("unique values count for column 'Heating Type'-->", df2['Heating Type'].nunique())
print("repeating counts for every values\n", df2['Heating Type'].value_counts())
print("this column needs to be cleaning. so we will look later")


print("----------------------")


print("---------- LOAN AVAILABILITY ----------")
print("unique values count for column 'Loan Availability'-->", df2['Loan Availability'].nunique())
print("repeating counts for every values\n", df2['Loan Availability'].value_counts())
print("according the outputs, dropping this column")

df2 = df2.drop(columns=['Loan Availability'])
print("column Loan Availability dropped")

print("----------------------")

print("---------- TITLE DEED STATUS ----------")
print("unique values count for column 'Title Deed Status'-->", df2['Title Deed Status'].nunique())
print("repeating counts for every values\n", df2['Title Deed Status'].value_counts())
print("this column needs to be cleaning. so we will look later")

not_needed_title_deed_types = ['Tapu None', 'Shared Deed', 'Freehold Title Deed']
df2 = df2[~df2['Title Deed Status'].isin(not_needed_title_deed_types)]
df2 = df2.reset_index(drop=True)

# Sonucu kontrol et
print(df2['Title Deed Status'].value_counts())

print("----------------------")

print("---------- FURNISHING STATUS ----------")
print("unique values count for column 'Furnishing Status'-->", df2['Furnishing Status'].nunique())
print("repeating counts for every values\n", df2['Furnishing Status'].value_counts())
print("this column needs to be cleaning. so we will look later")

print("----------------------")

print("---------- USAGE STATUS ----------")
print("unique values count for column 'Usage Status'-->", df2['Usage Status'].nunique())
print("repeating counts for every values\n", df2['Usage Status'].value_counts())

print("Unspecified rows dropping")
df2 = df2[df2['Usage Status'] != 'Unspecified']
df2 = df2.reset_index(drop=True)
print(df2['Usage Status'].value_counts())


print("----------------------")


print("---------- SWAP ----------")
print("unique values count for column 'Swap'-->", df2['Swap'].nunique())
print("repeating counts for every values\n", df2['Swap'].value_counts())
print("according the outputs, dropping this column")
df2 = df2.drop(columns=['Swap'])
print("column swap dropped")

print("----------------------")

df2.to_csv("2-unneccesary-columns-dropped.csv", index=False, encoding="utf-8-sig")
print("File saved successfully: 2-unneccesary-columns-dropped.csv")




