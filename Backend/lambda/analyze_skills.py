import json
import traceback
import boto3
import os

dynamodb = boto3.resource('dynamodb')
skills_table = dynamodb.Table('Skills')
courses_table = dynamodb.Table('Courses')
s3 = boto3.client('s3')

def analyze_skills(resume_skills_text, job_description_skills):
   
    resume_skills_extraction = set()

    for l in resume_skills_text.split("\n"):
        for skill in l.split(","):
            strip_skill = skill.strip()
            if strip_skill: 
                resume_skills_extraction.add(strip_skill.lower())


    matched_skills = list(job_description_skills & resume_skills_extraction)
    missing_skills = list(job_description_skills - resume_skills_extraction)

    result = {}

    result["matched_skills"] = matched_skills

    result["missing_skills"] = missing_skills
    return result


def retrieve_and_analyze_skills_from_s3(bucket_name, object_key):
    try:
        s3response = s3.get_object(Bucket=bucket_name, Key=object_key)
        data = json.loads(s3response["Body"].read().decode("utf-8"))

        resume_skills = "\n".join(data.get("skills_content", []))
        job_skills = set()

        if "api_response" in data:
            api_response = data["api_response"]
            if "skills" in api_response:
                job_skills = set(api_response["skills"])

        result=analyze_skills(resume_skills, job_skills)
        return result

    except Exception as e:
        print(f"ERROR: An error occurred: {e}")
        return None


def recommend_courses(missing_skills):
    recommended_courses_list = []
    missing_skill_names = []
    for missing_skill in missing_skills:
        #skills table scan
        response_data = skills_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('skill_name').eq(missing_skill)
        )
        items_in_response = response_data.get('Items', [])

        if items_in_response:

            if items_in_response and 'skill_id' in items_in_response[0]:
                
                missing_skill_names.append(missing_skill)
                skill_id = items_in_response[0]['skill_id']

            else:

                skill_id = None

            #course table scan
            response_data = courses_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('skills_covered').contains(skill_id)
            )
    
            course_items = response_data.get('Items', [])

            for c in course_items:
                recommended_courses_list.append({
                    'course_name': c['course_name'],
                    'provider': c['provider']
                })
        else:
            print(f"DEBUG: skills id not found for missing_skill: {missing_skill}") 

    return recommended_courses_list,missing_skill_names

def store_recommendations_in_s3(recommended_courses, bucket_name, object_key):
    try:
        courses_jsonobject = json.dumps(recommended_courses)
       
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=courses_jsonobject)

        return True
    
    except Exception as e:

        print(f"ERROR: Failed to store recommended courses in S3: {e}")
       
        return False
    
def lambda_handler(event, context):
    
    try:
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]

        object_key = event["Records"][0]["s3"]["object"]["key"]
        
        result = retrieve_and_analyze_skills_from_s3(bucket_name, object_key)
        
        if result:

            missing_skills = result["missing_skills"]

            recommended_courses,missing_skill_names = recommend_courses(missing_skills)
            result["recommended_courses"]=recommended_courses
            result["missing_skill_names"]=missing_skill_names

            file_name = object_key.split('/')[-1]

            final_filename = file_name.replace('.json', '_recommendations.json')

            recommendation_s3_key = f"recommendations/{final_filename}"
            
            if store_recommendations_in_s3(result, 'course-recommendations', recommendation_s3_key):

                return {"statusCode": 200, "body": json.dumps({"analysis_result": result, "recommendation_s3_key": recommendation_s3_key})}
            
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "recommedation file storage to s3 failed"}),
                }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Analyze skills failed"}),
            }

    except Exception as e:
        print(f"ERROR: Lambda handler error: {e}")
       
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}