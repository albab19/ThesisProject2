
FROM python:3.9-slim

# Set the working directory in the container


# Copy the current directory contents into the container at /app
COPY . ./app
WORKDIR .

# Install any needed packages specified in requirements.txt
RUN apt-storage update &&  pip install --upgrade pip && pip install -r app/requirements.txt



#RUN pip install pydicom==2.4.4, pip install pynetdicom==2.0.2, pip install numpy==1.23.5

# Expose the DICOM
EXPOSE 11112

# Run the app
CMD ["python", "app/dicomhawk.py"]
