#!py2.7
import webbrowser

import json as simplejson
import urllib

CHART_BASE_URL = 'http://chart.googleapis.com/chart'

def getChart(chartData, chartDataScaling="0,30", chartType="lc",chartLabel="Ranking",chartSize="500x160", chartColor="orange", **chart_args):
    chartSize = "500x480"
    chart_args.update({
        'cht': chartType,
        'chs': chartSize,
        'chl': chartLabel,
        'chco': chartColor,
        'chds': chartDataScaling,
        'chxt': 'x,y',
        'chxr': '1,1,20'
    })

    dataString = 't:' + ','.join(str(x) for x in chartData)
    chart_args['chd'] = dataString.strip(',')

    chartUrl = CHART_BASE_URL + '?' + urllib.urlencode(chart_args)

    webbrowser.open(chartUrl)
    
#input()

import os

filebase = "./results/"

def DoCheck():
    csv = ""
    ranks = []
    print ("RANK   VARIABLE")
    for variable in range(0, 1000):
    #for variable in range(0, 350):
        number = str(variable).zfill(4)
        filename = filebase + "results %s.txt" % (number)

        if not os.path.isfile(filename):
            print ("%s is missing" % (filename))
            break
            
        with open(filename) as f:
            text = f.read()
            found = text.rfind("Yomi AI")
            if found == -1:
                print("MAJOR PARSING ERROR")
                break
            start = text.rfind("\n", 0, found - 4)
            end = text.find("Yomi AI", found)
            #print (start, end)
            #line = text[found - 10] == "\n"
            #print (line)
            rank = str(text[start:end].strip())
            ranks.append(rank)
            print (" %s        %s" % (rank, number))            
            csv += "%s,%s\n" % (number, rank)

    #getChart(ranks)
    with open("results2.csv", "w") as f:
        f.write(csv)
        
DoCheck()