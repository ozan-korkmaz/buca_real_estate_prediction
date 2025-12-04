#*******************ACTIONS TAKEN*******************
# Dropped 'Fiyat (Metin)' and renamed 'Fiyat (Sayisal)' to 'Price'.
# Renamed 'Konum' to 'Location', grouped rare values as 'other', and applied One-Hot Encoding.
# Processed 'Last Update Date' to extract 'Listing_Age_Days' and 'Posted_Month', then dropped the original column.
# Split 'Number Of Room + Hall' into 'Rooms' and 'Halls' integer columns.
# Renamed 'Number of Bathrooms' to 'Bathrooms', filled missing values with mode, and converted to int.
# Extracted 'Net_m2' from 'Gross / Net m²' and dropped the original column.
# Cleaned 'Number of Floors' by removing text and converting to int.
# Converted 'Floor' to numeric, dynamically mapping text values (e.g., Middle, Top) based on total floors.
# Standardized 'Property Age' (set 'New Property' to 0) and converted to int.
# Mapped 'Heating Type', filtered out unwanted types, and applied One-Hot Encoding.
# Dropped rows with missing 'Title Deed Status' and applied One-Hot Encoding.
# Filled missing 'Furnishing Status' with 'Not Furnished' and applied One-Hot Encoding.
# Filled missing 'Usage Status' with 'Empty', applied One-Hot Encoding, and saved the result.

import pandas as pd
import numpy as np

df3 = pd.read_csv("2-unneccesary-columns-dropped.csv")


# Fiyat (Metin)             +
# Fiyat (Sayisal)           +
# Konum                     +
# Last Update Date          +
# Number Of Room + Hall     +
# Number of Bathrooms       +
# Gross / Net m²            +
# Number of Floors          +
# Floor                     +
# Property Age              +
# Heating Type              +
# Title Deed Status         +
# Furnishing Status         +
# Usage Status              +

print(df3.info())

print("----------------------")

print("---------- PRICE ----------")
print("dropping the column 'Fiyat (Metin)'... ")
df3 = df3.drop(columns=['Fiyat (Metin)'])
print("column Fiyat (Metin) dropped")

print("Fiyat (Sayisal) is renaming as Price")
df3 = df3.rename(columns={'Fiyat (Sayisal)': 'Price'})


print("-" * 30)
print(df3['Price'].head())

print("----------------------")

print("---------- LOCATION ----------")

df3 = df3.rename(columns={'Konum': 'Location'})

print(df3['Location'].unique())


print(f"\nunique for location: {df3['Location'].nunique()}")

print("less than 8 are grouping as other")
location_counts = df3['Location'].value_counts()
less_than_8 = location_counts[location_counts <= 8].index
df3['Location'] = df3['Location'].replace(less_than_8, 'other')
print("done")
print(df3['Location'].value_counts())
#one hot encoding
df3 = pd.get_dummies(df3, columns=['Location'], drop_first=True, dtype=int)


print("----------------------")

print("---------- LAST UPDATE DATE ----------")

df3 = df3.rename(columns={'Last Update Date': 'Last_Update_Date'})


print("Data Type:", df3['Last_Update_Date'].dtype)
print("-" * 30)
print(df3['Last_Update_Date'].head())


df3['Last_Update_Date'] = df3['Last_Update_Date'].astype(str).str.replace('-', '/').str.replace('.', '/')


df3['Last_Update_Date'] = pd.to_datetime(df3['Last_Update_Date'], dayfirst=True)

print(df3['Last_Update_Date'].dtype)
print("-" * 30)
print(df3['Last_Update_Date'].head())


reference_date = df3['Last_Update_Date'].max() 

df3['Listing_Age_Days'] = (reference_date - df3['Last_Update_Date']).dt.days

df3['Posted_Month'] = df3['Last_Update_Date'].dt.month

print(df3[['Last_Update_Date', 'Listing_Age_Days', 'Posted_Month']].head())

print("Last_Update_Date dropped ")
df3.drop(columns=['Last_Update_Date'], inplace=True)


print("----------------------")

print("---------- Number Of Room + Hall ----------")

print("unique values", df3['Number Of Room + Hall'].unique())

print("unique values counts", df3['Number Of Room + Hall'].value_counts())
print("there are new 2 columns those 'Rooms' and 'Halls'")
df3[['Rooms', 'Halls']] = df3['Number Of Room + Hall'].str.split('+', expand=True)

df3['Rooms'] = df3['Rooms'].str.strip().astype(int)
df3['Halls'] = df3['Halls'].str.strip().astype(int)
print("column Number Of Room + Hall dropped")
df3.drop(columns=['Number Of Room + Hall'], inplace=True)


print("----------------------")

print("---------- Number of Bathrooms ----------")

df3.rename(columns={'Number of Bathrooms': 'Bathrooms'}, inplace=True)

print("unique values", df3['Bathrooms'].unique())

print("unique values counts", df3['Bathrooms'].value_counts(dropna=False))

mode_bathroom = df3['Bathrooms'].mode()[0]


df3['Bathrooms'] = df3['Bathrooms'].fillna(mode_bathroom)

df3['Bathrooms'] = df3['Bathrooms'].astype(int)

print("column Bathrooms after the cleaning",df3['Bathrooms'].value_counts(dropna=False))



print("----------------------")

print("---------- Gross / Net m² AS Net_m2 ----------")

print(f"unique values: {df3['Gross / Net m²'].unique()}")
print("\nunique values counts Gross / Net m²")
print(df3['Gross / Net m²'].value_counts(dropna=False))

def extract_net_m2(text):
    try:
        if isinstance(text, str) and '/' in text:           
            net_part = text.split('/')[1]            
            return net_part.replace('m2', '').strip()
        return np.nan
    except:
        return np.nan

