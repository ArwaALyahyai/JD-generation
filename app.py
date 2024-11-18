from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Ollama URL
OLLAMA_LLM_URL = os.getenv('OLLAMA_LLM_URL', 'http://151.104.135.251:11434/api/generate')

def generate_job_description(title, requirements, experience_level="entry"):
    """
    Generate a job description using Ollama LLM.
    
    Args:
        title (str): Job title
        requirements (str): Required skills and qualifications
        experience_level (str): Required experience level (entry/mid/senior)
    
    Returns:
        str: Generated job description
    """
    prompt = f"""Create a professional job description for a {title} position.
    Experience Level: {experience_level}
    Required Skills and Qualifications: {requirements}
    
    Please structure the job description with the following sections:
    1. About the Role
    2. Key Responsibilities
    3. Required Qualifications
    4. Preferred Qualifications
    5. What We Offer
    
    Make it professional, clear, and engaging."""

    try:
        # Prepare the payload for Ollama
        payload = {
            "model": "llama3.2",  # You can adjust the model as needed
            "prompt": prompt,
            "stream": False
        }

        # Make request to Ollama endpoint
        response = requests.post(OLLAMA_LLM_URL, json=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('response', '')
        else:
            raise Exception(f"Error from Ollama API: {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to connect to Ollama API: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating job description: {str(e)}")

@app.route('/api/generate-jd', methods=['POST'])
def create_job_description():
    """API endpoint to generate a job description"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'title' not in data or 'requirements' not in data:
            return jsonify({
                'error': 'Missing required fields. Please provide title and requirements.'
            }), 400
        
        # Extract data
        title = data['title']
        requirements = data['requirements']
        experience_level = data.get('experience_level', 'entry')  # Optional field
        
        # Generate job description
        job_description = generate_job_description(
            title=title,
            
            requirements=requirements,
            experience_level=experience_level
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'job_description': job_description
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)