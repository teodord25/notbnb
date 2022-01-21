import csv
import pandas as pd


# this is redundant now,
# pandas is fucking awesome
#
# def read():
#     with open("fake_people.csv", "r") as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         line_count = 0
#         for row in csv_reader:
#             if line_count == 0:
#                 print(f"{'|'.join([w.ljust(12) for w in row])}")
#                 print("-"*100)
#                 line_count += 1
#             else:
#                 print(f"{'|'.join([w.ljust(12) for w in row])}")
#                 line_count += 1
#         print(f"processed {line_count} lines")


def panda():
    joe = pd.read_csv(filepath_or_buffer="fake_people.csv", delimiter=',', usecols=range(7))
    print(joe)

def autoregister()

def write():
    pass


if __name__ == "__main__":
    panda()
