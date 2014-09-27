import sys
import os
import re
import mmap
import csv

# Usage: python parse.py <PATH_TO>/file.c parsed.csv
# Update the sourcePath to point the branch you want to use.
sourcePath = "/usr3/dev/perforce/mainline/Source/"
# ------------------------------------------------------------

inwafile, outcsvfile = sys.argv[1], sys.argv[2]
fieldnames = ['WA Name', 'Needed for', 'Component', 'HWBugLink', 'HWSightingLink', 'Platform' ]

def validfile(filename):
	# It's a c/cpp/cxx/h/hpp file
	# It's bigger than 0
	# It isn't a symlink
	# It isn't the wa definition file
	if filename.endswith('.c') or filename.endswith('.cxx') or filename.endswith('.h') or \
			filename.endswith('.cpp') or filename.endswith('.hpp') :
		if (filename.endswith('_wa.h') == False) and (filename.endswith('_wa.c') == False) :
			if os.path.getsize(filename) > 0 :
				if os.path.islink(filename) == False :
					return True
	return False

def grep(path, name):
	res = []
	for root, dirs, fnames in os.walk(path):
		for fname in fnames:
			if validfile(os.path.join(root, fname)) :
				tmpfile = open(os.path.join(root, fname), 'r')
				tmpdata = mmap.mmap(tmpfile.fileno(), 0, prot=mmap.PROT_READ)
				if re.search(name, tmpdata):
					libname = re.sub('^.*Source/', '', root)
					# Don't add duplicates
					if (libname in res) == False :
						res.append(libname)
	return res


try:
	wafile = open(inwafile, 'r')
	csvwriter = csv.writer(open(outcsvfile, "wb"))
	csvwriter.writerow(fieldnames)

	for line in wafile:
		if re.search(r"WA_ENABLE", line):
			csvline = []
			ulStepId = next(wafile).strip(' ,;)"\t\n\r')
			waName = next(wafile).strip(' ,;)"\t\n\r')
			hwBugLink = next(wafile).strip(' ,;)"\t\n\r')
			hwSightingLink = next(wafile).strip(' ,;)"\t\n\r')
			platform = next(wafile).strip(' ,;)"\t\n\r')
			stepping = next(wafile).strip(' ,;)"\t\n\r')
			print waName + " found"
			component = grep(sourcePath, waName)
			csvline.append(waName)
			csvline.append(stepping)
			csvline.append(component)
			csvline.append(hwBugLink)
			csvline.append(hwSightingLink)
			csvline.append(platform)
			csvwriter.writerow(csvline)

finally:
	wafile.close()
	del csvwriter
	print "bye"