FROM python:3.12.0-alpine3.18

WORKDIR /usr/app

# install 
RUN pip install --upgrade pip && apk update && apk upgrade && apk add --no-cache gcc libc-dev libffi-dev

# copy necessary files
COPY requirements.txt ./requirements.txt
COPY ./sql_app ./sql_app
COPY ./start.sh ./start.sh

# expose port 3000, it is only for documentation, see start.sh
EXPOSE 3000

# grant permission to execute the script
RUN chmod +x ./start.sh

ENTRYPOINT ["/bin/sh", "./start.sh" ]