df3['Net_m2'] = df3['Gross / Net m²'].apply(extract_net_m2)

df3['Net_m2'] = pd.to_numeric(df3['Net_m2'], errors='coerce')

df3.drop(columns=['Gross / Net m²'], inplace=True)

print("Net_m2 cleaned")
print(df3['Net_m2'].head())
print("\nİstatistikler:")
print(df3['Net_m2'].describe())

 
print("----------------------")

print("---------- Number of Floors ----------")


df3.rename(columns={'Number of Floors': 'Number_Of_Floors'}, inplace=True)

print("unique values counts", df3['Number_Of_Floors'].value_counts(dropna=False))

print("unique values:", df3['Number_Of_Floors'].unique())

df3['Number_Of_Floors'] = df3['Number_Of_Floors'].str.replace(' Storey', '')

df3['Number_Of_Floors'] = df3['Number_Of_Floors'].astype(int)

print("cleaned version\n", df3['Number_Of_Floors'].value_counts().sort_index())
print("\nData Type:", df3['Number_Of_Floors'].dtype)



print("----------------------")

print("---------- Floor ----------")

print("unique value counts: ", df3['Floor'].value_counts(dropna=False))

print("unique values: ", df3['Floor'].unique())

def clean_floor_dynamic(row):
    
    val = str(row['Floor']).strip()
    total_floors = row['Number_Of_Floors'] 

    val = val.replace('.', '')

    if val in ['Ground', 'Raised Ground', 'Garden', 'Basement and Ground']:
        return 0
    elif val in ['Underground 1', 'Basement']:
        return -1
    elif val == 'Underground 2':
        return -2
    elif val in ['Top', 'Penthouse']:
        return total_floors  # En üst kat
    elif val == 'Middle':
        return int(total_floors / 2) if total_floors > 0 else 1 # Orta kat

    try:
        return int(val)
    except ValueError:
        return np.nan 


df3['Floor'] = df3.apply(clean_floor_dynamic, axis=1)

print("cleaned floor\n", df3['Floor'].value_counts(dropna=False).sort_index())


print("----------------------")

print("---------- Property_Age ----------")
df3.rename(columns={'Property Age': 'Property_Age'}, inplace=True)


print("unique value counts", df3['Property_Age'].value_counts(dropna=False))

print("unique values", df3['Property_Age'].unique())


df3['Property_Age'] = df3['Property_Age'].str.replace('New Property', '0')

df3['Property_Age'] = df3['Property_Age'].str.replace(' at Age', '')


df3['Property_Age'] = df3['Property_Age'].astype(int)


print("property age order from newest to oldest", df3['Property_Age'].value_counts().sort_index())

print("\nData Type:", df3['Property_Age'].dtype)





print("----------------------")

print("---------- Heating_Type ----------")


df3.rename(columns={'Heating Type': 'Heating_Type'}, inplace=True)

print("unique value counts", df3['Heating_Type'].value_counts(dropna=False))

print("unique values", df3['Heating_Type'].unique())

heating_map = {
    'Central Heating (Share Meter)': 'Central',
    'VRV': 'Air Conditioning',
    'Floor Heater': 'Underfloor Heating'
}


df3['Heating_Type'] = df3['Heating_Type'].replace(heating_map)

drop_list = [
    'No Heating', 
    'Gas Stove', 
    'Unspecified', 
    'Heating Stove'
]

df3 = df3[~df3['Heating_Type'].isin(drop_list)]

df3.reset_index(drop=True, inplace=True)


print("heating type last stuation", df3['Heating_Type'].value_counts())
print(f"\new row counts: {len(df3)}")


df3 = pd.get_dummies(df3, columns=['Heating_Type'], dtype=int)


print("----------------------")

print("---------- Title Deed Status ----------")


df3.rename(columns={'Title Deed Status': 'Title_Deed_Status'}, inplace=True)


print("unique value counts")
print(df3['Title_Deed_Status'].value_counts(dropna=False))

print("\nunique values")
print(df3['Title_Deed_Status'].unique())


df3.dropna(subset=['Title_Deed_Status'], inplace=True)

df3 = pd.get_dummies(df3, columns=['Title_Deed_Status'], prefix='Title', dtype=int)
print("ohe done for title deed status")



print("----------------------")

print("---------- Furnishing Status ----------")



df3.rename(columns={'Furnishing Status': 'Furnishing_Status'}, inplace=True)

print("unique value counts")
print(df3['Furnishing_Status'].value_counts(dropna=False))

print("\nunique values")
print(df3['Furnishing_Status'].unique())


print("---------- Furnishing_Status İşlemleri ----------")


df3['Furnishing_Status'] = df3['Furnishing_Status'].fillna('Not Furnished')



print("unique value counts after the fillna-->",df3['Furnishing_Status'].value_counts(dropna=False))

df3 = pd.get_dummies(df3, columns=['Furnishing_Status'], dtype=int)



print("----------------------")


print("---------- Usage_Status ----------")


df3.rename(columns={'Usage Status': 'Usage_Status'}, inplace=True)


print("unique value counts")
print(df3['Usage_Status'].value_counts(dropna=False))

print("\nunique values")
print(df3['Usage_Status'].unique())



df3['Usage_Status'] = df3['Usage_Status'].fillna('Empty')


print("unique value counts after fillna", df3['Usage_Status'].value_counts(dropna=False))


df3 = pd.get_dummies(df3, columns=['Usage_Status'], dtype=int)

print("\n---------- Encoding Sonrası İlk 5 Satır ----------")


print(df3.dtypes)


df3.to_csv("3-dataset-cleaned.csv", index=False, encoding="utf-8-sig")
print("File saved successfully: 3-dataset-cleaned.csv")

print(df3.dtypes)
