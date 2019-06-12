from jenkinsapi.jenkins import Jenkins
import sqlite3
from datetime import datetime

# defining jenkins parameters
jenkins_url = "http://localhost:8080/"
username = "samuel"
password = "samuel45"

# database details
db_name = "jenkins.db"

#  get server instance
server = Jenkins(jenkins_url, username, password)

# dictionary that holds the jobs name as keys 
jobs_dict = {}


# Connect to the database
conn = sqlite3.connect(db_name)
c = conn.cursor()

c.execute('create table jenkins ( id INTEGER PRIMARY KEY, job_name NOT NULL, status NOT NULL, date_checked TEXT )')


for job_name, job_instance in server.get_jobs():
	if job_instance.is_running():
		status = "Running"
	elif job_instance.get_last_build_or_none() == None :
		status = "NotBuilt"
	else:
		simple_job = server.get_job(job_instance.name)
		simple_build = simple_job.get_last_build()
		status = simple_build.get_status()
		
	i = datetime.now()
	checked_time = i.strftime("%Y/%m/%d %H-%M-%S")
	first_tuple = (job_instance.name, status, checked_time)
	c.execute("SELECT id FROM jenkins WHERE job_name = ?", (job_instance.name,))
	data=c.fetchone()
	if data is None:
		c.execute('INSERT INTO jenkins (job_name, status, date_checked) VALUES (?,?,?)', first_tuple)
	else:
		second_tuple = (status, checked_time, job_instance.name)
		c.execute('UPDATE jenkins SET status=?, date_checked=? WHERE job_name=?', second_tuple)
		
	### Add to dictionary ###
	jobs_dict[job_instance.name] = status
	
# Save (commit) the changes
conn.commit()

# We can close the connection 
conn.close()