# import oops
# from oops import math_fun
# print(dir(math_fun))

from oops4 import DataRead
from tables import freq_table
import os
from dotenv import load_dotenv
load_dotenv()
from charts import images,pie
#file_path='Visadataset.csv'
file_path=os.getenv('FILE_PATH')
col=os.getenv('COLUMN_NAME')
df=freq_table(file_path,col).table_creation()
data=DataRead(file_path).read_csv()
images(df).bar_chart()
pie(data,col).pie_chart()