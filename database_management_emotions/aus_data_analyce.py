import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



data=pd.read_csv('.\database_management_emotions\\aus.csv')


# Define the columns of interest
au_names = ['AU01', 'AU02', 'AU04', 'AU05', 'AU06', 'AU07', 'AU09', 'AU10', 'AU11', 'AU12', 'AU14', 'AU15', 'AU17', 'AU20', 'AU23', 'AU24', 'AU25', 'AU26', 'AU28', 'AU43']

# Separate data into positive and negative
positive_data = data[data['valence'] > 0]
negative_data = data[data['valence'] < 0]

# Calculate means
positive_means = positive_data[au_names].mean()
negative_means = negative_data[au_names].mean()

# Calculate absolute difference
absolute_difference = np.abs(positive_means - negative_means)

# Calculate mean absolute difference
mean_absolute_difference = absolute_difference.mean()

# Sort AU names based on absolute differences
sorted_au_names = sorted(au_names, key=lambda x: absolute_difference[x], reverse=True)

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(sorted_au_names, [absolute_difference[au] for au in sorted_au_names], color='skyblue', marker='o')
plt.title('Absolute Difference of Means for AUs between Positive and Negative Conditions')
plt.xlabel('AU')
plt.ylabel('Absolute Difference of Means')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Save the plot
plt.savefig('.\database_management_emotions\\general_aus_visualization.png')

# Show the graph
plt.show()

