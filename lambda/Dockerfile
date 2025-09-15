FROM public.ecr.aws/lambda/python:3.12

# Install tesseract and dependencies
RUN yum update -y && \
    yum install -y tesseract tesseract-langpack-eng poppler-utils && \
    yum clean all

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "app.lambda_handler" ]