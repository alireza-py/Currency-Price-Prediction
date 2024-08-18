import re
import os
import csv
import time
import numpy
import pandas
import random
import pathlib
import requests
from utils import Token, Utils
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, GRU, Dense, Dropout, Input
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.statespace.sarimax import SARIMAX
from dataclasses import dataclass
import tensorflow

@dataclass
class AiConfiguration:
    units = 500
    epochs = 50
    timesteps = 5
    batch_size = 32
    pricestate = ['High', 'Low']
    model_file = 'lstm_model.keras'

class CryptoCurrency:
    def __init__(self) -> None:
        print('------------------------\n')
        self.tools = Utils()
        self.token_history = {}
        config_file_loc = pathlib.Path() / 'TOKENCONFIGS.csv'
        result_file = pathlib.Path() / 'result.csv'

        if not result_file.exists():
            open(result_file, "wb")

        if not config_file_loc.exists():
            open(config_file_loc, "wb")
        
        if not os.path.getsize(config_file_loc) == 0:    
            config_file = pandas.read_csv(config_file_loc, header=None, delimiter=' ')        
            for data in config_file.values:
                Token.name = data[0]
                for interval in data[1:]:
                    match interval:
                        case Token.interval_daily:
                            Token.interval = "d"
                        case Token.interval_weekly:
                            Token.interval = "w"
                        case Token.interval_monthly:
                            Token.interval = "m"
                        case Token.interval_yearly:
                            Token.interval = "y"
                    self.tools.file_maker(f"{Token.name}_{Token.interval}")
        
        count = 0
        while True:
            if self.tools.check_internet_connection():
                status = self.tools.update()
                if status == -1:
                    continue
                break
            print("# Trying again for updating #")
            if count >= 10:
                break
            count += 1
            time.sleep(.5)

        for file in self.tools.list_file():
            result = (re.findall(r"\\(.+).csv", str(file)))[0]
            Token.name = result[:-2]
            Token.interval = result[-1]
            df = pandas.read_csv(file)
            df = self.remove_outliers_isolation_forest(
                df, 
                features_column= AiConfiguration.pricestate,
                contamination= 0.03
            )
            self.token_history[(Token.name, Token.interval)] = df
        print('\n------------------------')

        # config = tensorflow.compat.v1.ConfigProto()
        # config.gpu_options.allow_growth = True
        # tensorflow.compat.v1.Session(config=config)

    def price_prediction_tensorflow(self, data) -> dict:
        result = {}
        self.set_seed(42)
        for state in AiConfiguration.pricestate:
            tensorflow.compat.v1.reset_default_graph()
            tensorflow.keras.backend.clear_session()
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data[state].values.reshape(-1, 1))

            train_X, train_Y = self.create_dataset(scaled_data, AiConfiguration.timesteps)
            ''''''
            model = Sequential()
            model.add(Input(shape= (AiConfiguration.timesteps, 1)))
            model.add(Bidirectional(LSTM(units= AiConfiguration.units, return_sequences=True)))
            model.add(Dropout(0.2))
            model.add(Bidirectional(LSTM(units= AiConfiguration.units, return_sequences=True)))
            model.add(Dropout(0.2))
            model.add(Bidirectional(LSTM(units= AiConfiguration.units)))
            model.add(Dropout(0.2))
            model.add(Dense(units=1))
            ''''''
            model.compile(loss='mean_squared_error', optimizer='adam')
            early_stopping = tensorflow.keras.callbacks.EarlyStopping(
                monitor='loss', 
                patience=30, 
                restore_best_weights=True
            )
            
            model.fit(train_X, train_Y, epochs= AiConfiguration.epochs, 
                                batch_size= AiConfiguration.batch_size,
                                callbacks= [early_stopping],
                                verbose= 1 
                                )

            last_sequence = scaled_data[-AiConfiguration.timesteps:].reshape(1, AiConfiguration.timesteps, 1)
            next_price = model.predict(last_sequence)
            next_price = scaler.inverse_transform(next_price)

            last_timestamp = data['Date'].values[-1]
            
            match Token.interval:
                case 'd':
                    sum_ = pandas.DateOffset(days=1)
                case 'w':
                    sum_ = pandas.DateOffset(weeks=1)
                case 'm':
                    sum_ = pandas.DateOffset(months=1)
                case 'y':
                    sum_ = pandas.DateOffset(years=1)
            next_timestamp = pandas.to_datetime(last_timestamp) + sum_
            result[state] = (next_timestamp, next_price)
        return result
    
    def set_seed(self, seed_value=42):
        numpy.random.seed(seed_value)
        tensorflow.random.set_seed(seed_value)
        random.seed(seed_value)

    def create_dataset(self, dataset, timesteps):
        dataX, dataY = [], []
        for i in range(len(dataset) - timesteps - 1):
            a = dataset[i:(i + timesteps), 0]
            dataX.append(a)
            dataY.append(dataset[i + timesteps, 0])
        return numpy.array(dataX), numpy.array(dataY)

    def save_model(self, model, file_path):
        model.save(file_path)

    def load_model(self, file_path):
        return tensorflow.keras.models.load_model(file_path)

    def update_result(self, crypto, outdata, indata_today):
        text = []
        edit = []
        name = str(crypto[0]).upper()
        interval = {
            'today' : ('0000-00-00', (0,0)),
            'tomorrow' : ('0000-00-00', (0,0)),
            'week' : ('0000-00-00', (0,0)),
            'moth' : ('0000-00-00', (0,0)),
            'year' : ('0000-00-00', (0,0))
            }
              
        linecounter = 0
        with open('result.csv', 'r') as file:
            for line in csv.reader(file):
                text.append(line)
        for num in range(len(text)-1, 0, -1):
            if not text[num] == [' ']:
                text.append([' '])
                text.append([' '])
                break
            text.pop(num)
        for line in text:
            linecounter += 1
            if line == []:
                continue
            find = re.findall(name, line[0])
            if not find == []:
                find = find[0]
                break
        linecounter = linecounter - 1
        for out in text[linecounter+2:linecounter+7]:
            first = re.findall(r'(.*)?: ', out[0])
            date = re.findall(r'(\d{4}-\d{2}-\d{2})', out[0])
            price = re.findall(r'\[(.*)\|(.*)\]', out[0])
            if first != [] and date != [] and price != []:
                price = (float(str(price[0][0]).strip()), float(str(price[0][1]).strip()))
                interval[str(first[0]).lower()] = (date[0], price)
        
        
        out = (str(outdata['High'][0])[:-9], (float(outdata['Low'][1]), float(outdata['High'][1])))
        match crypto[1]:
            case 'd':
                last_timestamp = str(indata_today['Date'].values[-1])
                low = float(indata_today['Low'].values[-1])
                high = float(indata_today['High'].values[-1])
                interval['today'] = (last_timestamp, (low, high))
                interval['tomorrow'] = out
            case 'w':
                interval['week'] = out
            case 'm':
                interval['moth'] = out
            case 'y':
                interval['year'] = out

        editcontent = [
            [name.center(62, '-')],
            ["                                  low                     high"],
            [f"Today:       {interval['today'][0]}       -[{interval['today'][1][0]} | {interval['today'][1][1]}]+"],
            [f"Tomorrow:     {interval['tomorrow'][0]}       -[{interval['tomorrow'][1][0]} | {interval['tomorrow'][1][1]}]+"],
            [f"Week:        {interval['week'][0]}       -[{interval['week'][1][0]} | {interval['week'][1][1]}]+"],
            [f"Moth:        {interval['moth'][0]}       -[{interval['moth'][1][0]} | {interval['moth'][1][1]}]+"],
            [f"Year:        {interval['year'][0]}       -[{interval['year'][1][0]} | {interval['year'][1][1]}]+"],
            ]
        spl1 = text[:linecounter]
        spl2 = text[linecounter+7:]
        spl1.extend(editcontent)
        spl1.extend(spl2)
        with open('result.csv', 'w', newline='') as file:
            write = csv.writer(file)
            for i in spl1:
                write.writerow(i)
        result = ''
        for out in spl1:
            if out == []:
                out = ['']
            result = result + '\n' + out[0]
        return result          
    
    def set_ai_configs(self, interval):
        match interval:
            case 'd':
                AiConfiguration.units = 50
                AiConfiguration.epochs = 500
                AiConfiguration.timesteps = 1
                AiConfiguration.batch_size = 32
            case 'w':
                AiConfiguration.units = 500
                AiConfiguration.epochs = 20
                AiConfiguration.timesteps = 1
                AiConfiguration.batch_size = 32
            case 'm':
                AiConfiguration.units = 500
                AiConfiguration.epochs = 20
                AiConfiguration.timesteps = 1
                AiConfiguration.batch_size = 32
            case 'y':
                AiConfiguration.units = 500
                AiConfiguration.epochs = 20
                AiConfiguration.timesteps = 1
                AiConfiguration.batch_size = 32
            
    def remove_outliers(self, df, column):
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    
    def remove_outliers_isolation_forest(self, df, features_column, contamination=0.01):
        iso_forest = IsolationForest(contamination=contamination)
        outliers = iso_forest.fit_predict(df[features_column])
        print(outliers)
        df['Outlier'] = outliers
        df = df[df['Outlier'] == 1]
        df = df.drop(columns=['Outlier'])
        return df