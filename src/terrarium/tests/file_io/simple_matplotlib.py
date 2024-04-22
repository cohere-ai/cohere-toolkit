import matplotlib.pyplot as plt
import numpy as np

# Generate some sample data
x = np.linspace(0, 10, 100)  # Create an array of 100 values from 0 to 10
y = np.sin(x)  # Compute the sine values for each x

# Create a line plot
plt.plot(x, y, label="Sin(x)")
y = np.cos(x)  # Compute the cos values for each x
# Create a line plot
plt.plot(x, y, label="Cos(x)")
plt.plot(x, y + 1, label="Cos(x)+1")
plt.plot(x, y + 2, label="Cos(x)+2")

# Add labels and title
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Simple Matplotlib Example")

# Add a legend
plt.legend()

# Show the plot
# plt.tight_layout()
plt.savefig("plot.png")
plt.savefig("plot.pdf")
plt.savefig("plot.svg")
