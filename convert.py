import pandas
# from classes_and_stuff import headers


def headers(filename):
    header = []
    if filename == "data/reservations.csv":
        header = [
            "Sifra rezervacije", "Sifra apartmana", "Pocetak", "Broj nocenja",
            "Kraj", "Ukupna cena", "Gost/Kontakt osoba", "Status", "Gost1",
            "Gost2", "Gost3", "Gost4", "Gost5", "Gost6", "Gost7", "Gost8", "Grad"
        ]
    if filename == "data/apartment_data.csv":
        header = [
            "Sifra", "Tip", "Broj soba", "Broj gostiju", "Lokacija", "Adresa",
            "Domacin", "Cena po noci (eur)", "Status", "Ameniti"
        ]

    if filename == "data/amenities.csv":
        header = [
            "Sifra apartmana", "Dodatak 1", "Dodatak 2",
            "Dodatak 3", "Dodatak 4", "Dodatak 5"
        ]

    if filename == "data/user_data.csv":
        header = [
            "Korisnicko ime", "Ime", "Prezime",
            "Kontakt telefon", "Email adresa", "Pol", "Uloga"
        ]

    return header


def to_csv(dataframe: pandas.DataFrame, filename: str) -> None:
    with open(filename, "w") as file:
        df = dataframe

        # header = list(df.iloc[[0]])
        header = headers(filename)
        file.write(f"{','.join(header)}\n")

        for i in range(df.shape[0]):
            row = []

            for j in range(df.shape[1]):
                row.append(df.iat[i, j])

            row = [str(i) for i in row]# if i != None else ]

            file.write(f"{','.join(row)}\n")


def to_df(filename: str, use_cols=None) -> pandas.DataFrame:
    if use_cols is None:
        use_cols = []

    # without the encoding, python includes a "Byte Encoding Mark" on the first line
    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            lines = [line[:-1].split(",") for line in file.readlines()]

            try:
                header = lines[0]
            except IndexError:
                header = headers(filename)
                with open(filename, "w") as f:
                    f.write(",".join(header))

            # I'm reading values as plain text now, so I have to remove the ""
            # for every value in each nested list...

            # readable version of the listcomp below
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

    except FileNotFoundError:
        header = headers(filename)
        with open(filename, "w") as f:
            f.write(",".join(header))


if __name__ == "__main__":
    print(to_df("data/apartment_data.csv"))
    # to_csv(pandas.DataFrame(
    #     [["row", "row", "bing"],["test1", "test2", "test3"]], columns=["clm1", "c2", "c3"]), "test.csv")
    #
