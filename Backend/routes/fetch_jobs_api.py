import http.client
import json
import openai


def fetch_jobs(job_title):
    connection = http.client.HTTPSConnection("jsearch.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "",
        'x-rapidapi-host': "jsearch.p.rapidapi.com"
    }
    query = job_title.replace(" ", "+") + "%5jobs"
    connection.request(
        "GET", 
        f"/search?query={query}&location=US&page=1&num_pages=1&country=us&date_posted=today", 
        headers=headers
    )
    response = connection.getresponse()
    res_data = response.read().decode("utf-8")
    parsed_data = json.loads(res_data)

    if "data" in parsed_data and isinstance(parsed_data["data"], list):

        job_data = [{"description": job.get("job_description", "No Description Found"), "employer": job.get("employer_name", "Unknown Employer")} for job in parsed_data["data"][:3]]
    else:
        job_data = []

    return job_data

def extract_skills(job_data):
    if not job_data:
        return "No job description found in data provided."

    description_text = []
    for i in job_data:
        description_text.append(f"Employer: {i['employer']}\nDescription: {i['description']}")
    finaltext = "\n\n".join(description_text)

    OPENAI_API_KEY = ""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"Extract key technical skills all in lower case from the following job descriptions in comma separated way:\n\n{finaltext}\n\nSkills:"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        jobs_kills = response.choices[0].message.content.strip()
        skills_set = {skill.strip() for skill in jobs_kills.split(",")}
        return skills_set

    except Exception as e:
        return f"Error: {str(e)}"


