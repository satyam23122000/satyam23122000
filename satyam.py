
import pandas as pd 
import glob 
import os 
import re
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

facebook_spend_files = "G:/Shared drives/google_and_facebook_lead/facebook/facebook_raw/"
facebook_spend_files_combine = glob.glob(os.path.join(facebook_spend_files, "*.csv"))  # Reading only CSV files
facebook_dataframe = []  # Initialize an empty list

# facebook sheets api Creditails, api path 
yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%d-%B-%Y')
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("C:/Users/DELL/Documents/tesCodeSS/Credentials.json", scopes = scopes)
client = gspread.authorize(creds)
sheet_id = "1rx6pjNyLC4kajlqbkNCCXeQ5ziNjy4IVA3lgzndKprY"
sheet = client.open_by_key(sheet_id)
facebook_report = sheet.worksheet("facebook_report")
# yesterday_date = "27-March-2025"  # Replace with dynamic date if needed
date_cell = facebook_report.find("May-13-2025")


for file in facebook_spend_files_combine:
    print(f"Reading file: {file}")  # Print the file being read
    try:
        facebook_df= pd.read_csv(file, encoding='utf-8', low_memory=False)
        facebook_dataframe.append(facebook_df)  # Append each DataFrame to the list
    except Exception as e:
        print(f"Error reading file {file}: {e}")

# Combine all DataFrames into one
if facebook_dataframe:  # Check if the list is not empty
    facebook_dataframe = pd.concat(facebook_dataframe, ignore_index=True)  # Combine into a single DataFrame

    # Filtering the DataFrame
    G_df = facebook_dataframe[facebook_dataframe['Reach'] != '0']
    G_df = G_df[~G_df["Campaign name"].str.contains(r"Display|youtube|Branding", case=False, na=False)]
    G_df = G_df[~G_df["Campaign name"].str.contains("Total", case=False, na=False)]
    G_df["1"] = G_df["Campaign name"]


G_df["1"] = G_df.apply(
    lambda row: (
        "OSP" if re.search(r"\bosp\b", str(row.get("1", "")), re.IGNORECASE)
        else "Euler - Dealership" if re.search(r"\bDealership\b", str(row.get("1", "")), re.IGNORECASE)
        else "Montra-eviator" if re.search(r"\beviator\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata Yodha" if re.search(r"\byodha\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata Intra" if re.search(r"\bIntra\b",str(row.get("1", "")), re.IGNORECASE)
        else "Tata - ACE EV" if re.search(r"\bace\s*-\s*ev\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata - ACE EV" if re.search(r"\bev\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata Ace" if re.search(r"\bace\b", str(row.get("1", "")), re.IGNORECASE) and row["1"].lower() != "Ace ev"
        else "Tata ILCV + ICV" if re.search(r"\bicv\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata ILCV + ICV" if re.search(r"\blcv\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata MCV" if re.search(r"\bmcv\b", str(row.get("1", "")), re.IGNORECASE)
        else "TATA HCV RMC" if re.search(r"\brmc\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata HCV" if re.search(r"\bhcv\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata Magic" if re.search(r"\bmagic\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata Winger" if re.search(r"\bwinger\b", str(row.get("1", "")), re.IGNORECASE)
        else "Tata Buses" if re.search(r"\bbuses\b", str(row.get("1", "")), re.IGNORECASE)
        else "Cruzio" if re.search(r"\bcruzio\b", str(row.get("1", "")), re.IGNORECASE)
        else "Mahindra - BLAZO" if re.search(r"\bbalzo\b",str(row.get("1", "")),re.IGNORECASE)
        else "Mahindra - FURIO" if re.search(r"\bfurio\b",str(row.get("1", "")),re.IGNORECASE)
        else "Mahindra - JAYO" if re.search(r"\bjayo\b",str(row.get("1", "")),re.IGNORECASE)
        else "Treo" if re.search(r"\btreo\b", str(row.get("1", "")), re.IGNORECASE)
        else "Jeeto" if re.search(r"\bjeeto\b", str(row.get("1", "")), re.IGNORECASE)
        else "Zor Grand" if re.search(r"\bzor\s*grand\b",str(row.get("1", "")), re.IGNORECASE)
        else "Mahindra - E-ALFA" if re.search(r"\balfa\b", str(row.get("1", "")), re.IGNORECASE)
        else "Hiload- Three Wheeler" if re.search(r"\bhiload\b", str(row.get("1", "")), re.IGNORECASE)
        else "Euler" if re.search(r"\beuler\b", str(row.get("1", "")), re.IGNORECASE)
        else "Zeo" if re.search(r"\bzeo\b", str(row.get("1", "")), re.IGNORECASE)
        else "Mahindra Supro" if re.search(r"\bSupro\b", str(row.get("1", "")), re.IGNORECASE)
        else "Mahindra Veero" if re.search(r"\bveero\b", str(row.get("1", "")), re.IGNORECASE)
        else "Mahindra Bolero" if re.search(r"\bBolero\b", str(row.get("1", "")), re.IGNORECASE)
        else "Zor Grand" if re.search(r"\bzor\b", str(row.get("1", "")), re.IGNORECASE)
        else "Montra" if re.search(r"\bmontra\b", str(row.get("1", "")), re.IGNORECASE) 
        else str(row.get("1", ""))
    ),
    axis=1
)

G_df["Reach"] = (
    G_df["Reach"]
    .astype(str)  # Convert all values to string
    .str.replace(",", "")  # Remove commas
    .replace("nan", "0")  # Handle NaN cases
    .astype(float)  # Convert back to float
)

current_datetime = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
facebook_spend = f'G:/Shared drives/google_and_facebook_lead/facebook/facebook_combine/facebook_{current_datetime}.csv'
G_df.to_csv(facebook_spend,index=False)
#Amount_spent:Spends Results:Leads
G_gsheets=G_df.groupby("1")[["Amount spent (INR)","Results"]].sum()
# conversion of column name according to google sheets 
G_gsheets.rename(columns={"Amount spent (INR)": "Spends"}, inplace=True)
G_gsheets.rename(columns={"Results": "Leads"}, inplace=True)
G_gsheets['Yesterday_Date'] = yesterday_date

if date_cell:
    row_number = date_cell.row
    print(f"Rrow found for yesterday's date: {row_number}")

    # Get header row to find column indices for vehicles
    header_row = facebook_report.row_values(1)

    for vehicle_name in G_gsheets.index:
        if vehicle_name in header_row:
            vehicle_col_index = header_row.index(vehicle_name) + 1  # Columns are 1-based in gspread

            # Get spends and leads values for the vehicle
            Amount_spent = G_gsheets.loc[vehicle_name, "Spends"]
            Leads = G_gsheets.loc[vehicle_name, "Leads"]

            # Update "Spends" (column below vehicle_name)
            facebook_report.update_cell(row_number, vehicle_col_index + 0, Amount_spent)

            # Update "Leads" (next column)
            facebook_report.update_cell(row_number, vehicle_col_index + 1, Leads)
            
            print(f"Updated {vehicle_name}: Spends={Amount_spent}, Leads={Leads}")
else:
    print("Date not found in the sheet.")
    