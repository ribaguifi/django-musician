FROM python

WORKDIR /home

RUN python3 -m pip install --upgrade pip
RUN pip install wheel

COPY . .
RUN pip install -r requirements.txt
RUN python manage.py migrate

EXPOSE 8080

ENTRYPOINT [ "python", "manage.py", "runserver", "0.0.0.0:8080" ]