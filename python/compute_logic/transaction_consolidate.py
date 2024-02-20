import os
import json
import argparse
import pandas as pd
from refine_defs import *
from merge_defs import *
from datetime import datetime

PRJ_HOME = os.environ.get('PRJ_HOME')

# Initialize CSV inputs
apple_card_csv        = None
quicksilver_csv       = None
amazon_card_csv       = None
savor_csv             = None
wells_fargo_csv       = None
costco_card_csv       = None
f01k_contribution_csv = None
hysa_csv              = None

# logfile
logfile_path = os.path.join(PRJ_HOME, 'Logs/consolidate.log')
if os.path.exists(logfile_path):
    os.remove(logfile_path)
l = open(logfile_path, 'w')

# =======================================
# delete worklib contents if not empty
# =======================================

output_dir = os.path.join(PRJ_HOME, 'worklib')

if any(os.scandir(output_dir)):
    for item in os.scandir(output_dir):
        if item.is_file():
            os.remove(item.path)
        elif item.is_dir():
            os.rmdir(item.path)

# ==============================
# arg parse
# ==============================
parser = argparse.ArgumentParser(description="")
parser.add_argument('-t', '--year_month', help="Specify the year and month in the format 'YYYY MMM'")
parser.add_argument('-k', '--keep_cashback', help='')
parser.add_argument('-i', '--include_401k', help='') 
args = parser.parse_args()

Keep_Cashback           = eval(args.keep_cashback) # eval ensures these get correctly casted as bools
Include_401k_Contribute = eval(args.include_401k)  # eval ensures these get correctly casted as bools

year, month_str = args.year_month.split()
month = datetime.strptime(month_str, '%b').strftime('%B')

month_num = datetime.strptime(month_str, '%b').strftime('%m')

csv_directory = os.path.join(PRJ_HOME, "Data", year, f"{month_num}-{month}")
print("Identified following input directory: " + str(os.path.join(PRJ_HOME, "Data", year, f"{month_num}-{month}")))

# ================
# Detect CSV files
# ================
for filename in os.listdir(csv_directory):
    if filename == "apple_card.csv":
        apple_card_csv = os.path.join(csv_directory, filename)
    
    elif filename == "quicksilver.csv":
        quicksilver_csv = os.path.join(csv_directory, filename)
    
    elif filename == "savor_one.csv":
        savor_csv = os.path.join(csv_directory, filename)
    
    elif filename == "amazon.csv":
        amazon_card_csv = os.path.join(csv_directory, filename)

    elif filename == "wells_fargo_checking.csv":
        wells_fargo_csv = os.path.join(csv_directory, filename)

    elif filename == "costco.csv":
        costco_card_csv = os.path.join(csv_directory, filename)

    elif filename == "401k_contribute.csv":
        f01k_contribution_csv = os.path.join(csv_directory, filename)   

    elif filename == "hysa.csv":
        hysa_csv = os.path.join(csv_directory, filename)                

# =============================================================
# Filter out transactions to ignore
# =============================================================    
if apple_card_csv is not None:   
    refine_apple_card_csv(apple_card_csv)
if quicksilver_csv is not None:
    refine_capital_one_csv(quicksilver_csv, 'quicksilver_refined.csv', Keep_Cashback)
if savor_csv is not None:
    refine_capital_one_csv(savor_csv, 'savor_refined.csv', Keep_Cashback)
if amazon_card_csv is not None:
    refine_amazon_card_csv(amazon_card_csv)
if wells_fargo_csv is not None:
    refine_wells_fargo_csv(wells_fargo_csv, Keep_Cashback)
if costco_card_csv is not None:
    refine_costco_card_csv(costco_card_csv)
if f01k_contribution_csv is not None:
    refine_f01k_contributions(f01k_contribution_csv)
if hysa_csv is not None:
    refine_hysa_csv(hysa_csv)

# ===========================================================================
# Merge every CSV into a consolidated CSV which will contain all transactions
# ===========================================================================
consolidated_csv = os.path.join(output_dir, 'consolidated_transactions.csv')

# Create a header line for the output CSV
with open(consolidated_csv, 'w') as file:
    file.write('Account,Transaction Date,Merchant,Category,Description,Amount,Budget Category\n')

if apple_card_csv is not None: 
    merge_apple_card_csv()
if quicksilver_csv is not None:
    merge_capital_one_csv('quicksilver_refined.csv')
if savor_csv is not None:
    merge_capital_one_csv('savor_refined.csv')
if amazon_card_csv is not None:
    merge_amazon_card_csv()
if wells_fargo_csv is not None:
    merge_wells_fargo_csv()
if costco_card_csv is not None:    
    merge_costco_card_csv()
if (f01k_contribution_csv is not None) and (Include_401k_Contribute):   
    merge_f01k_contributions() 
if (hysa_csv is not None) and (Keep_Cashback):   
    merge_hysa_csv()        

# =============================================================
# Categorize
# =============================================================  

num_no_match = 0

def find_category(row):
    global num_no_match
    description = row['Description']
    merchant = row['Merchant']

    for key, value in json_data.items():
        if key.lower() in description.lower():
            return value
        
    if not pd.isna(merchant) and str(merchant).strip() != "":
        for key, value in json_data.items():
            if key.lower() in str(merchant).lower():
                return value


    num_no_match += 1
    l.write("#" + str(num_no_match) + " transaction that failed to match with a category:\n")
    l.write(str(row) + "\n\n")
    return None

df = pd.read_csv(consolidated_csv)

with open(os.path.join(PRJ_HOME, 'keys/key.json'), 'r') as f:
    json_data = json.load(f)

df['Budget Category'] = df.apply(find_category, axis=1)

if num_no_match != 0:
    print("\n\n********** WARNING **********\n\n")
    print("failed to match " + str(num_no_match) + " transactions with a budget category")
    print("See /Logs/consolidate.log for a list of failed transaction")
    print("Add description or merchant of these transaction to /keys/key.json\n\n")

df.to_csv(consolidated_csv, index=False)