# delete output directory (don't do this and ye get bad data!)
rm -f $SF/Sankey-Demo/Transactions-to-Plot/*

export COMPUTE_YEAR="2023"
export COMPUTE_MONTH="Dec"

python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "$COMPUTE_YEAR $COMPUTE_MONTH" --keep_cashback True --include_401k True
cp $PRJ_HOME/worklib/consolidated_transactions.csv $SF/Sankey-Demo/Transactions-to-Plot/1.csv

# delete output if it exists
[ -e "$SF/Sankey-Demo/Transactions-to-Plot/combined.csv" ] && rm "$SF/Sankey-Demo/Transactions-to-Plot/combined.csv"
python $PRJ_HOME/python/util/concat_output_csvs.py

python $PRJ_HOME/python/plotting/plot_sankey.py --year_month "$COMPUTE_YEAR $COMPUTE_MONTH" --filename demo_version --month_flag True
