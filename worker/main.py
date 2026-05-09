# Closed Source License - kloud Cloud
# Copyright (c) kloud. All rights reserved.

import time
import logging

logging.basicConfig(filename='worker.log', level=logging.INFO)

def run_worker():
    logging.info('Worker started')
    while True:
        logging.info('Worker heartbeat')
        time.sleep(10)

if __name__ == "__main__":
    run_worker()


