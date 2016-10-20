import os
import psycopg2
from flask import Flask, render_template, request
import urlparse
from os.path import exists
from os import makedirs

app = Flask(__name__)

# [START DB connection]
url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
db = ("dbname=%s user=%s password=%s host=%s" % 
		 (url.path[1:], url.username, url.password, url.hostname))
schema = "schema.sql"
conn = psycopg2.connect(db)
# [END DB connection]

# Set DB cursor
cur = conn.cursor()

# This function is designed to parse a DB object serialized in a GET request
def parseRequestVars(request):

	# Strip enclosing parens
	request = request[1:-1]

	# Split request into list by its corresponding attributes
	request = request.split(', ')

	# Strip leading and trailing quotes around object attribute
	request = [x[1:-1] for x in request]
	return request


# [START Routing functions]
@app.route('/', methods=['GET'])
def home():
	"""Returns full page rendered template
	This function gets all students stored in the DB and passes them as template
	variables.

	Params: None
	"""
	cur_student = []

	cur.execute("""SELECT name, sfid, instrument__c FROM salesforce.student__c""")
	students = cur.fetchall()

	return render_template('base.html', students=students)


@app.route('/book', methods=['GET'])
def getTeachers():
	"""Returns full page rendered template
	This function gets all teachers and rooms from the DB. Teachers that are
	authorized to teach the instrument of the student passed to this function
	are passed as template variables, along with all rooms and the current
	student.

	Params: student (URL serialized DB object as string)

	Note: student parameter has the form: ('Student Name', 'SFID', 'Instrument'),
				where SFID == 18 character sequence.
	"""
	try:
		teachers = []

		# cur_student is a list of the student's attributes
		cur_student = parseRequestVars(request.args['student'])

		# The Salesforce "multipicklist" type, which is the type of the instrument
		# is particularly tricky. Query results are filtered here instead of on DB
		# for this reason. instrument__c type returned is a tuple.
		cur.execute("""SELECT name, sfid, instrument__c FROM salesforce.teacher__c""");
		potential_teachers = cur.fetchall()

		cur.execute("""SELECT name, sfid FROM salesforce.room__C ORDER BY name ASC""");
		rooms = cur.fetchall()

		# Filter the teachers to be valid options for client lesson booking
		for x in potential_teachers:

			# If cur_student's instrument is in teacher's instrument__c tuple, teacher
			# is a potential teacher for this student
			if cur_student[2] in x[2]:
				teachers.append(x)

		return render_template('base.html', teachers=teachers, student=cur_student, rooms=rooms)
	except Exception as e:
		print e
		message = "There was an error with your request."
		return render_template('base.html', message=message)


@app.route('/book', methods=['POST'])
def bookLesson():
	"""Returns full page rendered template
	This function inserts a new lesson into the DB with the specified attributes.
	Success or failure message is the only template variable.

	Params: student (sfid), teacher (sfid), room (sfid), duration, scheduledTime
	"""
	try:
		# Lesson name is hardcoded, non-unique, not visible by client
		lesson_name = "Form Lesson"
		student = request.form['student']
		teacher = request.form['teacher']
		duration = request.form['duration']
		lesson_datetime = str(request.form['scheduledTime'])
		room = request.form['room']

		# In psycopg2, the type of the values are converted into appropriate field
		# types, so "%s" is used for all types
		cur.execute("""INSERT INTO salesforce.lesson__C (name, student__c, teacher__c, room__c, start_datetime__c, duration__c) 
								   VALUES (%s, %s, %s, %s, %s, %s)""", 
							 		 (lesson_name, student, teacher, room, lesson_datetime, duration))

		conn.commit()

		message = "Your lesson has been booked! A confirmation email will be sent to you shortly."

		return render_template('base.html', message=message)
	except Exception as e:
		print e
		message = "There was an error with your request. Your lesson was not booked."
		return render_template('base.html', message=message)
# [END Routing functions]

if __name__ == '__main__':
	app.run()
