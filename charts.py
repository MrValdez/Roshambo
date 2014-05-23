import matplotlib.pyplot as plt
import numpy
import sys

def Plot(filename, title, saveFigure = True):
    with open(filename) as f:
        data = f.read().strip()

    data = data.split("\n")
        
    x_data = [s.split(',')[0] for s in data]
    y_data = [s.split(',')[1] for s in data]

    # 5x4 inches
    fig = plt.figure(figsize=(10, 6), dpi=80, frameon = False)
    fig.subplots_adjust(left=0.05, right=1.0, top=0.9, bottom=0.1, wspace=0, hspace=0)

    xMargin = 30
    yMargin = 2
    
    plt.xlim(-xMargin,1000+xMargin)
    plt.ylim(0, int(max(y_data)) + yMargin)
    
    #plt.yticks(numpy.linspace(-1, 1, 5, endpoint=True))
    
    ax = fig.add_subplot(1,1,1) # one row, one column, first plot

    #y_data = numpy.random.normal(5.0, 3.0, 1000)
    y_data = numpy.array(y_data)
    #ax.scatter(x_data, y_data, color="red", marker="^")
    ax.plot(x_data, y_data, "b", linewidth=1.0, linestyle="-")
    
    ax.set_title(title + "\n(lower is better)")
    ax.set_xlabel("targetTurn")
    ax.set_ylabel("Ranking")

    if saveFigure:
        figureName = str(filename).split(".")[0] + ".png"
        fig.savefig(figureName)
        print ("%s saved" % (figureName))
    else:
        fig.show()

def startPlotting():
    Plot("results_match.csv", "Match Results", True)
    Plot("results_tournament.csv", "Tournament Results", True)    

if __name__ == "__main__":
    startPlotting()
    input("Press any key to continue")
    plt.close(3)