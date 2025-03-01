# Resume Parser & Generator App (Gen AI + Flask)

### Objective

The Resume Parser & Generator App, powered by Flask and Generative AI, transforms job seekers’ resumes into ATS-compliant versions. Users upload their resumes in PDF format, and the app analyzes the content—extracting details like full name, email, GitHub portfolio, LinkedIn profile, employment history, technical skills, and soft skills. Leveraging Gen AI, it then generates a new, optimized resume tailored for Applicant Tracking Systems (ATS), offering a choice between two professional templates. The extracted data is also provided in JSON format for user review.

Built with Python, Flask, and tools like Pyresparser, pdfminer.six, and NLP libraries (nltk, spaCy), alongside a Generative AI model, this app automates resume parsing and enhancement. It meets the demand for technology-driven recruitment solutions, helping job seekers boost their resumes’ ATS compatibility and aiding recruiters in processing applications efficiently.

The app's functionality aligns with the growing need for streamlined recruitment processes and the increasing reliance on technology to evaluate and process job applications. By providing users with a detailed analysis of their resumes, the app empowers job seekers to optimize their resumes for better visibility and compatibility with ATS.

### Sneak Peak of the App
![image]()

#### Overview: 
This app analyzes your PDF resume and generates an ATS-optimized version using Gen AI. Choose from two polished templates to ensure your resume stands out in modern hiring systems.


#### Features: 
Parses resume data (e.g., contact info, skills, experience).  

Uses Generative AI to create ATS-compliant resumes.  

Offers two customizable output templates.  

Provides extracted data in JSON format for transparency.



#### Installation: 
Run the pip install requirements.txt to install and set up the app, including any dependencies and prerequisites.

#### Usage: 
Upload your PDF resume, let the app analyze it, and download your new ATS-ready resume in your preferred template. :)


##### Running the program

1. Clone the repository to your local machine
2. Navigate to the project directory
3. Install all the required libraries (just run pip install -r /path/to/requirements.txt)
4. Provide your Open AI API key in the .env file
5. Run the following command to start the chatbot -

    ```
    python app.py
    ```

    ```
    Go to: https://localhost:8000
    ```
    
Overall, the development of a resume parser app using Flask represents a significant advancement in leveraging technology to support job seekers in optimizing their resumes for the modern recruitment landscape. This app aligns with the increasing demand for efficient and technology-driven solutions in the job application process, ultimately benefiting both job seekers and recruiters.
