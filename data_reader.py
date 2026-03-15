import pandas as pd

class DataRead:

    def __init__(self,file_path):
        self.file_path=file_path

    def read_csv(self):
        data=pd.read_csv(self.file_path)
        return data


if __name__ == "__main__":

    read = DataRead("Visadataset.csv")

    data = read.read_csv()

    print(data.head())