import json
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from statemachine import StateMachine, State
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

class CrawlerBot(StateMachine):
    # Definisci gli stati
    start = State('Start', initial=True)
    address_page_loaded = State('Address page loaded')
    wallet_page_loaded = State('Wallet page loaded')
    banned = State('Banned',final=True)
    OK = State("OK",final=True)

    # Definisci le transizioni
    loading_for_address = start.to(address_page_loaded,cond='thereAreAddress') | address_page_loaded.to(address_page_loaded,cond='thereAreAddress') | wallet_page_loaded.to(address_page_loaded,cond='thereAreAddress')
    loading_for_wallet = address_page_loaded.to(wallet_page_loaded,unless='thereIsCaptcha') | address_page_loaded.to(address_page_loaded,cond='thereAreAddress') | address_page_loaded.to(OK,unless='thereAreAddress')
    to_banned = address_page_loaded.to(banned,cond='thereIsCaptcha')

    finish = address_page_loaded.to(OK)

    def __init__(self, addresses,oneshot):
        self.driver = webdriver.Edge()  # o qualsiasi altro browser preferisci        
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
        })   
        self.oneshot = oneshot
        self.driver.implicitly_wait(3)
        self.addresses = addresses  # Utilizzo un set per facilitare la rimozione degli indirizzi
        self.current_address = None
        self.wallet_names = {}
        super(CrawlerBot, self).__init__()

    def thereAreAddress(self):
        return len(self.addresses) > 0
        
    def thereIsCaptcha(self):
        try:
            captcha = self.driver.find_element(By.XPATH,"//*[contains(@class, 'captcha')]")
            print("Elemento con classe 'captcha' trovato.")
            return True
        except NoSuchElementException:
            print("Elemento con classe 'captcha' non trovato.")
            return False

    def get_address_url(self):
        return f"https://bitinfocharts.com/bitcoin/address/{self.current_address}" 

    def on_enter_address_page_loaded(self):
        self.current_address = self.addresses.pop()
        self.driver.get(self.get_address_url()) 
        self._scrape_wallet_name()        

    def on_enter_wallet_page_loaded(self):
        self._check_wallet_addresses()
        self.loading_for_address()

    def on_enter_OK(self):
        self.driver.quit()

    def _scrape_wallet_name(self):
        try:
            wallet_link = self.driver.find_element(By.XPATH,'//a[contains(@href, "/wallet/")]')
            self.wallet_names[self.current_address] = wallet_link.get_attribute("href").split('/wallet/')[-1]
            if (self.oneshot):
                self.finish()
                return
            wallet_link.click()
            print("Elemento link wallet trovato.")
            self.loading_for_wallet()
            return
        except NoSuchElementException:
            print("Elemento link wallet non trovato.")

        try:
            captcha = self.driver.find_element(By.XPATH,"//*[contains(@class, 'captcha')]")
            print("Elemento con classe 'captcha' trovato.")
            self.to_banned()
            return
        except NoSuchElementException:
            print("Elemento con classe 'captcha' non trovato.")
        self.loading_for_address()
        

    def _check_wallet_addresses(self):
        try:
            address_elements = self.driver.find_elements(By.CSS_SELECTOR,
                "#ShowAddresesContainer a"
            )
            wallet_addresses = {el.text for el in address_elements}
            self.addresses -= wallet_addresses  # Remove the addresses present in the wallet
            return
        except NoSuchElementException:
            print("Elemento ShowAddresesContainer non trovato.")

        try:
            captcha = self.driver.find_element(By.XPATH,"//*[contains(@class, 'captcha')]")
            print("Elemento con classe 'captcha' trovato.")
        except NoSuchElementException:
            print("Elemento con classe 'captcha' non trovato.")
        self.loading_for_address()

    def run(self):
        self.loading_for_address()

# Funzione per cercare un indirizzo Bitcoin su WalletExplorer
def cerca_indirizzo(indirizzo):
    url = f'https://www.walletexplorer.com/address/{indirizzo}'
    response = requests.get(url)
    time.sleep(4)
    # Verifica se la richiesta è andata a buon fine
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Estrai le informazioni di interesse, ad esempio il saldo dell'indirizzo
        div_walletnote  = soup.find('div', {'class': 'walletnote'})

        # Cerca l'elemento 'a' figlio del div trovato
        elemento_a = None
        if div_walletnote:
            for child in div_walletnote.children: # type: ignore
                if child.name == 'a': # type: ignore
                    elemento_a = child
                    break

        # Estrai l'attributo 'href' dell'elemento 'a' trovato
        href = elemento_a['href'] if elemento_a else None # type: ignore
        if href:
            return href.split('/wallet/')[-1]
        else:
            return 'Informazioni non trovate'
    else:
        return f'Errore nella richiesta: {response.status_code}'


with open("clusters.json","r") as f:
    data = json.load(f)

Mapping = pd.read_csv('DataSets/2013/mapAddr2Ids8708820.csv',
                      names=['hash', 'addressId'])
Mapping['addressId'] = pd.to_numeric(Mapping['addressId'],downcast='unsigned')

sorted_cluster = sorted(data.items(), key =lambda x: len(x[1]),reverse=True)

top_10 = sorted_cluster[0:10]

del sorted_cluster

final_pd = pd.DataFrame(columns=['Address','Wallet','Fonte'])
oneshot = True #fermarsi al primo wallet trovato?
chiave=0
for cluster in top_10:
    cluster_pd = pd.DataFrame([cluster[0]] + cluster[1],columns=['addressId'])
    x =cluster_pd.merge(Mapping,how='inner')

    addresses = set(x['hash'])
    bot = CrawlerBot(addresses.copy(),oneshot)
    bot.run()

    temp=pd.DataFrame(bot.wallet_names.items(),columns=['Address','Wallet'])
    temp['Fonte'] = 'bitinfocharts.com'
    temp['ChiaveCluster']=chiave
    final_pd = pd.concat([final_pd, temp], axis=0)
    del temp

    WalletExplorer_names = {}
    while addresses:
        indirizzo = addresses.pop()
        walletName = cerca_indirizzo(indirizzo)
        WalletExplorer_names[indirizzo]=walletName
        if(oneshot):
            break

    temp=pd.DataFrame(WalletExplorer_names.items(),columns=['Address','Wallet'])
    temp['Fonte'] = 'walletexplorer.com'
    temp['ChiaveCluster']=chiave
    final_pd = pd.concat([final_pd, temp], axis=0)
    del temp
    chiave = chiave + 1
        

final_pd.to_csv('DataSets/risultato2.csv')
