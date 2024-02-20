import plotly.graph_objects as go
import os
import pandas as pd
from dataclasses import dataclass
import csv
import argparse
from datetime import datetime, timedelta
import calendar

#######################################################################
#                     Arg Parsing
#######################################################################

parser = argparse.ArgumentParser(description="")
parser.add_argument('-t', '--year_month', help="Specify the year and month in the format 'YYYY MMM'")
parser.add_argument('-f', '--filename', help="HTML filename")
parser.add_argument('-m', '--month_flag', help="Is this for month scope Sankey?")
args = parser.parse_args()

if args.year_month is not None:
    year, month_str = args.year_month.split()
    month = datetime.strptime(month_str, '%b').strftime('%B')
filename = args.filename
month_flag = eval(args.month_flag)

#######################################################################
#             Declare / Initialize Data and Data Structures
#######################################################################

# used to store information about a node
@dataclass
class budgetCategory:
    label: str
    index: int
    node_col: str
    link_col: str
    parent: str
    amount: float
    leaf: bool

# used as final input to sankey plotting
master_labels = []
master_node_colors = []
master_link_colors = []
master_sources = []
master_targets = []
master_values = []

# used to reference data as its being populated / manipulated
cashflow_items = []
index_LUT = {}

# general pay information
BIWEEKLY_PAY       = 10
MATCH_PER_PAYCHECK = 2
Federal_Withhold   = 1
State_Withhold     = 1
SS_Withhold        = 1
Medicare_Withhold  = 1
HSA_Contribute     = 1
Medical_Insurance  = 1
Dental_Insurance   = 1

# paths
SF = os.environ.get('SF')
PRJ_HOME = os.environ.get('PRJ_HOME')
transaction_list = os.path.join(SF, 'Sankey-Demo/Transactions-to-Plot/combined.csv')

# debug log
debug_log_path = os.path.join(PRJ_HOME, 'Logs/snakey_debug.log')
if os.path.exists(debug_log_path):
    os.remove(debug_log_path)
d = open(debug_log_path, 'w')

# read transaction list and get category spending
df = pd.read_csv(transaction_list)
category_sum = df.groupby('Budget Category')['Amount'].sum()
d.write("Summary of Cumulative CSV\n")
d.write(str(category_sum))

# determine number of weeks in time scope
if not month_flag:
    date_series = pd.to_datetime(df['Transaction Date'], format='%m/%d/%Y')
    earliest_date = date_series.min()
    latest_date = date_series.max()
    weeks_difference = (latest_date - earliest_date).days // 7
else:
    earliest_date = datetime(int(year), datetime.strptime(month, '%B').month, 1)
    _, last_day_of_month = calendar.monthrange(int(year), earliest_date.month)
    latest_date = earliest_date + timedelta(days=last_day_of_month - 1)
    weeks_difference = 4

# read file containing all nodes / colors / heirerarchy and initialize the `cashflow_items` data structure
csv_file_path = os.path.join(PRJ_HOME, 'keys/sankey_nodes.csv')
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')

    for i, row in enumerate(csv_reader):
            name, node_col, link_col, parent, leaf = row
            cashflow_items.append(budgetCategory(name, i, node_col, link_col, parent, 0, eval(leaf)))
            index_LUT[name] = i

#######################################################################
#                      Populate income data
#######################################################################

# Populate Income Amounts
primary_income = (weeks_difference / 2) * BIWEEKLY_PAY
match_total = (weeks_difference / 2) * MATCH_PER_PAYCHECK

# get information about bonuses:
# 1. How many bonuses in the given timeframe?
# 2. For each one, how much and what was the tax withholding on the paycheck containing that bonus?
bonus_csv = os.path.join(PRJ_HOME, 'Data/Bonuses/bonuses.csv')

# if this is a one-month scope, assume only one bonus possible (target date represents the month we're looking for)
target_date = datetime.now()
if month_flag:
    target_date = datetime.strptime(f"{month} {year}", "%B %Y")

with open(bonus_csv, 'r') as bonus_file:
    bonus_reader = csv.reader(bonus_file)
    header = next(bonus_reader, None)

    bonus_counter = 0
    bonus_amount = 0
    bonus_fed_tax, bonus_ss_tax, bonus_state_tax, bonus_medicare = 0, 0, 0, 0
    for row in bonus_reader:
        bonus_date = datetime.strptime(row[0], "%m/%d/%Y")

        if (bonus_date.month == target_date.month and bonus_date.year == target_date.year) or not month_flag:
            bonus_counter += 1
            bonus_amount += float(row[1])
            bonus_fed_tax += float(row[2])
            bonus_ss_tax += float(row[3])
            bonus_state_tax += float(row[4])
            bonus_medicare += float(row[5])
            if month_flag:
                break # stop after first match / assume max 1 bonus per month

