I am new to python and I am having difficulty with this. In order to do this I am using Pycharm. I am trying to make a graph of a stock using yahoo finance information. 
This is my code right now:
import pandas as pd 
from matplotlib import pyplot as plt
TSLA_data=pd.read_csv('TSLA_data.csv')
TSLA_data.index=TSLA_data['Date']
TSLA_data['Open'].plot(label='TSLA_data Open Price')
TSLA_data['Close'].plot(label='TSLA_data Close price')
TSLA_data['High'].plot (label='TSLA_data High price')
TSLA_data['Low'].plot(label='TSLA_data Low price')
plt.legend() 
plt.title ('Tesla Stock Prices") 
plt.ylabel('Stock Price') 
plt.show()