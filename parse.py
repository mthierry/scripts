import sys
import os
import re
import mmap
import csv
import smtplib
import diff_match_patch
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

info  = "# Usage: python parse.py <PATH_TO>/file_to_parse.c parsedoutput.csv [reference.csv]\n"
info += "# If a reference.csv is given, an email with diffs will be generated.\n"
info += "# Remember to update 'sourcePath'\n"

# Update the sourcePath to point the branch you want to use.
sourcePath = "/usr3/dev/perforce/mainline/Source/"
# ------------------------------------------------------------
if len(sys.argv) < 2 :
	print "Not enough parameters"
	print info
	sys.exit(0)

inwafile, outcsvfile = sys.argv[1], sys.argv[2]

if len(sys.argv) == 4 :
	prevcsvfile = sys.argv[3]

inwacommentsfile = sourcePath + "the_comments_file.h"
fieldnames = ['WA Name', 'Needed for', 'Component', 'HWBugLink', 'HWSightingLink', 'Platform', 'Description' ]

# -------------------------------------------------------------
# email setup
emailfrom = "someone@emal.com"
emailto = "someone@emal.com"
emailsmtp = "smtp.mail.com"
emailsubject = "update detected in " + re.sub('^.*Source/', '', inwafile)
emailfileinfo  = str("<p><b>New CSV file:</b> %s<br>" % outcsvfile)
if len(sys.argv) == 4 :
	emailfileinfo += str("<b>Reference CSV file:</b> %s</p>" % prevcsvfile)

emailtext = " new (or renamed) _magic_ found:<br><br>"
emailchangescount = 0
sendemail = False
wainprevcsvfile = False
# -------------------------------------------------------------

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

def gethtmldiff(fromfile, tofile):
	#create a diff_match_patch object
	dmp = diff_match_patch.diff_match_patch()

	# Depending on the kind of text you work with, in term of overall length
	# and complexity, you may want to extend (or here suppress) the
	# time_out feature
	dmp.Diff_Timeout = 0   # or some other value, default is 1.0 seconds

	# All 'diff' jobs start with invoking diff_main()
	diffs = dmp.diff_main(file(fromfile).read(), file(tofile).read())

	# diff_cleanupSemantic() is used to make the diffs array more "human" readable
	dmp.diff_cleanupSemantic(diffs)

	# and if you want the results as some ready to display HMTL snippet
	htmlSnippet = dmp.diff_prettyHtml(diffs)
	htmlSnippet = re.sub('&para;', '', htmlSnippet)
	return htmlSnippet

def sendtheemail(emailtext, emailfiles=[]):
	msg = MIMEMultipart()
	msg['From'] = emailfrom
	msg['To'] = emailto
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = emailsubject
	htmltext = gethtmldiff(emailfiles[1], emailfiles[0])
	msg.attach( MIMEText(emailtext + htmltext, 'html') )

	for f in emailfiles:
		part = MIMEBase('application', "octet-stream")
		part.set_payload( open(f,"rb").read() )
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
		msg.attach(part)

	smtp = smtplib.SMTP(emailsmtp)
	smtp.sendmail(emailfrom, emailto, msg.as_string())
	smtp.close()
	print "email sent to " + emailto

# _main_:
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
			# find more info from comments file .h
			wacommentsfile = open(inwacommentsfile, 'r')
			for commentline in wacommentsfile:
				if re.search(r"%s" % waName, commentline):
					description = next(wacommentsfile).strip(' ,;)"\t\n\r')
					break
			wacommentsfile.close()
			csvline.append(waName)
			csvline.append(stepping)
			csvline.append(component)
			csvline.append(hwBugLink)
			csvline.append(hwSightingLink)
			csvline.append(platform)
			csvline.append(description)
			csvwriter.writerow(csvline)

			# report newly found/changed _magic_ if reference csv was given
			if len(sys.argv) == 4 :
				prevwafile = open(prevcsvfile, 'r')
				for anotherline in prevwafile:
					if re.search(r"%s" % waName, anotherline):
						wainprevcsvfile = True
						break
				prevwafile.close()

				if wainprevcsvfile == False:
					emailchangescount += 1
					emailtext += "<b>" + waName + "</b>, " + stepping + ", component(s): " + "".join(component)
					emailtext += "<br><br>"
					sendemail = True

				wainprevcsvfile = False

finally:
	wafile.close()
	del csvwriter
	if sendemail == True :
		emailtext = "<p>" + `emailchangescount` + emailtext + "<br>"
		emailtext += "<hr><br><b>Full CSV diff:</b><br>"
		emailtext += "(green = added, red = removed)<br><br>"
		attachements = [outcsvfile, prevcsvfile]
		sendtheemail(emailfileinfo + emailtext, attachements)
	print "bye"
