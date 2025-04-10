
import json
from fetch_jobs_api import extract_skills, fetch_jobs
from flask_cors import CORS
from flask import Flask,request
import s3upload as file_upload
from flask import jsonify
import boto3
app = Flask(__name__)

CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})
s3_client = boto3.client("s3")

#Upload resume to S3
@app.route('/upload_data', methods=['POST'])
def upload_data():

   title = request.form.get('jobTitle')
   resume = request.files.get('resume')
   filename = resume.filename 
   file_upload_status=file_upload.resume_upload(resume,filename,title)
   if file_upload_status:
          return {
           'Message': 'Success',
       }
   else:
         return {
           'Message': 'Failed'
       }
   
#get_job_description_skills
@app.route('/extracts_job_skills', methods=['GET'])
def extract_job_requirement_skills():
    title = request.args.get('job_title')
    if not title:
        return jsonify(
            {
                "error": "Job title is required"
            }), 400
    job_description = fetch_jobs(title)
    if isinstance(job_description, str):  
        
        return jsonify(
            {
            "error": job_description}), 500
    skills = extract_skills(job_description)
    return jsonify({"skills": list(skills)})

#get recommended course
@app.route("/get_recommended_courses", methods=["GET"])
def get_recommended_courses():
    pass
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
