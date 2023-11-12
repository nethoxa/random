import os
import re
import requests
import json

from bs4 import BeautifulSoup
from github import Github, Repository, ContentFile
from termcolor import colored
from github import Auth

# -------------------------------------------------
# Header
# -------------------------------------------------
INTRO = colored("""

ooooooooo.         .o.         ooooooooo.      .oooooo..o   ooooo   oooooooooooo       .o.         ooooo        
`888   `Y88.      .888.        `888   `Y88.   d8P'    `Y8   `888'   `888'     `8      .888.        `888'        
 888   .d88'     .8"888.        888   .d88'   Y88bo.         888     888             .8"888.        888         
 888ooo88P'     .8' `888.       888ooo88P'     `"Y8888o.     888     888oooo8       .8' `888.       888         
 888           .88ooo8888.      888`88b.           `"Y88b    888     888    "      .88ooo8888.      888         
 888          .8'     `888.     888  `88b.    oo     .d8P    888     888          .8'     `888.     888       o 
o888o        o88o     o8888o   o888o  o888o   8""88888P'    o888o   o888o        o88o     o8888o   o888ooooood8 
""", "red", attrs=["bold"])

INTRO += """

                                                                                                      
                                              Made by neth

                                        
                                GitHub:    https://github.com/nethoxa
                                Cantina:   https://cantina.xyz/u/neth
                                Twitter:   https://twitter.com/nethoxa
                                Code4rena: https://code4rena.com/@erebus

                                
                
    Parsifal is gonna download ALL data at Immunefi (GitHub repos, deployed contracts, implementations...)
    and apply a registry of pretty complex REGEX patterns to look after some easter eggs that dM-FoR-aUdiTs 
    fuckers do not care/know about. 

    You need to set some environment keys for this thing to work, namely your API keys for the next block
    explorers:

    @todo block explorers

            This thing is heavily inspired by ScrapiFy => https://github.com/pratraut/scrapyFi
"""


# -------------------------------------------------
# Browser headers
# -------------------------------------------------
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}


# -------------------------------------------------
# File extensions
# -------------------------------------------------
FILE_EXTENSIONS = [".sol", ".rs", ".zkevm", ".cairo", ".go"]


# -------------------------------------------------
# Coloring
# -------------------------------------------------
SUCCESS = colored("[+]", "green", attrs=["bold"])
WARNING = colored("[!]", "yellow", attrs=["bold"])
ERROR = colored("[-]", "red", attrs=["bold"])

# -------------------------------------------------
# Some utilities
# -------------------------------------------------
class Utils:

    # Safe list indexing
    def safe_list_get(lst, index, default):
        try:
            return lst[index]
        except IndexError:
            return default
        

# -------------------------------------------------
# Abstract representation of Immunefi projects
# -------------------------------------------------
class Project(object):
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.project = kwargs['project']
        self.date = kwargs['date']
        self.maximum_reward = kwargs['maximum_reward']
        self.technologies = kwargs['technologies']
        self.kyc = kwargs['kyc']
        self.assets_in_scope = kwargs['assets_in_scope']
        self.url = kwargs['url']
        self.num_contracts = kwargs['num_contracts']


