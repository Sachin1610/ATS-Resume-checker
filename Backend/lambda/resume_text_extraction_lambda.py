import boto3
import re
import json
import traceback
import requests
import os

def extract_resume_text(bucket_name, object_name):
    
    s3client = boto3.client('s3')
    try:
        metadata_response = s3client.head_object(Bucket=bucket_name, Key=object_name)
        title = metadata_response['Metadata']['title']
        
    except Exception as e:
        print(f"ERROR: Failed to retrieve object metadata. Error: {e}")
    try:
        textract = boto3.client('textract')

        # Extracting entire text from resume
        full_text_response = textract.analyze_document(
            Document={'S3Object': {'Bucket': bucket_name, 'Name': object_name}},
            FeatureTypes=['TABLES', 'FORMS']
        )
        full_text_data = [data["Text"] for data in full_text_response.get("Blocks", []) if data["BlockType"] == "LINE"]
        full_text = ' '.join(full_text_data)

        # Extract skills section from resume
        technical_skills_response = textract.analyze_document(
            Document={'S3Object': {'Bucket': bucket_name, 'Name': object_name}},
            FeatureTypes=['LAYOUT']
        )

        blocks = technical_skills_response['Blocks']
        technical_skills_text = ""
        current_section = None
        next_section_header_regex = re.compile(r'\b(?:experience|projects|education|relevant coursework|certifications|achievements)\b', re.IGNORECASE)
        skills_section_header_regex = re.compile(r'\b(?:technical skills|key skills|proficiencies)\b', re.IGNORECASE)
        
        for block in blocks:

            if block['BlockType'] == 'LINE' and 'Text' in block:

                text = block['Text']
                print(current_section)
                if current_section == 'SKILLS':

                    if next_section_header_regex.search(text) or ('\n\n' in text):

                        break 
                    else:
                        technical_skills_text += text + "\n"  

                elif skills_section_header_regex.search(text):

                    current_section = 'SKILLS'

            elif current_section == 'SKILLS' and block['BlockType'] == 'LAYOUT_TEXT' and 'Text' in block:
                technical_skills_text += block['Text'] + "\n"

        if current_section == 'SKILLS':

            return full_text, technical_skills_text.strip(), title
        else:
            return full_text, None, title

    except Exception as e:
        traceback.print_exc()
        return None, None, title

def section_data_formatter(entire_text, skills_content, title):
    skills = []
    if skills_content:
        for skill in skills_content.split('\n'):
            stripped_skill = skill.strip()
            if stripped_skill:
                skills.append(stripped_skill)

    formated_data = {
        "entire_text": entire_text,
        "skills_content": skills,
        "title": title
    }
    return formated_data

def invoke_api(job_title):
    api_url = 'http://3.141.29.233:5000/extracts_job_skills' 
    headers = {'Content-Type': 'application/json'}
    params = {'job_title': job_title}

    try:
        response = requests.get(api_url, headers=headers, params=params) 
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        
        print(f"ERROR: Failed to invoke API: {e}")
        
        return None

def lambda_handler(event, context):


    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']

        object_name = event['Records'][0]['s3']['object']['key']
        
        job_title = 'Software Engineer' #Default

        full_text, skills, title = extract_resume_text(bucket_name, object_name)

        if full_text is not None:

            formatted_data = section_data_formatter(full_text, skills, title)

            job_skills_api_response = invoke_api(title)

            if job_skills_api_response:

                formatted_data['api_response'] = job_skills_api_response

                json_response = json.dumps(formatted_data)
                
                output_key = object_name.replace(".pdf", ".json")

                s3client = boto3.client('s3')
                s3client.put_object(Body=json_response, Bucket="extracted-skills-out", Key=output_key)

                return {
                    'statusCode': 200,
                                   }
            else:
               
                return {
                    'statusCode': 500,
                    'body': json.dumps('API Call failed')
                }

        else:
            return {
                'statusCode': 500,
                'body': json.dumps('extraction failed')
            }

    except Exception as e:
        print(f"ERROR: Error in lambda_handler: {e}")

        return {
            
            'statusCode': 500,
            'body': json.dumps(f'Error: {e}')
        }