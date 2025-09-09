from utils import Utils
from github import Github

class Git:
    def __init__(self) -> None:
        self.token = "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"
        self.repository = "alireza-py/result_data_connection"
        self.path = 'crypto_currencys.txt'
        self.object = Github(self.token)
        self.tool = Utils()
        
    def send_result(self, content:str):
        if not self.tool.check_internet_connection():
            return
        repo = self.object.get_repo(self.repository)
        file = repo.get_contents(self.path)
        repo.update_file(self.path, "Update file", content, file.sha)
        print('- Github updated -')