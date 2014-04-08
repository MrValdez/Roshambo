import subprocess

filebase = "./results/"

for variable in range(0, 1000):
    filename = filebase + "results %s.txt" % (str(variable).zfill(4))
    #print (filename)
    
    with open(filename, "w") as f:
        output = subprocess.check_output(["go.exe", str(variable)], universal_newlines = True)
        stdout = str(output)
        f.write(stdout)
    
    print("%s is done." % (filename))
    #input()
    