# This script shows how to connect to a JIRA instance with a
# username and password over HTTP BASIC authentication.
import os
import ConfigParser
import datetime
import pytz
import smtplib
from dateutil.parser import parse
from jira.client import JIRA
from jira.config import get_jira
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

config = ConfigParser.ConfigParser()
config.read("jira.ini")
username = config.get('jira', 'user')
password = config.get('jira', 'password')
url = config.get('jira', 'url')
myname = config.get('jira', 'myname')
server = {'server': url}
myname = myname.strip(' ,\t\n\r')

today = datetime.datetime.now();
lastweek = today - datetime.timedelta(weeks=1)
lastweek = pytz.utc.localize(lastweek)

# -------------------------------------------------------------
# email setup
emailfrom = config.get('email', 'emailfrom')
emailto = config.get('email', 'emailto')
emailsmtp = config.get('email', 'emailsmtp')
emailsubject = "Your JIRA comments since " + str(lastweek)
# -------------------------------------------------------------

# By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK.
# See https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details.
jira = JIRA(options=server, basic_auth=(username, password))    # a username/password tuple

# Find all issues reported by me
#issues = jira.search_issues('assignee=michelth')

# Find the top three projects containing issues reported by me
#from collections import Counter
#top_three = Counter([issue.fields.project.key for issue in issues]).most_common(3)

#issues_in_proj = jira.search_issues('project=ACD')
#all_proj_issues_but_mine = jira.search_issues('project=ACD and assignee != currentUser()')

# my top 5 issues due by the end of the week, ordered by priority
#oh_crap = jira.search_issues('assignee = currentUser() and due < endOfWeek() order by priority desc', maxResults=5)

def sendtheemail(emailtext):
    msg = MIMEMultipart()
    msg['From'] = emailfrom
    msg['To'] = emailto
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = emailsubject
    msg.attach( MIMEText(emailtext, 'html') )
    smtp = smtplib.SMTP(emailsmtp)
    smtp.sendmail(emailfrom, emailto, msg.as_string())
    smtp.close()
    print "email sent to " + emailto

# Summary of my last 10 assigned issues
emailbody = "<b>Found these JIRAs:</b><BR>"
emailbodynocommentsthisweek = "<BR><hr><b>Found these JIRAs without comments this week:</b><BR>"
emailbodynocomments = "<BR><hr><b>Found these JIRAs without comments:</b><BR>"
for issue in jira.search_issues('assignee = currentUser() and project=ACD order by updated desc', maxResults=10):
    print issue
    print "Issue summary: " + issue.fields.summary
    numcomments = 0
    numcommentsthisweek = 0
    for comment in jira.comments(issue):
        numcomments += 1
        author = str(comment.author)
        author = author.strip(' ,\t\n\r')
        if author == myname:
            print "Comment by: " + myname
            commentdate = parse(str(comment.updated))
            print "comment updated on: " + str(commentdate)
            if commentdate >= lastweek:
                if numcomments == 1:
                    emailbody += "<BR>" + str(issue) + ": " + issue.fields.summary + "<BR>"
                numcommentsthisweek += 1
                print "Ok, comment after: " + str(lastweek)
                print comment.body
                emailbody += unicode(comment.body).encode('ascii', 'ignore') + "<BR>"
            else:
                print "ignoring comments from previous weeks"
                print "I only process comments created after: " + str(lastweek)
            print ""
        else:
            print "ignoring comment from: " + str(comment.author)
        #attrs = vars(comment)
        #print ', '.join("A: %s: B: %s" % item for item in attrs.items())
    if numcommentsthisweek == 0 and numcomments != 0:
        print "No comments found this week.\n"
        emailbodynocommentsthisweek += "<BR>" +str(issue) + ": " + issue.fields.summary + "<BR>"
    elif numcomments == 0:
        print "No comments found.\n"
        emailbodynocomments += "<BR>" + str(issue) + ": " + issue.fields.summary + "<BR>"
    print "----------"

sendtheemail(emailbody + emailbodynocommentsthisweek + emailbodynocomments)
print "bye"
