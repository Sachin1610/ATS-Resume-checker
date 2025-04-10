from boto3 import resource
import boto3

#Uploading resume to s3 
def resume_upload(resume,filename,title):
   try:
        s3client = boto3.client(
            's3')
        response=s3client.upload_fileobj(resume,'code-input',filename,ExtraArgs={

        "Metadata": {

            "title": title,
            
        }
    })
        return True
   except Exception as e:
        print(f"Error in file upload to s3: {str(e)}")
        return False