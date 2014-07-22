import matplotlib.pyplot as plt
import numpy
import sys

def Plot(filename, title, saveFigure = True):
    with open(filename) as f:
        data = f.read().strip()

    data = data.split("\n")
        
    x_data = [x for x in range(100)]
    y_data = [float(x) * 100 for x in data]

    # 5x4 inches
    fig = plt.figure(figsize=(10, 6), dpi=80, frameon = False)
    fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1, wspace=0, hspace=0)

    #xMargin = 30
    #yMargin = 2
    xMargin = 0
    yMargin = 0
    
    plt.xlim(-xMargin,100+xMargin)
    plt.ylim(0, 100 + yMargin)
    
    #plt.yticks(numpy.linspace(-1, 1, 5, endpoint=True))
    
    ax = fig.add_subplot(1,1,1) # one row, one column, first plot

    #y_data = numpy.random.normal(5.0, 3.0, 1000)
    y_data = numpy.array(y_data)
    #ax.scatter(x_data, y_data, color="red", marker="^")
    ax.plot(x_data, y_data, "b", linewidth=1.0)

    # add labels for yomi
    layer1max = 30
    layer2max = 40
    plt.xticks([layer1max, layer2max])
    yPos = -10
    plt.text(layer1max / 2, yPos, "Layer 1", fontsize = 14)
    plt.text((layer1max + layer2max) / 2, yPos, "Layer 2", fontsize = 14)
    plt.text((layer2max) + ((100 - layer2max) / 2), yPos, "Layer 3", fontsize = 14)
    
    #ax.set_title("(lower is better)")
    ax.set_xlabel("targetPredictionSize")
    ax.set_ylabel("Ranking")

    if saveFigure:
        figureName = str(filename).split(".")[0] + ".png"
        fig.savefig(figureName)
        print ("%s saved" % (figureName))
    else:
        fig.show()

def startPlotting():
    Plot("foo.csv", "Confidence Level", False)

if __name__ == "__main__":
    startPlotting()
    input("Press any key to continue")
    plt.close(3)