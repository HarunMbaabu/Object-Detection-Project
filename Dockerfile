#Set base image in Python 
FROM python:3.8 

#Setting Working directory
WORKDIR /app 

#Copy packages file, requirements.txt file from local to docker image
COPY requirements.txt ./requirements.txt 

#Run command
RUN pip3 install -r requirements.txt  
RUN pip3 install -U pip setuptools wheel  

#Expose port 8501 for app to run on 
EXPOSE 8501 

#Command to RUn STREAMLIT Application
CMD ["streamlit", "run", "app.py"]
