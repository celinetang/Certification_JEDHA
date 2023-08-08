FROM python:3.10.10

WORKDIR /home/app


COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app
# the .h5 files for our models are automatically uploaded but not in git as too heavy


CMD gunicorn app:app  --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker