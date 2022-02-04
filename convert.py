import pandas


def to_csv(dataframe: pandas.DataFrame, filename: str) -> None:
    with open(filename, "w") as file:
        df = dataframe

        header = list(df.iloc[[0]])
        file.write(f"{','.join(header)}\n")

        for i in range(df.shape[0]):
            row = []

            for j in range(df.shape[1]):
                row.append(df.iat[i, j])

            row = [str(i) for i in row]# if i != None else ]

            file.write(f"{','.join(row)}\n")


def to_df(filename: str, use_cols=None) -> pandas.DataFrame:
    if use_cols == None:
        use_cols = []

    # without the encoding, python includes a "Byte Encoding Mark" on the first line
    with open(filename, "r", encoding="utf-8-sig") as file:
        lines = [line[:-1].split(",") for line in file.readlines()]
        header = lines[0]

        # I'm reading values as plain text now, so I have to remove the ""
        # for every value in each nested list...
        # data = []
        # for i in lines[1:]:
        #     row = []
        #     for j in i:
        #         j = j[1:-1] if j[0] == '"' else j
        #         row.append(j)
        #     data.append(row)

        data = [[j[1:-1] if j[0] == '"' else j for j in i] for i in lines[1:]]

        df = pandas.DataFrame(data, columns=header)

        if use_cols:
            df = df.iloc[:, use_cols]

        return df


if __name__ == "__main__":
    print(to_df("data/apartment_data.csv"))
    # to_csv(pandas.DataFrame(
    #     [["row", "row", "bing"],["test1", "test2", "test3"]], columns=["clm1", "c2", "c3"]), "test.csv")
    #
