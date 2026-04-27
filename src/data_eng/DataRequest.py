import requests
import pandas as pd
import os
import yfinance as yf


""""codes = ['1389', '1393', '1395', '4390', '11752', '433']"""

class Requests():
    def __init__(self, codes:list):
        self.codes = codes
        
    def get_data(self, start:str, end:str):
            self.response_list = []
            for code in self.codes:
                url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={start}&dataFinal={end}"
                self.response = requests.get(url)
                if self.response.status_code==200:
                    print(f'fazendo requisiçao - cod {code}')
                    print(f'inicio: {start} | fim: {end}')

                    print(f'{code} - requisiçao bem sucedida')
                    data = pd.DataFrame(self.response.json())
                    data['data'] = pd.to_datetime(data['data'], dayfirst=True)
                    data = data.sort_values(by='data')
                    data['valor'] = data['valor'].apply(pd.to_numeric, errors='coerce')
                    data = data.set_index('data')
                    #data.columns = code
                    
                    print(f'Exportando dados para parquet - {code}')
                    print()
                    raw_path = os.path.join('..','data', 'raw', f'dados_historicos_{code}.parquet')
                    #data.to_parquet(raw_path, engine='fastparquet')
                    #data['data'] = pd.to_datetime(data['data'])           
                    self.response_list.append(data)    
                    
        
    def get_dataframe(self)->pd.DataFrame:
        self.df_sgs = pd.concat(self.response_list, axis=1, ignore_index=True)
        self.df_sgs.columns = self.codes
        
        self.df_sgs = self.df_sgs.rename(columns={'1389':'Produção de derivados de petróleo',
                                '1393':'Consumo de derivados de petróleo - gasolina',
                                '1395':'Consumo de derivados de petróleo - Óleo combustível',
                                '4390':'Selic',
                                '11752':'Cambio - IPCA', 
                                '433':'IPCA', 
                                '21859':'Producao Industrial',
                                '22707':'Balança comercial',
                                '24364':'IBC-Br'
                                })
        return self.df_sgs
    
    def y_finance_req(self, ticker:list, start:str, end:str):
        self.finance_list = []
        for ticker_code in ticker:
            print(f'inicio: {start} | final: {end}')
            df_yfinance = yf.download(ticker_code, start=start, end=end, interval='1mo')[['Close', 'Volume']]
            df_yfinance = df_yfinance.reset_index()
            df_yfinance = df_yfinance.rename(columns={'Date':'data'})
            df_yfinance['data'] = pd.to_datetime(df_yfinance['data'], dayfirst=True)
            print('Requisiçao bem sucedida')
            self.finance_list.append(df_yfinance)
            
        df_yfinance_ = pd.concat(self.finance_list, ignore_index=True)
        
        if isinstance(df_yfinance_.columns, pd.MultiIndex):
                df_yfinance_.columns = df_yfinance_.columns.droplevel(1)
                df_yfinance_ = df_yfinance_.rename(columns={'Close':'Close_PETR4.SA', 'Volume':'Volume_PETR4.SA'})
        df_sgs_ = self.df_sgs.reset_index()
        if 'index' in df_sgs_.columns:
            df_sgs_ = df_sgs_.rename(columns={'index':'data'})
            
            
        print(df_sgs_)
        print('=======')
        print(df_yfinance_)
        return pd.merge(df_sgs_, df_yfinance_, on='data', how='left').set_index('data')

    def get_ibov(self, ticker, start, end):
        brent = yf.download(tickers=ticker, start=start, end=end, interval='1mo')[['Close', 'Volume']]
        brent.columns = brent.columns.droplevel(1)
        brent = brent.reset_index()
        brent = brent.rename(columns={'Date':'data', 
                                    'Close':'Close_IBOV', 
                                    'Volume':'Volume_IBOV'})
        
        brent['data'] = pd.to_datetime(brent['data'], dayfirst=True)
        brent = brent.set_index('data')
        return brent 