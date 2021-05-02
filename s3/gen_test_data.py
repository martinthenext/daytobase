"""

Data corpus from http://www.nltk.org/nltk_data/ - Evaluation data from WMT15

"""
import re
from random import randint
import csv
from datetime import datetime


INPUT_FILENAME = "newstest2015-enru-src.en.sgm"
OUTPUT_FILENAME = "daytobase.test.s3.csv"
YEAR = 2020
LONG_TIME_FORMAT = '%Y.%m.%d %H:%M:%S'


def main():
    documents = []
    timestamps = []

    with open(INPUT_FILENAME, "r") as corpus_file:
        for line in corpus_file:
            if line.startswith("<seg"):
                document = re.search(">(.*)<", line).group(1)
                documents.append(document)

                timestamp = datetime(YEAR, randint(1, 12), randint(1, 28),
                        hour=randint(0, 11), minute=randint(0, 59))
                timestamps.append(timestamp)
    
    with open(OUTPUT_FILENAME, "w+") as output_file:
        writer = csv.writer(output_file)
        for document, timestamp in zip(documents, timestamps):
            timestamp_str = timestamp.strftime(LONG_TIME_FORMAT)
            writer.writerow((timestamp_str, document))


if __name__ == "__main__":
    main()

