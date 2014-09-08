import matplotlib.pyplot as plt
import numpy
import sys

def Plot(filename, title, saveFigure = True):
    with open(filename) as f:
        data = f.read().strip()

    data = data.split("\n")
        
    x_data = []
    y_data = []
    for s in data:
        mid = s.rfind(",")
        row = [s[:mid], s[mid+1:]]
        x_data.append(row[0])
        y_data.append(row[1])

    # 5x4 inches
    fig = plt.figure(figsize=(10, 6), dpi=80, frameon = False)
    fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1, wspace=0, hspace=0)

    xMargin = 2
    yMargin = 2
    
    plt.xlim(-xMargin,len(y_data)+xMargin)
    plt.ylim(0, int(max(y_data)) + yMargin)
    
    #plt.yticks(numpy.linspace(-1, 1, 5, endpoint=True))
    
    ax = fig.add_subplot(1,1,1) # one row, one column, first plot

    #y_data = numpy.random.normal(5.0, 3.0, 1000)
    y_data = numpy.array(y_data)
    #ax.scatter(x_data, y_data, color="red", marker="^")
    #ax.plot(x_data, y_data, "b", linewidth=1.0, linestyle="-")
    #ax.plot([s for s in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(y_data)]], y_data, "b", linewidth=1.0, linestyle="-")
    ax.plot(range(len(y_data)), y_data, "b", linewidth=1.0, linestyle="-")
    
    #ax.set_title(title + "\n(lower is better)")
    #ax.set_title("(lower is better)")
    ax.set_xlabel("SequenceSize")
    ax.set_ylabel("Ranking")

    if saveFigure:
        figureName = str(filename).split(".")[0] + ".png"
        fig.savefig(figureName)
        print ("%s saved" % (figureName))
    else:
        fig.show()

def startPlotting():
    #Plot("results_match.csv", "Match Results", True)
    #Plot("results_tournament.csv", "Tournament Results", True)    
    Plot("results_match.csv", "Match Results", False)
    #Plot("results_tournament.csv", "Tournament Results", True)    

if __name__ == "__main__":
    startPlotting()
    input("Press any key to continue")
    plt.close(3)