"""
Bitcoin Address De-anonymization Web Scraper

This module implements automated web scraping to de-anonymize Bitcoin addresses
by finding associated wallet names from public blockchain explorers.

The scraper uses a finite state machine (FSM) architecture to navigate through
two sources:
1. BitInfoCharts.com - Primary source for wallet information
2. WalletExplorer.com - Secondary source using direct HTTP requests

The FSM-based crawler handles various states including loading address pages,
wallet pages, captcha detection, and completion states.

Architecture: See crawlerFSM.jpeg for the state machine diagram
"""

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
    """
    Finite State Machine-based web crawler for Bitcoin address de-anonymization.

    This crawler navigates BitInfoCharts.com to find wallet names associated with
    Bitcoin addresses. It uses a state machine pattern to handle different stages
    of the scraping process and edge cases like captchas.

    States:
        - start: Initial state
        - address_page_loaded: Address page successfully loaded
        - wallet_page_loaded: Wallet page successfully loaded
        - banned: Captcha detected, scraping blocked
        - OK: Scraping completed successfully

    Attributes:
        driver (WebDriver): Selenium Edge WebDriver instance
        addresses (set): Set of Bitcoin addresses to scrape
        current_address (str): Currently processed address
        wallet_names (dict): Mapping of addresses to discovered wallet names
        oneshot (bool): If True, stop after first wallet found per cluster

    Example:
        >>> addresses = {'1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', '1BvBM...'}
        >>> bot = CrawlerBot(addresses, oneshot=True)
        >>> bot.run()
        >>> print(bot.wallet_names)
    """

    # Define states
    start = State('Start', initial=True)
    address_page_loaded = State('Address page loaded')
    wallet_page_loaded = State('Wallet page loaded')
    banned = State('Banned', final=True)
    OK = State("OK", final=True)

    # Define state transitions
    # Transition to load address page (from start, previous address, or wallet page)
    loading_for_address = start.to(address_page_loaded, cond='thereAreAddress') | \
                          address_page_loaded.to(address_page_loaded, cond='thereAreAddress') | \
                          wallet_page_loaded.to(address_page_loaded, cond='thereAreAddress')

    # Transition to load wallet page (if no captcha detected)
    loading_for_wallet = address_page_loaded.to(wallet_page_loaded, unless='thereIsCaptcha') | \
                         address_page_loaded.to(address_page_loaded, cond='thereAreAddress') | \
                         address_page_loaded.to(OK, unless='thereAreAddress')

    # Transition to banned state if captcha detected
    to_banned = address_page_loaded.to(banned, cond='thereIsCaptcha')

    # Manual transition to finish
    finish = address_page_loaded.to(OK)

    def __init__(self, addresses, oneshot):
        """
        Initialize the crawler bot with addresses to scrape.

        Args:
            addresses (set): Set of Bitcoin addresses (hashes) to de-anonymize
            oneshot (bool): If True, stop after finding first wallet per cluster
                           If False, process all addresses in the set

        Note:
            Initializes Edge WebDriver with anti-detection measures to avoid
            being flagged as a bot by modifying the navigator.webdriver property.
        """
        self.driver = webdriver.Edge()  # Edge browser (can use Chrome, Firefox, etc.)

        # Anti-detection: Hide webdriver property to avoid bot detection
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
        })

        self.oneshot = oneshot
        self.driver.implicitly_wait(3)  # Wait up to 3 seconds for elements to appear
        self.addresses = addresses  # Set allows efficient removal of processed addresses
        self.current_address = None
        self.wallet_names = {}
        super(CrawlerBot, self).__init__()

    def thereAreAddress(self):
        """
        Condition function: Check if there are addresses remaining to process.

        Returns:
            bool: True if addresses remain in the queue, False otherwise
        """
        return len(self.addresses) > 0

    def thereIsCaptcha(self):
        """
        Condition function: Check if a captcha is present on the current page.

        This is used to detect if the scraper has been flagged and blocked by
        the website's anti-bot measures.

        Returns:
            bool: True if captcha element found, False otherwise
        """
        try:
            captcha = self.driver.find_element(By.XPATH, "//*[contains(@class, 'captcha')]")
            print("Captcha element detected - bot may be blocked.")
            return True
        except NoSuchElementException:
            print("No captcha found - continuing scraping.")
            return False

    def get_address_url(self):
        """
        Generate the BitInfoCharts URL for the current Bitcoin address.

        Returns:
            str: Full URL to the address page on bitinfocharts.com
        """
        return f"https://bitinfocharts.com/bitcoin/address/{self.current_address}"

    def on_enter_address_page_loaded(self):
        """
        State entry handler: Load and scrape an address page.

        This method is called when entering the address_page_loaded state.
        It pops an address from the queue, navigates to its page, and
        attempts to scrape wallet information.
        """
        self.current_address = self.addresses.pop()
        self.driver.get(self.get_address_url())
        self._scrape_wallet_name()

    def on_enter_wallet_page_loaded(self):
        """
        State entry handler: Process a wallet page.

        This method is called when entering the wallet_page_loaded state.
        It checks all addresses associated with the wallet and removes them
        from the processing queue (since they're all part of the same wallet).
        """
        self._check_wallet_addresses()
        self.loading_for_address()

    def on_enter_OK(self):
        """
        State entry handler: Clean up when scraping completes successfully.

        Closes the WebDriver to free resources.
        """
        self.driver.quit()

    def _scrape_wallet_name(self):
        """
        Extract wallet name from the current address page.

        Attempts to find a wallet link on the address page. If found, extracts
        the wallet name and either finishes (if oneshot mode) or navigates to
        the wallet page for further processing.

        Side effects:
            - Updates self.wallet_names with discovered wallet name
            - May trigger state transition (to wallet page, banned, or next address)
            - Prints status messages

        Transitions:
            - To wallet_page_loaded: If wallet found and oneshot=False
            - To OK: If wallet found and oneshot=True
            - To banned: If captcha detected
            - To next address: If no wallet found and no captcha
        """
        try:
            wallet_link = self.driver.find_element(By.XPATH, '//a[contains(@href, "/wallet/")]')
            self.wallet_names[self.current_address] = wallet_link.get_attribute("href").split('/wallet/')[-1]
            if (self.oneshot):
                self.finish()
                return
            wallet_link.click()
            print("Wallet link element found.")
            self.loading_for_wallet()
            return
        except NoSuchElementException:
            print("Wallet link element not found.")

        # Check for captcha if wallet not found
        try:
            captcha = self.driver.find_element(By.XPATH, "//*[contains(@class, 'captcha')]")
            print("Captcha element detected.")
            self.to_banned()
            return
        except NoSuchElementException:
            print("No captcha found.")
        self.loading_for_address()

    def _check_wallet_addresses(self):
        """
        Extract all addresses belonging to the current wallet.

        Scrapes the wallet page to find all associated Bitcoin addresses.
        These addresses are removed from the processing queue since they
        all belong to the same wallet (already identified).

        Side effects:
            - Removes discovered addresses from self.addresses queue
            - Prints status messages

        Note:
            This optimization prevents redundant scraping of addresses that
            are already known to belong to an identified wallet.
        """
        try:
            address_elements = self.driver.find_elements(By.CSS_SELECTOR,
                "#ShowAddresesContainer a"
            )
            wallet_addresses = {el.text for el in address_elements}
            # Remove all addresses in this wallet from the queue (efficiency optimization)
            self.addresses -= wallet_addresses
            return
        except NoSuchElementException:
            print("ShowAddresesContainer element not found.")

        try:
            captcha = self.driver.find_element(By.XPATH, "//*[contains(@class, 'captcha')]")
            print("Captcha element detected.")
        except NoSuchElementException:
            print("No captcha found.")
        self.loading_for_address()

    def run(self):
        """
        Start the scraping process.

        Initiates the state machine by triggering the first state transition
        to load the first address page.
        """
        self.loading_for_address()

