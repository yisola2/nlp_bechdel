import pandas as pd

# Read the CSV files
male_df = pd.read_csv('data/male.csv')
female_df = pd.read_csv('data/female.csv')

# Convert names to lowercase
male_df['name'] = male_df['name'].str.lower()
female_df['name'] = female_df['name'].str.lower()

# Save the modified files
male_df.to_csv('data/male.csv', index=False)
female_df.to_csv('data/female.csv', index=False)

print("Names have been converted to lowercase in both files.") 