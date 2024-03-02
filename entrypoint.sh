#!/bin/sh

uvicorn sql_app.main:app --host=0.0.0.0 --port=3000
