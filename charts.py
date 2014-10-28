import matplotlib.pyplot as plt
import numpy
import sys

def Plot(filename, title, saveFigure = True):
    with open(filename) as f:
        data = f.read().strip()

    data = data.split("\n")
        
    x_data_raw = []
    y_data = []
    for s in data:
        mid = s.rfind(",")
        row = [s[:mid], s[mid+1:]]
        x_data_raw.append(row[0])
        y_data.append(int(row[1]))
        
    x_data_raw.reverse()
    y_data.reverse()

    # 5x4 inches
    #fig = plt.figure(figsize=(15, 6), dpi=80, frameon = False)
    #fig.subplots_adjust(left=0.05, right=0.55, top=0.9, bottom=0.1, wspace=0, hspace=0)
    fig = plt.figure(figsize=(10, 6), dpi=80, frameon = False)
    fig.subplots_adjust(left=0.06, right=0.95, top=0.9, bottom=0.1, wspace=0, hspace=0)

    xMargin = 1
    yMargin = 2

    y_data = numpy.array(y_data)    
    plt.xlim(-xMargin,len(y_data)+xMargin)
    plt.ylim(0, int(max(y_data)) + yMargin)
    
    plt.yticks(y_data)
    
    ax = fig.add_subplot(1,1,1) # one row, one column, first plot

    #ax.scatter(x_data, y_data, color="red", marker="^")
    #ax.plot(x_data, y_data, "b", linewidth=1.0, linestyle="-")
    x_data = range(len(y_data))
    #alphabet = [s for s in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"[:len(y_data)]]
    alphabet = [str(i) for i in range(1, 2 + len(y_data))]
    plt.xticks(x_data, alphabet, rotation=0)
    ax.plot(x_data, y_data, "bo", linewidth=1.0, linestyle="-")
    
    #ax.set_title(title + "\n(lower is better)")
    #ax.set_title("(lower is better)")
    #ax.set_xlabel("SequenceSize length")     # MBFP
    ax.set_xlabel("WindowSize length")      # Sequence Predictor
    ax.set_ylabel("Ranking")
    
    textstr = ""
    for i, data in enumerate(x_data_raw):
        #textstr +=  "%s: %s\n" % (alphabet[i], data)
        
        data_range = data.split(",")
        data_range = "%s - %s" % (data_range[0], data_range[-1])
        
        textstr +=  "%s: %s\n" % (alphabet[i], data_range)

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='white')

    #ax.text(1.02, 0.99, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)
        
    if saveFigure:
        figureName = str(filename).split(".")[0] + ".png"
        fig.savefig(figureName)
        print ("%s saved" % (figureName))
    else:
        fig.show()

def startPlotting():
    Plot("results_match.csv", "Match Results", saveFigure = True)
    Plot("results_tournament.csv", "Tournament Results", saveFigure = True)    
    #Plot("results_match.csv", "Match Results", saveFigure = False)
    #Plot("results_tournament.csv", "Tournament Results", saveFigure = False)    

if __name__ == "__main__":
    startPlotting()
    input("Press any key to continue")
    plt.close(3)