# bonus CSV gives tax amounts INCLUDING tax of primary income (not just bonus)
# so doing this subtraction prevents double-counting normal salary tax
nonbonus_tax_weeks = weeks_difference - (2 * bonus_counter)
cashflow_items[index_LUT['Medicare3']].amount = ((nonbonus_tax_weeks / 2) * Medicare_Withhold)
cashflow_items[index_LUT['Social Security3']].amount = ((nonbonus_tax_weeks / 2) * SS_Withhold)
cashflow_items[index_LUT['State Taxes3']].amount = ((nonbonus_tax_weeks / 2) * State_Withhold)
cashflow_items[index_LUT['Federal Taxes3']].amount = ((nonbonus_tax_weeks / 2) * Federal_Withhold)

# if received at least one bonus in time frame, add in the tax withholding for those paychecks
if(bonus_counter > 0):
    cashflow_items[index_LUT['Medicare3']].amount += bonus_medicare
    cashflow_items[index_LUT['Social Security3']].amount += bonus_ss_tax
    cashflow_items[index_LUT['State Taxes3']].amount += bonus_state_tax
    cashflow_items[index_LUT['Federal Taxes3']].amount += bonus_fed_tax

if month_flag:
    cashflow_items[index_LUT['HSA3']].amount = ((HSA_Contribute) * (weeks_difference / 2))
else:
    cashflow_items[index_LUT['HSA3']].amount = 600 + ((HSA_Contribute) * (weeks_difference / 2))

#######################################################################
#                       Populate Expenses
#######################################################################

# Populate values on leaf level sankey nodes using the category sums computed earlier
for i, category in enumerate(cashflow_items):
    for j in range(len(category_sum)):
        if (str(category.label[:-1]) == str(category_sum.index[j])):
            d.write("matched " + str(category.label) + " with " + str(category_sum.index[j]) + " amount = " + str(category_sum.iloc[j]) + "\n")
            category.amount = category_sum.iloc[j]

# approximate amazon card cashback as amazon spending * 0.05
cashflow_items[index_LUT['Cashback/Interest0']].amount += cashflow_items[index_LUT['Amazon3']].amount * 0.05
cashback_interest = cashflow_items[index_LUT['Cashback/Interest0']].amount            

# FIXME : if you want to re-sort amazon purchaes at the transaction level, include the function in /python/util and provide Amazon download data
# amazon_sorted_dict = amazon_sorter(earliest_date, latest_date)
# for key, value in amazon_sorted_dict.items():
#     if key == 'OMIT':
#         cashflow_items[index_LUT['Amazon3']].amount -= value
#         continue
#     else:
#         cashflow_items[index_LUT['Amazon3']].amount -= value
#         cashflow_items[index_LUT[key]].amount += value
# Always pop original Amazon category since this should disappear
# cashflow_items.pop(index_LUT['Amazon3'])

# remove leaf categories with 0 spending this month ()
indexes_to_remove = []   
if month_flag:
    # allow bonus to be deleted if no bonuses
    if(bonus_counter > 0):
        cashflow_items[index_LUT['Bonus0']].leaf = False

    # identify items with amount 0:
    for i, item in enumerate(cashflow_items):
        if (item.amount == 0) and (item.leaf == True):
        # if (item.amount == 0):
            d.write("removed the following leaf category due to no spending: " + item.label)
            indexes_to_remove.append(i)

    # remove items in reverse order:
    for index in reversed(indexes_to_remove):
        cashflow_items.pop(index)

# Rebuild index LUT dict with removed items
index_LUT = {}
for i, item in enumerate(cashflow_items):
    index_LUT[item.label] = i        

#######################################################################
#                      Build Sankey Arrays
#######################################################################
# Order of Leaf to Trunk
def append_sankey_node(p_index, i, amount):
        master_sources.append(p_index)
        master_targets.append(i)
        master_values.append(amount)
        master_link_colors.append(cashflow_items[p_index].link_col)
        cashflow_items[p_index].amount += category.amount

# Column 4 (Leaf)
for i, category in enumerate(cashflow_items):
    if(category.parent[-1] == '3'):
        p_index = index_LUT[category.parent] 
        append_sankey_node(p_index, i, category.amount)

# Column 3
for i, category in enumerate(cashflow_items):
    if(category.parent[-1] == '2'):
        p_index = index_LUT[category.parent] 
        append_sankey_node(p_index, i, category.amount)               

# Column 2 (Gross Income)
for i, category in enumerate(cashflow_items):
    if(category.parent[-1] == '1'):
        p_index = index_LUT[category.parent] 
        append_sankey_node(p_index, i, category.amount)  

# Column 1 (Income)      
append_sankey_node(index_LUT['Primary Income0'], index_LUT['Gross Income1'], primary_income)
append_sankey_node(index_LUT['401(k) Match0'], index_LUT['Gross Income1'], match_total)
append_sankey_node(index_LUT['Cashback/Interest0'], index_LUT['Gross Income1'], cashflow_items[index_LUT['Cashback/Interest0']].amount) 

