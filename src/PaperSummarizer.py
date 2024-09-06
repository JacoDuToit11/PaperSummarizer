import os
import requests
import PyPDF2
import openai
from urllib.parse import urlparse

def download_paper(url, data_folder='../data/PDFs'):
    # Create data folder if it doesn't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Download the PDF
    response = requests.get(url)
    if response.status_code == 200:
        # Extract filename from URL
        filename = os.path.basename(urlparse(url).path)
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        filepath = os.path.join(data_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath
    else:
        raise Exception(f"Failed to download the paper. Status code: {response.status_code}")

def extract_text_from_pdf(filepath):
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def summarize_text(text):
    openai.api_key = os.getenv("JACO_OPENAI_API_KEY")
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes academic papers."},
            {"role": "user", "content": f"Please summarize the following academic paper:\n\n{text}"}
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content
    
def save_summary(summary, filename):
    summaries_folder = os.path.join('../data', 'Summaries')
    os.makedirs(summaries_folder, exist_ok=True)
    
    filepath = os.path.join(summaries_folder, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(summary)
    return filepath

def summarize_paper(url):
    try:
        # Download the paper
        filepath = download_paper(url)
        print(f"Paper downloaded to: {filepath}")

        # Extract text from the PDF
        text = extract_text_from_pdf(filepath)

        # Summarize the text
        summary = summarize_text(text)

        # Save the summary
        filename = os.path.basename(urlparse(url).path)
        if not filename.endswith('.txt'):
            filename = filename.rsplit('.', 1)[0] + '.txt'
        summary_path = save_summary(summary, filename)
        print(f"Summary saved to: {summary_path}")

        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    paper_url = "https://arxiv.org/pdf/1706.03762"
    summary = summarize_paper(paper_url)
    print("Summary:")
    print(summary)
