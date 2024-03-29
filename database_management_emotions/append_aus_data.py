import pandas as pd

# Load the CSV files
file1_path = '.\\database_management_emotions\\diffusionFER_aus.csv'
file2_path = '.\\database_management_emotions\multiemoVA_aus.csv'

df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)


df2 = df2[df1.columns]

# Concatenate dataframes vertically
concatenated_df = pd.concat([df1, df2], ignore_index=True)

# Save the result to a new CSV file
output_path = '.\database_management_emotions\\aus.csv'
concatenated_df.to_csv(output_path, index=False)





