# This file provided just as an example, but is not functional with demo

rm $SF/Consolidate_Script/Outputs_Combined/*

python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "2023 Aug" --keep_cashback True --include_401k True
cp $PRJ_HOME/worklib/consolidated_transactions.csv $SF/Consolidate_Script/Outputs_Combined/1.csv
python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "2023 Sep" --keep_cashback True --include_401k True
cp $PRJ_HOME/worklib/consolidated_transactions.csv $SF/Consolidate_Script/Outputs_Combined/2.csv
python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "2023 Oct" --keep_cashback True --include_401k True
cp $PRJ_HOME/worklib/consolidated_transactions.csv $SF/Consolidate_Script/Outputs_Combined/3.csv
python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "2023 Nov" --keep_cashback True --include_401k True
cp $PRJ_HOME/worklib/consolidated_transactions.csv $SF/Consolidate_Script/Outputs_Combined/4.csv
python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "2023 Dec" --keep_cashback True --include_401k True
cp $PRJ_HOME/worklib/consolidated_transactions.csv $SF/Consolidate_Script/Outputs_Combined/5.csv
python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "2024 Jan" --keep_cashback True --include_401k True
cp $PRJ_HOME/worklib/consolidated_transactions.csv $SF/Consolidate_Script/Outputs_Combined/6.csv

# delete output if it exists
[ -e "$SF/Consolidate_Script/Outputs_Combined/combined.csv" ] && rm "$SF/Consolidate_Script/Outputs_Combined/combined.csv"
python $PRJ_HOME/python/util/concat_output_csvs.py

python $PRJ_HOME/python/plotting/plot_sankey.py --month_flag False --filename one_year