#!bin/bash

export PYTHONPATH=/home/ubuntu/backend:$PYTHONPATH
pytest test/user_test.py
pytest test/borrow_return.py