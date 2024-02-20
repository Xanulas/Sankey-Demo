import pandas as pd
import os

PRJ_HOME = os.environ.get('PRJ_HOME')
output_csv = os.path.join(PRJ_HOME, 'worklib/consolidated_transactions.csv')

# =====================
# APPLE CARD DEFINITION
# =====================
def merge_apple_card_csv():
    source_df = pd.read_csv(os.path.join(PRJ_HOME, 'worklib/apple_card_refined.csv'))

    # Create a new DataFrame for destination.csv with required columns
    destination_df = pd.DataFrame(columns=["Account", "Transaction Date", "Merchant", "Category", "Description", "Amount"])

    # Match columns and copy data
    destination_df["Transaction Date"] = source_df["Transaction Date"]
    destination_df["Description"] = source_df["Description"]
    destination_df["Amount"] = source_df["Amount (USD)"]
    destination_df["Merchant"] = source_df["Merchant"]
    destination_df["Category"] = source_df["Category"]

    destination_df["Account"] = "Apple Card"    

    # Write to destination.csv
    destination_df.to_csv(output_csv, mode='a', header=False, index=False)

# =====================
# CAPITAL ONE DEFINITION
# =====================
def merge_capital_one_csv(input_filename):
    source_csv = os.path.join(PRJ_HOME, 'worklib/' + input_filename) 
    source_df = pd.read_csv(source_csv)

    if input_filename == 'quicksilver_refined.csv':
        Account = 'Quicksilver'
    else:
        Account = 'Savor'

    # Create a new DataFrame for destination.csv with required columns
    destination_df = pd.DataFrame(columns=["Account", "Transaction Date", "Merchant", "Category", "Description", "Amount"])

    # Match columns and copy data
    destination_df["Transaction Date"] = pd.to_datetime(source_df["Transaction Date"]).dt.strftime('%m/%d/%Y')
    destination_df["Description"] = source_df["Description"]
    destination_df["Category"] = source_df["Category"]

    # Assign "Amount" based on the condition
    destination_df["Amount"] = source_df["Debit"].fillna(source_df["Credit"])

    destination_df["Account"] = Account

    # Fill unused columns with empty values
    destination_df["Merchant"] = ""

    # Write to destination.csv
    destination_df.to_csv(output_csv, mode='a', header=False, index=False)    

# =====================
# AMAZON CARD DEFINITION
# =====================
def merge_amazon_card_csv():
    source_df = pd.read_csv(os.path.join(PRJ_HOME, 'worklib/amazon_card_refined.csv'))

    # Create a new DataFrame for destination.csv with required columns
    destination_df = pd.DataFrame(columns=["Account", "Transaction Date", "Merchant", "Category", "Description", "Amount"])

    # Match columns and copy data
    destination_df["Transaction Date"] = source_df["Transaction Date"]
    destination_df["Description"] = source_df["Description"]
    destination_df["Category"] = source_df["Category"]
    destination_df["Amount"] = -source_df["Amount"]

    destination_df["Account"] = "Amazon Card"

    # Fill unused columns with empty values
    destination_df["Merchant"] = ""

    # Write to destination.csv
    destination_df.to_csv(output_csv, mode='a', header=False, index=False)

# =====================
# WELLS FARGO DEFINITION
# =====================
def merge_wells_fargo_csv():
    source_df = pd.read_csv(os.path.join(PRJ_HOME, 'worklib/wells_fargo_refined.csv'))

    # Create a new DataFrame for destination.csv with required columns
    destination_df = pd.DataFrame(columns=["Account", "Transaction Date", "Merchant", "Category", "Description", "Amount"])

    # Match columns and copy data
    destination_df["Transaction Date"] = source_df["Transaction Date"]
    destination_df["Description"] = source_df["Description"]
    
    # Flip the sign only for negative numbers in the "Amount" column
    destination_df["Amount"] = source_df["Amount"].apply(lambda x: -x if x < 0 else x)

    destination_df["Account"] = "WF Checking"

    # Fill unused columns with empty values
    destination_df["Merchant"] = ""
    destination_df["Category"] = ""

    # Write to destination.csv
    destination_df.to_csv(output_csv, mode='a', header=False, index=False)

# =====================
# COSTCO CARD DEFINITION
# =====================
def merge_costco_card_csv():
    source_df = pd.read_csv(os.path.join(PRJ_HOME, 'worklib/costco_card_refined.csv'))

    # Create a new DataFrame for destination.csv with required columns
    destination_df = pd.DataFrame(columns=["Account", "Transaction Date", "Merchant", "Category", "Description", "Amount"])

    # Match columns and copy data0
    destination_df["Transaction Date"] = source_df["Date"]
    destination_df["Description"] = source_df["Description"]
    destination_df["Amount"] = source_df["Debit"]

    destination_df["Account"] = "Costco Card"    

    # Fill unused columns with empty values
    destination_df["Merchant"] = ""
    destination_df["Category"] = ""

    # Write to destination.csv
    destination_df.to_csv(output_csv, mode='a', header=False, index=False)

# =====================
# FIDELITY 401K DEFINITION
# =====================
def merge_f01k_contributions():
    source_df = pd.read_csv(os.path.join(PRJ_HOME, 'worklib/401k_contribute_refined.csv'))

    # Create a new DataFrame for destination.csv with required columns
    destination_df = pd.DataFrame(columns=["Account", "Transaction Date", "Merchant", "Category", "Description", "Amount"])

    # Match columns and copy data0
    destination_df["Transaction Date"] = source_df["Date"]
    destination_df["Description"] = source_df["Transaction Type"]
    destination_df["Amount"] = source_df["Amount ($)"]
    destination_df["Category"] = source_df["Investment"]

    destination_df["Account"] = "FIDELITY 401(k)"    

    # Fill unused columns with empty values
    destination_df["Merchant"] = ""

    # Write to destination.csv
    destination_df.to_csv(output_csv, mode='a', header=False, index=False)    

# =====================
# DISCOVER HYSA DEFINITION
# =====================    
def merge_hysa_csv():
    source_df = pd.read_csv(os.path.join(PRJ_HOME, 'worklib/hysa_refined.csv'))

    # Create a new DataFrame for destination.csv with required columns
    destination_df = pd.DataFrame(columns=["Account", "Transaction Date", "Merchant", "Category", "Description", "Amount"])

    # Match columns and copy data0
    destination_df["Transaction Date"] = source_df["Transaction Date"]
    destination_df["Description"] = source_df["Transaction Description"]
    destination_df["Amount"] = source_df["Credit"].replace(r'[\$,]', '', regex=True).astype(float)
    destination_df["Account"] = "DISCOVER HYSA"    

    # Fill unused columns with empty values
    destination_df["Merchant"] = ""
    destination_df["Category"] = ""  

    # Write to destination.csv
    destination_df.to_csv(output_csv, mode='a', header=False, index=False)       