import os
import time
import pandas as pd
import json
import logging
import backoff
from openai import AzureOpenAI, RateLimitError
from dotenv import load_dotenv
from utils import total_cost_calc

load_dotenv() # Loading required environment variables.

SYSTEM_PROMPT = "You are an AI language model tasked with analyzing academic papers."
INPUT_FILE = r'input_files/input_data.xlsx'
# Initialize OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  
    api_version="2024-02-01",
    azure_endpoint=os.getenv("OPENAI_API_BASE_URL")
)

# Exponential backoff mechanism   
@backoff.on_exception(backoff.expo, RateLimitError)
def analyze_review(client, review):
    
    prompt = f"""
Task: Provide a concise summary, describe the research methodology, list key research questions, and suggest future research directions.

Input: {review}

Output: JSON format with the following keys:
- concise_summary
- research_methodology
- key_research_questions
- future_research_directions

Example output:
{{
    "concise_summary": "brief summary",
    "research_methodology": "methodology description",
    "key_research_questions": ["question1", "question2"],
    "future_research_directions": ["direction1", "direction2"]
}}
    """

    try:
        # API call with backoff        
        response = client.chat.completions.create(
            model=os.getenv("DEPLOYMENT_NAME"), 
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}]
        )
                  
        # Parse JSON response
        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
      
        message_content = response.choices[0].message.content.strip()
        result = json.loads(message_content)
        logging.debug(f"Parsed result: {result}")        
        
        return  prompt_tokens, completion_tokens, result

    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return None

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

    logging.error("Max retries exceeded. Returning None.")
    return None

# Process reviews
def process_reviews(client, input_file):
    
    df = pd.read_excel(input_file)
    successful_responses = []
    failed_responses = []
    total_prompt_tokens = 0
    total_completion_tokens = 0

    for index, row in df.iterrows():
        paper_id = row['paper_id']
        review = f"Title: {row['title']}\nAbstract: {row['abstract']}\nPublication Year: {row['publication_year']}"

        try:
            prompt_tokens, completion_tokens, analysis = analyze_review(client, review)
            
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            if analysis:
                analysis['paper_id'] = paper_id
                successful_responses.append(analysis)
            else:
                failed_responses.append({'paper_id': paper_id, 'error': 'Invalid response format'})
        except Exception as e:
            logging.error(f"Failed to analyze review for paper ID {paper_id}: {e}")
            failed_responses.append({'paper_id': paper_id, 'error': str(e)})

    return total_prompt_tokens, total_completion_tokens, successful_responses, failed_responses

# Save results
def save_results(successful_responses, failed_responses):
    success_df = pd.DataFrame(successful_responses)
    failed_df = pd.DataFrame(failed_responses)
    success_df.to_excel('successful_responses.xlsx', index=False)
    success_df.to_json('successful_responses.json', orient='records', indent=4)
    failed_df.to_excel('failed_responses.xlsx', index=False)
