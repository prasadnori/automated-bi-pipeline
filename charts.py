import pandas as pd
import matplotlib.pyplot as plt
# from tables import freq_table
# file_path='Visadataset.csv'
# col='continent'
class images:
    def __init__(self,df):
        self.df=df
    def bar_chart(self):
        x=self.df['Labels']
        y=self.df['Count']
        plt.bar(x,y)
        plt.savefig('continent.jpg')

class pie:
    def __init__(self,data,col):
        self.data=data
        self.col=col
    def pie_chart(self):
        keys=self.data[self.col].value_counts().keys()
        values=self.data[self.col].value_counts().values
        plt.pie(values,labels=keys,autopct="%0.2f%%")
        plt.savefig('pie.jpg')

if __name__=="__main__":
    obj=images()
    obj.bar_chart()