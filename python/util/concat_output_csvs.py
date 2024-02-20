import pandas as pd
import os

SF = os.environ.get('SF')

directory_path = os.path.join(SF, 'Sankey-Demo/Transactions-to-Plot')

csv_files = [file for file in os.listdir(directory_path) if file.endswith('.csv')]

# Check if there are at least 2 CSV files to combine
if len(csv_files) == 0:
    print("Error: There are not enough CSV files to combine.")
elif len(csv_files) == 1:

    single_csv_file = csv_files[0]

    single_df = pd.read_csv(os.path.join(directory_path, single_csv_file))

    single_df.to_csv(os.path.join(directory_path, 'combined.csv'), index=False)

    print(f"Single CSV file '{single_csv_file}' copied successfully. The result is stored in 'combined.csv'.")
else:
    dfs = []

    for file in csv_files:
        current_df = pd.read_csv(os.path.join(directory_path, file))
        dfs.append(current_df)

    combined_df = pd.concat(dfs, ignore_index=True)

    combined_df.to_csv(os.path.join(directory_path, 'combined.csv'), index=False)

    print("CSV files combined successfully. The result is stored in 'combined.csv'.")