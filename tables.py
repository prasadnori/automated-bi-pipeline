import pandas as pd

class freq_table:

    def __init__(self,file_path,col):
        self.file_path=file_path
        self.col=col
    def read_csv(self):
        data=pd.read_csv(self.file_path)
        return data

    def table_creation(self):
        data=self.read_csv()
        keys=data[self.col].value_counts().keys()
        values=data[self.col].value_counts().values
        df=pd.DataFrame(zip(keys,values),columns=['Labels','Count'])
        df.to_csv(f'{self.col}_df.csv',index=False)
        return (df)

if __name__=="__main__":
    obj=freq_table('Visadataset.csv','continent')
    obj.table_creation()