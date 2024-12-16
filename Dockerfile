FROM python:3

RUN mkdir /app
ADD . /app
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# CMD ["/bin/sh", "-c", "python main.py > logs/output.log 2>&1"]
CMD ["/bin/sh", "-c", "nohup python main.py"]