# -------------------------------------------------
# Github module
# -------------------------------------------------
class GithubModule:

    # Github urls parser
    def github_parse(self, url: str):

        # Parse the url to see if it is indeed a valid Github url
        regex = r'https://[www.]*github.com(.+)'
        result = re.match(regex, url)
        if not result:
            print(ERROR + f" Error trying to download {url}. Bad format")
            return "", "", "", ""
        
        # Split the url => github.com/{author}/{repository}/tree/{branch}/{remaining_path}
        repo_path = result.group(1)
        split_path = repo_path.split('/')
        author = Utils.safe_list_get(split_path, 1, "")
        repository = Utils.safe_list_get(split_path, 2, "")
        branch = Utils.safe_list_get(split_path, 4, "")

        if not branch:
            branch = "master"
            remaining_path = ""
        
        else:
            remaining_path = repo_path[repo_path.index(branch) + len(branch) + 1::]

        return author, repository, branch, remaining_path


    # Generic download
    def download(self, c: ContentFile, out: str):
        r = requests.get(c.download_url)
        output_path = f'{out}/{c.path}'
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(r.content)

            print(SUCCESS + f" File {output_path} successully downloaded")

        else:
            print(WARNING + f" File {output_path} does exists")

    # Downloads recursively a given folder
    def download_folder(self, repo: Repository, folder: str, out: str):
        contents = repo.get_contents(folder)
        for c in contents:
            if c.download_url is None:
                self.download_folder(repo, c.path, out)
                continue
            self.download(c, out)


    # Downloads a single file
    def download_file(self, repo: Repository, folder: str, out: str):

        c = repo.get_contents(folder)
        self.download(c, out)


    # Github downloader
    def github_download(self, url: str, git: Github):
        
        author, repository, branch, remaining_path = self.github_parse(url)
        if not author and not repository and not branch and not remaining_path:
            return
        
        repo = git.get_repo(author + "/" + repository)

        # I expect three situations:
        #   - It is a file, so *.sol, *.rs and all of that
        #   - It is a sub-folder
        #   - It is the root directory
        is_file = False
        for extension in FILE_EXTENSIONS:
            if url.endswith(extension):
                is_file = True
                break
        
        try:
            if is_file:
                self.download_file(repo, remaining_path, f"downloads/{author}/{repository}")
            
            elif remaining_path:
                self.download_folder(repo, remaining_path, f"downloads/{author}/{repository}")

            else:
                os.makedirs(f"downloads/{author}", exist_ok=True)
                os.chdir(f"downloads/{author}")
                os.system(f"git clone -q https://github.com/{author}/{repository}.git")
                os.chdir("../..")

                print(SUCCESS + f" Repository {author}/{repository} downloaded")
        
        except:
            return

   

