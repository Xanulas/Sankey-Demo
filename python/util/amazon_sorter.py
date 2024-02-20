import os
import pandas as pd
from datetime import datetime

def amazon_sorter(start, end):
    
    SF = os.environ.get('SF')
    PRJ_HOME = os.environ.get('PRJ_HOME')

    AMZN_PATH = os.path.join(PRJ_HOME, "Data/Amazon/Retail.OrderHistory.1/Retail.OrderHistory.1.csv")

    df = pd.read_csv(AMZN_PATH)

    # might require fixing for amazon orders with miliseconds in the order date
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%Y-%m-%dT%H:%M:%SZ')

    df['Total Owed'] = pd.to_numeric(df['Total Owed'], errors='coerce')

    mask = (df['Order Date'] >= start) & (df['Order Date'] <= end)
    filtered_df = df.loc[mask]

    category_sum = filtered_df.groupby('Budget Category')['Total Owed'].sum()

    result_dict = category_sum.to_dict()

    return result_dict
