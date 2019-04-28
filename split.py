import csv
import sys

train_ts = float(sys.argv[7])
valid_ts = float(sys.argv[8])
ts_f = int(sys.argv[9])

with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    headers = next(reader, None)

    train_stat_f = open(sys.argv[2], 'w')
    train_stat_writer = csv.writer(train_stat_f, delimiter=',')
    train_targ_f = open(sys.argv[3], 'w')
    train_targ_writer = csv.writer(train_targ_f, delimiter=',')

    valid_stat_f = open(sys.argv[4], 'w')
    valid_stat_writer = csv.writer(valid_stat_f, delimiter=',')
    valid_targ_f = open(sys.argv[5], 'w')
    valid_targ_writer = csv.writer(valid_targ_f, delimiter=',')

    test_stat_f = open(sys.argv[6], 'w')
    test_stat_writer = csv.writer(test_stat_f, delimiter=',')

    sortedlist = sorted(reader, key=lambda row: row[ts_f], reverse=False)
    for row in sortedlist:
        ts = float(row[ts_f])
        test_stat_writer.writerow(row)
        if ts < train_ts:
            train_stat_writer.writerow(row)
            valid_stat_writer.writerow(row)
        elif ts < valid_ts:
            valid_stat_writer.writerow(row)
            train_targ_writer.writerow(row)
        else:
            valid_targ_writer.writerow(row)
