#!/bin/bash

# install dependencies
pip install -r requirements.txt

uvicorn sql_app.main:app --reload --host=0.0.0.0 --port=3000