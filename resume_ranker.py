import spacy
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import csv

csv_filename = "ranked_resumes.csv"

# Load spaCy NER model
nlp = spacy.load("en_core_web_sm")

# Sample job description
job_description = "NLP Specialist: Develop and implement NLP algorithms. Proficiency in Python, NLP libraries, and ML frameworks required."

# List of resume PDF file paths
resume_paths = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]  # Add more file paths here

# Extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

# Extract emails and names using spaCy NER
def extract_entities(text):
    # Extract emails using regular expression
    emails = re.findall(r'\S+@\S+', text)
    # Extract names using a simple pattern (assuming "First Last" format)
    names = re.findall(r'^([A-Z][a-z]+)\s+([A-Z][a-z]+)', text)
    if names:
        names = [" ".join(names[0])]
    
    return emails, names


# Extract job description features using TF-IDF
tfidf_vectorizer = TfidfVectorizer()
job_desc_vector = tfidf_vectorizer.fit_transform([job_description])

# Rank resumes based on similarity
ranked_resumes = []
for resume_path in resume_paths:
    resume_text = extract_text_from_pdf(resume_path)
    emails, names = extract_entities(resume_text)
    resume_vector = tfidf_vectorizer.transform([resume_text])
    similarity = cosine_similarity(job_desc_vector, resume_vector)[0][0]
    ranked_resumes.append((names, emails, similarity))

# Sort resumes by similarity score
ranked_resumes.sort(key=lambda x: x[2], reverse=True)

# Display ranked resumes with emails and names
for rank, (names, emails, similarity) in enumerate(ranked_resumes, start=1):
    print(f"Rank {rank}: Names: {names}, Emails: {emails}, Similarity: {similarity:.2f}")

with open(csv_filename, "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Rank", "Name", "Email", "Similarity"])
    
    for rank, (names, emails, similarity) in enumerate(ranked_resumes, start=1):
        name = names[0] if names else "N/A"
        email = emails[0] if emails else "N/A"
        csv_writer.writerow([rank, name, email, similarity])