def cerca_indirizzo(indirizzo):
    """
    Search for a Bitcoin address on WalletExplorer using HTTP requests.

    This is an alternative scraping method that uses direct HTTP requests
    instead of Selenium. It searches WalletExplorer.com for wallet information
    associated with a Bitcoin address.

    Args:
        indirizzo (str): Bitcoin address hash to search for

    Returns:
        str: Wallet name if found, 'Informazioni non trovate' if not found,
             or error message if request fails

    Note:
        Includes a 4-second sleep to avoid rate limiting and being blocked
        by the website.

    Example:
        >>> wallet_name = cerca_indirizzo('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        >>> print(wallet_name)
    """
    url = f'https://www.walletexplorer.com/address/{indirizzo}'
    response = requests.get(url)
    time.sleep(4)  # Rate limiting to avoid being blocked

    # Check if request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract wallet information from the page
        div_walletnote = soup.find('div', {'class': 'walletnote'})

        # Find the anchor element child of the walletnote div
        elemento_a = None
        if div_walletnote:
            for child in div_walletnote.children: # type: ignore
                if child.name == 'a': # type: ignore
                    elemento_a = child
                    break

        # Extract the href attribute from the anchor element
        href = elemento_a['href'] if elemento_a else None # type: ignore
        if href:
            return href.split('/wallet/')[-1]
        else:
            return 'Informazioni non trovate'  # Information not found
    else:
        return f'Errore nella richiesta: {response.status_code}'  # Request error


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
