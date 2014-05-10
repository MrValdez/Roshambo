import matplotlib.pyplot as plt
import sys

# Create some data to plot
#num_datapoints = 1000
#x_data = [x for x in range(0,num_datapoints)]
#y_data = [random.randint(17,20) for i in range(0, num_datapoints)]

with open("results_match.csv") as f:
    data = f.read().strip()

data = data.split("\n")
    
x_data = [s.split(',')[0] for s in data]
y_data = [s.split(',')[1] for s in data]

fig = plt.figure(figsize=(5, 4))
ax = fig.add_subplot(1,1,1) # one row, one column, first plot

ax.scatter(x_data, y_data, color="red", marker="^")

ax.set_title("Match results")
ax.set_xlabel("targetTurn")
ax.set_ylabel("Ranking")

#fig.savefig("scatterplot.png")
fig.show()

input("Press any key to continue")