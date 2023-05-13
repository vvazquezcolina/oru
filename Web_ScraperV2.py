
import openai
from selenium import webdriver
import time
import gradio as gr
from bs4 import BeautifulSoup
import re

# Set up OpenAI API key
openai.api_key = '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'

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def extract_data(url, cv_text): 
    # Initialize the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    # Load the URL
    driver.get(url)
    
    # Wait for page load
    time.sleep(5)
    
    # Extract text using Beautiful Soup functions 
    soup = BeautifulSoup(driver.page_source, "html.parser") 
    
    paragraphs = soup.find_all("p")
    
    # Extract text from each paragraph
    text = ' '.join([clean_html(p.get_text()) for p in paragraphs])
    
    driver.quit()
    
    # Send text to GPT-3.5-turbo to extract job requirements
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"I have a job listing here and I need you to extract the main points or responsibilities. Here's the job listing: {text}"},
        ]
    )
    
    job_requirements = response.choices[0].message['content']

    # Send CV text and job requirements to GPT-3.5-turbo for improvement and cover letter generation
    messages_improve_cv = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Here is the original CV:\n\n{cv_text}\n\nBased on the following job points or responsibilities:\n\n{job_requirements}\n\nCan you improve this CV and generate a cover letter without inventing new companies or universities?"},
    ]

    response_improve_cv = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages_improve_cv
    )
    improved_cv_and_cover_letter = response_improve_cv.choices[0].message['content']

    # Print everything done in the terminal, specially the errors.
    print("Extracted job requirements:", job_requirements)
    print("Improved CV and cover letter:", improved_cv_and_cover_letter)

    # Save the result as a file with timestamp
    file_name = f"results_{time.strftime('%Y%m%d-%H%M%S')}.txt"
    
    with open(file_name, "w") as f:
        f.write(improved_cv_and_cover_letter)

    return improved_cv_and_cover_letter

iface = gr.Interface(
    fn=extract_data,
    inputs=["text", "textarea"],
    outputs="text",
    max_execution_time=120,
)

iface.queue().launch(debug=True, share=True, inline=False)