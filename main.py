import time
import csv
from cryptocurrency import CryptoCurrency, AiConfiguration, Token
from connections import Git
from utils import Utils
from os import system

def main():
    git = Git()
    tool = Utils()
    crypto = CryptoCurrency()
    for name, data in crypto.token_history.items():
        Token.name = name[0]
        Token.interval = name[1]
        if not Token.interval == 'd':
            continue
        crypto.set_ai_configs(Token.interval)
        # try:
        result = crypto.price_prediction_tensorflow(data)
        text = crypto.update_result(name, result, data)
        # except:
        #     print('Fileerror ...')

        count = 0
        while True:
            count += 1
            if not tool.check_internet_connection():
                print('Network ...')
                if count >= 1000:
                    break
                continue
            try:
                git.send_result(text)
            except:
                print('Github connection ...')
            break


if __name__ == '__main__':
    main()