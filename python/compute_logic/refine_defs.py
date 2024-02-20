import csv
import os

# The purpose of this file is to remove all transactions from an account transaction file
# that we want to ignore. Usually payments, but sometimes some other things as well.

PRJ_HOME = os.environ.get('PRJ_HOME')

# =====================
# APPLE CARD DEFINITION
# =====================
def refine_apple_card_csv(input_csv):
    output_file = os.path.join(PRJ_HOME, 'worklib/apple_card_refined.csv')     

    with open(input_csv, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames
        filtered_rows = [row for row in reader if row['Type'] != 'Payment']

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(filtered_rows)

# =====================
# CAPITAL ONE DEFINITION
# =====================
def refine_capital_one_csv(input_csv, outfile_name, Keep_Cashback):
    output_file = os.path.join(PRJ_HOME, 'worklib/' + outfile_name)     

    with open(input_csv, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames
        if not Keep_Cashback:
            filtered_rows = [row for row in reader if row['Category'] != 'Payment/Credit']
        else:
            filtered_rows = []
            for row in reader:
                # all expenses
                if row['Category'] != 'Payment/Credit':
                    filtered_rows.append(row)
                # and all cashback
                elif row['Description'] == 'CREDIT-CASH BACK REWARD':
                    filtered_rows.append(row)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(filtered_rows)

# =====================
# AMAZON CARD DEFINITION
# =====================
def refine_amazon_card_csv(input_csv):
    output_file = os.path.join(PRJ_HOME, 'worklib/amazon_card_refined.csv')     

    with open(input_csv, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames
        filtered_rows = [row for row in reader if row['Type'] != 'Payment']

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(filtered_rows)

# ==================================
# WELLS FARGO DEFINITION (No income)
# ==================================
def refine_wells_fargo_csv(input_file, Keep_Cashback):
    output_file = os.path.join(PRJ_HOME, 'worklib/wells_fargo_refined.csv')     

    forbidden_strings = [
        "CAPITAL ONE",
        "CHASE CREDIT CRD",
        "APPLECARD GSBANK PAYMENT",
        "CITI CARD",
        "PAYPAL INST XFER"
    ]

    cashback_strings = [
        "APPLE CASH BANK",
    ]

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            amount = row.get("Amount", "")
            # Filter out 1. Positive amounts and 2. Any row containing a "forbidden string" but NOT cashback
            if not Keep_Cashback:
                if (amount.startswith("-")) and (not any(forbidden in row["Description"] for forbidden in forbidden_strings)):
                    writer.writerow(row)
            else:
                # write all the same rows as previous case
                if (amount.startswith("-")) and (not any(forbidden in row["Description"] for forbidden in forbidden_strings)):
                    writer.writerow(row)
                # and also write cashback rows
                elif any(cashback in row["Description"] for cashback in cashback_strings):
                    writer.writerow(row)          

# ==================================
# WELLS FARGO DEFINITION (No income)
# ==================================
def refine_wells_fargo_csv_income(input_file):
    output_file = os.path.join(PRJ_HOME, 'worklib/wells_fargo_refined.csv')     

    forbidden_strings = [
        "CAPITAL ONE",
        "CHASE CREDIT CRD",
        "APPLECARD GSBANK PAYMENT",
        "CITI CARD"
        "PAYPAL INST XFER"
    ]

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # Filter out 1. Positive amounts and 2. Any row containing a "forbidden string"
            if not any(forbidden in row["Description"] for forbidden in forbidden_strings):
                writer.writerow(row)                

# =====================
# COSTCO CARD DEFINITION
# =====================
def refine_costco_card_csv(input_csv):
    output_file = os.path.join(PRJ_HOME, 'worklib/costco_card_refined.csv')

    with open(input_csv, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        csv_writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        csv_writer.writeheader()

        for row in reader:
            if not row['Credit']:
                csv_writer.writerow(row)

# ==============================
# 401(k) CONTRIBUTION DEFINITION
# ==============================
def refine_f01k_contributions(input_csv):
    output_file = os.path.join(PRJ_HOME, 'worklib/401k_contribute_refined.csv')     

    with open(input_csv, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames
        filtered_rows = [row for row in reader if row['Transaction Type'] == 'Contributions']

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(filtered_rows)  

# ==============================
# DISCOVER HYSA
# ==============================
def refine_hysa_csv(input_csv):
    output_file = os.path.join(PRJ_HOME, 'worklib/hysa_refined.csv')     

    with open(input_csv, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames
        filtered_rows = [row for row in reader if row['Transaction Description'] == 'Interest Paid']

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(filtered_rows)                        