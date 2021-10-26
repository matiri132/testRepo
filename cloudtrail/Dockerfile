FROM amazon/aws-lambda-python:3.7

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN  /var/lang/bin/python3.7 -m pip install --upgrade pip
RUN  pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]
