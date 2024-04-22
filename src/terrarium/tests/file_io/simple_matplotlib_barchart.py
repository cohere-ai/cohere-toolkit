import matplotlib.pyplot as plt

# Data for plot
data = {"Olympus Mons": 72000, "Ascraeus Mons": 11200, "Arsia Mons": 10000}

# Create horizontal bar chart
width = 10
colors = ["#FFA500", "#FFC000", "#FFB74D"]

for i, (mountain, height) in enumerate(data.items()):
    plt.barh(mountain, height, color=colors[i], edgecolor="black")

plt.xlabel("Height (feet)")
plt.savefig("mars_mountains.png")
