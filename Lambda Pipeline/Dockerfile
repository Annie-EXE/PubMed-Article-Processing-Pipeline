FROM amazon/aws-lambda-python

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY lambda_function.py .

COPY GRID_Data /GRID_Data

COPY world_countries.txt .

CMD [ "lambda_function.lambda_handler" ]