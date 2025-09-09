
from cryptocurrency import CryptoCurrency, Token
from connections import Git
from utils import Utils

class PricePredictionApp:
    def __init__(self):
        self.git = Git()
        self.tool = Utils()
        self.crypto = CryptoCurrency()

    def run(self):
        for name, data in self.crypto.token_history.items():
            Token.name = name[0]
            Token.interval = name[1]
            if Token.interval != 'd':
                continue
            self.crypto.set_ai_configs(Token.interval)
            try:
                result = self.crypto.price_prediction_tensorflow(data)
                text = self.crypto.update_result(name, result, data)
            except Exception as e:
                print(f'File error: {e}')
                continue

            count = 0
            while True:
                count += 1
                if not self.tool.check_internet_connection():
                    print('Network ...')
                    if count >= 1000:
                        break
                    continue
                try:
                    self.git.send_result(text)
                except Exception as e:
                    print(f'Github connection error: {e}')
                break

if __name__ == '__main__':
    app = PricePredictionApp()
    app.run()
