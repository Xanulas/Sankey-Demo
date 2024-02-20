export COMPUTE_YEAR="2023"
export COMPUTE_MONTH="Dec"

python $PRJ_HOME/python/compute_logic/transaction_consolidate.py --year_month "$COMPUTE_YEAR $COMPUTE_MONTH" --keep_cashback False --include_401k False
