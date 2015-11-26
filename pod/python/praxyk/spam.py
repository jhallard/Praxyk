import os
import sys
import getopt
import csv
import praxyk

# TODO: Python docstring
def process_feature(filename):
    #load feature list
    features = []
    features_path = os.path.join(praxyk.get_mlpack_dir(), "features.txt")
    try:
        features_file = open(features_path, "r")
    except IOError:
        raise RuntimeError(features_path + " missing.")
        exit()
    for line in features_file:
        features.append(line.strip())
    csv_path = os.path.join("/tmp", (filename + ".csv"))
    output = open(csv_path, "a")
    try:
        test_file = open(filename, "r").read()
    except IOError:
        print "IOError: " + filename
    test_entry = []
    for word in features:
        test_entry.append(test_file.count(word))
    writer = csv.writer(output)
    writer.writerow(test_entry)
    return csv_path

def bayes_spam(filename_path):
    csv_path = process_feature(filename_path)
    return praxyk.praxyk_python.__get_spam_chance(csv_path)

#entry_list = []
#output = open("output.csv", "a")
#writer = csv.writer(output)
#for filename in sys.argv[1:]:
    #read file
#    try:
#        test_file = open(filename, "r").read()
#    except IOError:
#        print "Ioerror: " + filename
#        continue
#    test_entry = []
#    for word in features:
        #incase we need binary attributes
    #    if word in test_file:
    #        test_entry.append(1)
    #    else:
    #        test_entry.append(0)
#        test_entry.append(test_file.count(word))
#    writer.writerow(test_entry)
#    entry_list.append(test_entry)
#with open("output.csv", "wb") as f:
#    writer = csv.writer(f)
#    writer.writerows(entry_list)
