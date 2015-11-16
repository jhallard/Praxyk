import os
import sys
import getopt
import csv
import praxyk

def process_feature(filename):
	#load feature list
	features = []
	print praxyk.get_mlpack_dir()
	try:
		features_file = open(praxyk.get_mlpack_dir() + "/features.txt", "r")
	except IOError:
		raise RuntimeError(praxyk.get_mlpack_dir() + "features.txt missing.")
		exit()
	for line in features_file:
		features.append(line.strip())
	output = open(filename + ".csv", "a")
	try:
		test_file = open(filename, "r").read()
	except IOError:
		print "Ioerror: " + filename
	test_entry = []
	for word in features:
		test_entry.append(test_file.count(word))
	writer = csv.writer(output)
	writer.writerow(test_entry)

def bayes_spam(filename_path):
	process_feature(filename_path)
	return get_spam_chance(filename_path + ".csv")

#entry_list = []
#output = open("output.csv", "a")
#writer = csv.writer(output)
#for filename in sys.argv[1:]:
	#read file
#	try:
#		test_file = open(filename, "r").read()
#	except IOError:
#		print "Ioerror: " + filename
#		continue
#	test_entry = []
#	for word in features:
		#incase we need binary attributes
	#	if word in test_file:
	#		test_entry.append(1)
	#	else:
	#		test_entry.append(0)
#		test_entry.append(test_file.count(word))
#	writer.writerow(test_entry)
#	entry_list.append(test_entry)
#with open("output.csv", "wb") as f:
#	writer = csv.writer(f)
#	writer.writerows(entry_list)
