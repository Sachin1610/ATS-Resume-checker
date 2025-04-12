
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
    filename_prefix = request.args.get('filename_prefix')  
    if not filename_prefix:
        return jsonify(
            {"error": "filename prefix parameter is missing"}
            ), 400
    s3_object_key = f"recommendations/{filename_prefix}_recommendations.json" 

    try:
        s3response = s3_client.get_object(Bucket='course-recommendations', Key=s3_object_key)
        responsebody=s3response["Body"]
        filecontent = responsebody.read().decode("utf-8")
        recommendedcourses = json.loads(filecontent)
        return jsonify(recommendedcourses), 200
    
    except s3_client.exceptions.NoSuchKey:

        return jsonify(
            {"error": "File does not exists"
             }
             ), 404
    
    except Exception as e:

        return jsonify({
            "error": str(e)
            }), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
