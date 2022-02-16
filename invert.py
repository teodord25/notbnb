import classes_and_stuff as cs
import datetime
import convert
import pandas as pd


def add(s, lst):
    s = [i.strip() for i in s.strip().split(",")]
    date = str(datetime.date.today())
    if cs.compare(date, ">", s[0]) or cs.compare(s[0], ">", s[1]):
        raise cs.InvalidDateError

    try:
        tf = cs.TimeFrame(s[0], end=s[1])

    except cs.InvalidDateError:
        return

    lst.append(tf)
    return lst


def finish(apt_id, lst):
    pairs = cs.free_time(0, tf_lst=lst)

    df = convert.to_df("data/reservations.csv")

    res_id = df.iat[-1, 0]

    base = [res_id, apt_id, "p", "brn", "k", "c", "g", "Prihvacena", "g1",
            "g2", "g3", "g4", "g5", "g6", "g7", "g8", "gr"]

    # 0 1 2 4

    rows = []
    i = 1
    for pair in pairs:
        row = base[:]

        row[0] = str(int(row[0]) + i)
        i += 1
        row[2] = pair[0]
        row[4] = pair[1]

        rows.append(row)

    dfp = pd.DataFrame(rows, columns=convert.headers("data/reservations.csv"))
    df = pd.concat([df, dfp], ignore_index=True)
    # df = df.append(dfp, ignore_index=True)
    # print(df)

    convert.to_csv(df, "data/reservations.csv")

