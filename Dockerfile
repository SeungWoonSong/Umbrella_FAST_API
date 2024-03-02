FROM python:3.10-alpine3.18

RUN apk update && apk add dumb-init

WORKDIR /usr/app

# copy necessary files
COPY ./sql_app ./sql_app
COPY ./requirements.txt ./requirements.txt
COPY ./entrypoint.sh ./entrypoint.sh

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# expose port 3000, it is only for documentation, see entrypoint.sh
EXPOSE 3000

# Start dumb-init for PID 1
ENTRYPOINT [ "/usr/bin/dumb-init", "--" ]

# Start FastAPI server
CMD [ "/bin/sh", "./entrypoint.sh" ]
