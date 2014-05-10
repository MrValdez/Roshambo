import matplotlib.pyplot as plt
import sys

def Plot(filename, title, saveFigure = True):
    #num_datapoints = 1000
    #x_data = [x for x in range(0,num_datapoints)]
    #y_data = [random.randint(17,20) for i in range(0, num_datapoints)]

    with open(filename) as f:
        data = f.read().strip()

    data = data.split("\n")
        
    x_data = [s.split(',')[0] for s in data]
    y_data = [s.split(',')[1] for s in data]

    fig = plt.figure(figsize=(5, 4))
    ax = fig.add_subplot(1,1,1) # one row, one column, first plot

    ax.scatter(x_data, y_data, color="red", marker="^")

    ax.set_title(title)
    ax.set_xlabel("targetTurn")
    ax.set_ylabel("Ranking")

    if saveFigure:
        figureName = str(filename).split(".")[0] + ".png"
        fig.savefig(figureName)
    else:
        fig.show()

def startPlotting():
    Plot("results_match.csv", "Match Results", False)
    Plot("results_tournament.csv", "Tournament Results", False)    

if __name__ == "__main__":
    startPlotting()
    input("Press any key to continue")