if 'Bonus0' in index_LUT:
    append_sankey_node(index_LUT['Bonus0'], index_LUT['Gross Income1'], bonus_amount) 
if ('HSA Match0' in index_LUT) and not month_flag:
    append_sankey_node(index_LUT['HSA Match0'], index_LUT['Gross Income1'], 600)

# populate node colors
for item in cashflow_items:
    master_node_colors.append(item.node_col)  

#######################################################################
#                     Manipulate Node Labels
#######################################################################

# (just for label purposes)
cashflow_items[index_LUT['Primary Income0']].amount = primary_income
cashflow_items[index_LUT['401(k) Match0']].amount = match_total

if 'Bonus0' in index_LUT:
    cashflow_items[index_LUT['Bonus0']].amount = bonus_amount
if 'HSA Match0' in index_LUT:
    cashflow_items[index_LUT['HSA Match0']].amount = 600

# (just for label purposes) FIXME
if month_flag:
    cashflow_items[index_LUT['Gross Income1']].amount = (primary_income + match_total + bonus_amount + cashback_interest)
else:
    cashflow_items[index_LUT['Gross Income1']].amount = (primary_income + match_total + bonus_amount + 600 + cashback_interest)

cashflow_items[index_LUT['Cashback/Interest0']].amount = cashback_interest

# remove column indicator from labels
for category in cashflow_items:
    master_labels.append(category.label)
master_labels_no_column = [s[:-1] for s in master_labels]

# Add values to the labels
for i, label in enumerate(master_labels_no_column):
    for j in range(len(cashflow_items)):
        if (str(cashflow_items[j].label[:-1]) == str(label)):
            d.write("matched " + str(label) + " with " + str(cashflow_items[j].label) + " amount = " + str(cashflow_items[j].amount) + "\n")
            master_labels_no_column[i] = "{}: ${:,.0f}".format(master_labels_no_column[i], cashflow_items[j].amount)
            # master_labels_no_column[i] = "{}".format(master_labels_no_column[i]) # hide amounts

d.write(str(master_labels_no_column) + "\n")

#######################################################################
#                     Horizontal Node Positioning
#######################################################################

def nodify(node_names):
    node_names = master_labels
    # uniqe name endings
    ends = sorted(list(set([e[-1] for e in node_names])))
    
    # intervals
    steps = 1/len(ends)

    # x-values for each unique name ending
    # for input as node position
    nodes_x = {}
    xVal = 0
    for e in ends:
        nodes_x[str(e)] = xVal
        xVal += steps

    # x and y values in list form
    x_values = [nodes_x[n[-1]] for n in node_names]
    y_values = [0.1]*len(x_values)
    
    return x_values, y_values

nodified = nodify(node_names=master_labels)

xc=nodified[0]
yc=nodified[1]  

#######################################################################
#                     Vertical Node Positioning
#######################################################################

# In general, smaller number means it will be placed higher, larger number means it will be placed lower. Requires some guess/check sometimes
for i, item in enumerate(cashflow_items):
    if item.parent == 'Entertainment3':
        yc[i] = 0.25

for i, item in enumerate(cashflow_items):
    if item.parent == 'Transportation3':
        yc[i] = 0.45 

# used to store a list of column 2 labels and amount to figure out amount order
@dataclass
class sort_logic:
    label: str
    amount: float

# make a list containing labels and amounts
ordered = [sort_logic('Savings2',cashflow_items[index_LUT['Savings2']].amount),
           sort_logic('Taxes2',cashflow_items[index_LUT['Taxes2']].amount),
           sort_logic('Expenses2',cashflow_items[index_LUT['Expenses2']].amount)]

# sort the list by amount
ordered = sorted(ordered, key=lambda x: x.amount)

# biggest amount on top, smallest amount on bottom
for i, item in enumerate(cashflow_items):
    if item.parent == ordered[2].label:
        yc[i] = 0.10
    if item.parent == ordered[1].label:
        yc[i] = 0.15  
    if item.parent == ordered[0].label:
        yc[i] = 0.20   

#######################################################################
#                           Sankey Call
#######################################################################
fig = go.Figure(data=[go.Sankey(
    arrangement='snap',    
    node=dict(
        pad=40,
        thickness=30,
        line=dict(color="black", width=0),
        label=master_labels_no_column,
        color=master_node_colors,
        x = xc,
        y = yc
    ),
    link=dict(
        source=master_sources,
        target=master_targets,
        value=master_values,
        color=master_link_colors
    ))])

fig.update_layout(
    font_family="Helvetica",
    font_color="black",
    font_size=20,
)

if month_flag:
    fig.update_layout(title_text=str(month + " " + year))

# Save the figure as an HTML file
fig.write_html(os.path.join(SF, filename + '.html'))