# -------------------------------------------------
# Parsifal module
# -------------------------------------------------
class ParsifalModule:

    # Init the API keys
    def __init__(self) -> None:
        self.mapping = {
            "polygonscan.com" : "BNKC4SHP4Y5NRTKWD83PMFYZ3AP1PVF3MZ",
            "zkevm.polygonscan.com" : "DS1J4XDHSBXTIVQ4GY1E6MIKQYASU9I3SJ", 
            "bscscan.com" : "MKF4MPCUYH6R8TJGM917CW2FX4A1RAR2Q1",
            "zksync.io" : "",
            "arbiscan.io" : "B85W9VIEA1J36CPA9UYVYX74FJSD719A1Z",
            "ftmscan.com" : "UC5NT8UE2HJCJ729I4GW7MI7V5BZITCR4G",
            "moonscan.io" : "DP8V4ACXMK1RSJ5TKVP99IGREM7PWW1ZD1",
            "starkscan.co" : "", 
            "basescan.org" : "T27ZJASHUFHSPNFCNAZDJ4C44RQCX6VJRP",
            "lineascan.build" : "YWIYEA4IFG4U82WT5UBZSEJTE9BTX2YDX7", 
            "optimistic.etherscan.io" : "QSDYQX2QYJ2TANQ2R1623IFWW8D87AW5GY",
            "snowtrace.io" : "RYNER57KGHX8BDEG4DK7DRY87WBTNIPWIA",
            "etherscan.io" : "CM623FKSS1EEMDXCQ1Q6FRWN6R2Y73NWY9"
        }

    # Just indexing and passing if the block explorer is either zkSync or Starkware, as they are not supported
    def get_explorer_and_key(self, url: str):
        
        explorer = ""
        index = 0
        for scanner in self.mapping:
            if scanner in url and scanner != "starkscan.co" and scanner != "zksync.io": # @todo support them
                explorer = scanner
                key = self.mapping[explorer]
                break
            
            index += 1

        return explorer, key

    # Fetch initial contract, fetch implementation too if it is a proxy
    def fetch_contract(self, url: str):
        explorer, key = self.get_explorer_and_key(url)
        if not explorer:
            print(WARNING + f" Block explorer API not implemented for the url {url}")
            return
        
        regex = r'0x\w*'
        # ["https:", "", "EXPLORER", "address", "0xasdhsajdhsaj", "..." ]
        address = re.match(regex, url.split("/")[4]).group(0)

        new_url = "https://api." + explorer + "/api?module=contract&action=getsourcecode&address=" + address + "&apikey=" + key
        r = requests.get(new_url)
        
        # @todo json file mostrando cosas o lo que hay es redundante ??
        data = r.json()["result"][0]
        source_code = data["SourceCode"] # @todo hacer que sea únicamente el source code y no la info adicional
        contract_name = data["ContractName"]
        compiler_version = data["CompilerVersion"]
        optimization = data["OptimizationUsed"]
        runs = data["Runs"]
        constructor_args = data["ConstructorArguments"]
        evm = data["EVMVersion"]
        is_proxy = data["Proxy"]
        implementation = data["Implementation"]

        if is_proxy == "1":
            self.fetch_implementation(explorer, implementation, key)

        output_path = f"downloads/contracts/{contract_name}"
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(source_code.encode("utf-8"))

            print(SUCCESS + f" File {output_path} successully downloaded")

        else:
            print(WARNING + f" File {output_path} does exists")
        
    # Fetch contract implementation
    def fetch_implementation(self, explorer:str, implementation: str, key: str):
        new_url = "https://api." + explorer + "/api?module=contract&action=getsourcecode&address=0x" + implementation + "&apikey=" + key
        r = requests.get(new_url)
        
        # @todo json file mostrando cosas o lo que hay es redundante ??
        data = r.json()["result"]
        source_code = data["SourceCode"]
        contract_name = data["ContractName"]
        compiler_version = data["CompilerVersion"]
        optimization = data["OptimizationUsed"]
        runs = data["Runs"]
        constructor_args = data["ConstructorArguments"]
        evm = data["EVMVersion"]

        output_path = f"downloads/contracts/{contract_name}"
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(source_code.encode("utf-8"))

            print(SUCCESS + f" File {output_path} successully downloaded")

        else:
            print(WARNING + f" File {output_path} does exists")


    # From scrapiFy::get
    def get(self, obj, id):

        if id in obj and obj[id]:
            return obj[id]
        
        return None


    # From scrapiFy::get_assets
    def get_assets(self, assets, filter=None):  

        new_assets = {}
        new_assets['github'] = []
        new_assets['contract'] = []
        new_assets['other'] = []

        if not assets:
            return new_assets

        for asset in assets:
            if filter and filter not in asset['url']:
                continue
            
            if 'github' in asset['url']:
                new_assets['github'].append(asset['url'])

            elif '/0x' in asset['url']:
                new_assets['contract'].append(asset['url'])

            else:
                new_assets['other'].append(asset['url'])
                
        return new_assets


    # From scrapiFy::get_project_data
    def get_project_data(self, url):

        try:
            page = requests.get(url, timeout=10)

        except requests.ConnectionError:
            print(ERROR + f" Error trying to fetch {url}")
            exit()

        soup = BeautifulSoup(page.content, 'html.parser')   

        soup = soup.find("script", id="__NEXT_DATA__")
        json_data = json.loads(soup.string)
        bounty = json_data['props']['pageProps']['bounty']

        return bounty

    # From scrapiFy::get_data
    def get_data(self):
        url = 'https://immunefi.com/explore/'
        main_url = 'https://immunefi.com'

        try:
            page = requests.get(url, timeout=10)
        
        except requests.ConnectionError:
            print(ERROR + f" Error trying to fetch {url}")
            exit()

        soup = BeautifulSoup(page.content, "html.parser")

        soup = soup.find("script", id="__NEXT_DATA__")
        json_data = json.loads(soup.string)
        bounties = json_data['props']['pageProps']['bounties']

        projects = []
        for project in bounties:
            if project['is_external']:
                continue

            try:
                project_detail = {}
                project_detail['id'] = self.get(project, 'id')
                project_detail['project'] = self.get(project, 'project')
                project_detail['date'] = self.get(project, 'date')
                project_detail['maximum_reward'] = self.get(project, 'maximum_reward')
                project_detail['technologies'] = self.get(project, 'technologies')
                bounty_url = main_url + '/bounty/' + project_detail['id']
                project_detail['url'] = bounty_url
                project_ext_data = self.get_project_data(bounty_url)
                project_detail['kyc'] = self.get(project_ext_data, 'kyc')

                assets = project_ext_data['assets']
                project_detail['assets_in_scope'] = self.get_assets(assets)
                project_detail['num_contracts'] = 0

                projects.append(Project(**project_detail))

            except Exception as err:
                print(ERROR + " Exception =", err)

        return projects
    


# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    print(INTRO)

    parsifal = ParsifalModule()
    git = GithubModule()
    github = Github(auth=Auth.Token("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"))

    projects = parsifal.get_data()

    # O(n²) as I have the freemium version of the explorers 
    for project in projects:
        for github_asset in project.assets_in_scope["github"]:
            try:
                git.github_download(github_asset, github)

            except:
                continue

        for contract_asset in project.assets_in_scope["contract"]:
            try:
                parsifal.fetch_contract(contract_asset)

            except:
                continue

    print(SUCCESS + " Parsifal finished downloadin everything. Let's fuck them all")


if __name__ == "__main__":
    main()