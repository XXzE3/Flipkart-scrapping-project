from bs4 import BeautifulSoup as bs
import requests
import os
import platform
from plyer import notification
import time

# assigning headers to get proper response from the server
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'http://google.com',
}

def clear_screen():
    '''
    Clears the terminal screen
    '''
    if platform.system()=='Windows':
        os.system('cls')
    else:
        os.system('clear')


def max_page(url):
    '''
    Returns the total number of pages available for searching.
    If total page is not there in the webpage, returns a value of 1
    '''
    url = url
    r = requests.get(url,headers=headers)
    try:
        if r.status_code == 200: # checking for proper connection
            soup = bs(r.content,'lxml')
            pages = soup.find('div', class_ = '_1G0WLw').span.text.split(' ')[-1].replace(',','') # extracting the total number of pages
            return int(pages)
        else:
            print('Server not responding')
            return
    except ValueError as v:
        print(f'Error {v}')
        return
    except AttributeError:
        pages = 1
        return pages


def check_product_class(parsed_HTML):
    '''
    Take the class.txt file and creates a dictionary with number as keys,
    product class and product link class as values in a list format.
    Check the input parsed HTML for which product class is present and returns
    the product link class along with the product class find all values.    
    '''
    class_dict = {}
    try:
        with open ('class.txt','r') as f:
            for line in f:
                g = line.strip().split(',')
                if g[2].lower() == "none":
                    g[2] = None
                class_dict[int(g[0])] = [g[1],g[2]]
    except:
        print('Error. Check your class.txt file or directory')
        return

    for i in range(len(class_dict)):
        product_class = class_dict[i][0]
        product = parsed_HTML.find_all('div',class_ = product_class)
        if product: # check here
            break
    product_link_class = class_dict[i][1]
    return product, product_link_class


def product_links(url,page=1):
    '''
    Takes the URL and returns all the product links on the given number of pages in a list format
    '''
    base_url='https://www.flipkart.com'
    url = url
    link_list = []
    class_detected = False #class is not detected
    for i in range(1,page+1):
        r = requests.get(url,headers=headers)
        
        if r.status_code == 200:
            r = r.content
            soup = bs(r,'lxml')
            
            if not class_detected:
                product, link_class = check_product_class(soup)
                class_detected = True #class is detected
            for prod in product:
                link = prod.find('a', class_ = link_class)['href'] # product links in the page
                link_list.append(base_url+link) # collecting the clickable link by joining the base link
            
            next_link = soup.find('a',class_ = '_9QVEpD')
            if next_link is not None: #check for the presence of next link (for cases when only one page is present)
                next_link = soup.find('a',class_ = '_9QVEpD')['href'] # link to next page
                url = base_url+next_link # clickable link of next page
        
        else:
            print('Request generation failed. Not able to generate links')
            print(r)
            return 
    
    return link_list


def get_details(link_list):
    '''
    Takes a list of clickable links and finds the Name, Rating,
    Number of ratings, Number of reviews, Actual price, Current price and Link of the products
    to create a dictionary.
    '''
    total = len(link_list)
    print(f'Getting details for {total} products')
    product_details = {'Name':[],"Rating":[],"Number of ratings":[],'Number of reviews':[],"Actual Price":[], "Current Price":[], "Link":[]}
    for i,link in enumerate(link_list,1):
        url = link
        r = requests.get(url,headers=headers)
        if r.status_code == 200:

            r = r.content
            soup = bs(r,'lxml')

            # extracting name
            try:
                name = soup.find('span',class_ = 'VU-ZEz').text
            except:
                name = 'Unable to fetch.'

            # extracting rating
            try:
                rating = float(soup.find('div',class_='XQDdHH').text)
            except:
                rating = 0
            
            # extracting number of ratings and reviews
            try:
                rate = soup.find('span', class_ = "Wphh3N").text.split(' ')
            except:
                rate = []
            try:
                ratings = int(rate[0].replace(',',''))
            except:
                ratings = 0            
            try:
                reviews = int(rate[1][10:].replace(',',''))
            except:
                reviews = 0
            
            # extracting actual price 
            try:
                actualprice = float(soup.find('div',class_ = 'yRaY8j A6+E6v').text[1:].replace(',',''))
            except:
                actualprice = 'Not available'
            
            # extracting discount price
            try:
                price = float(soup.find('div',class_ = 'Nx9bqj CxhGGd').text[1:].replace(',',''))
            except:
                price = 'Not available'
            
            product_details['Name'].append(name)
            product_details["Rating"].append(rating)
            product_details["Number of ratings"].append(ratings)
            product_details['Number of reviews'].append(reviews)
            product_details["Actual Price"].append(actualprice)
            product_details["Current Price"].append(price)
            product_details['Link'] = link

            clear_screen()
            print(f'Getting details for {total} products')
            print('[','█'*i,' '*(total-i),']',end=' ')
            print(f'{i}/{total}')
            
        else:
            print(f'{i} not done')
            print (f'Reponse code --> {r.status_code}')
            return 
    return product_details


def notify(title,message):
    '''
    Sends a notification with the title and message
    '''
    notification.notify(
            title=title,
            message=message,
            timeout=20
        )


def price_notifier(url,target_price,recheck_hour):
    '''
    Takes the product link and target price to check if the price has dropped below target.
    Rechecks every user input hour and sends a notification if price has dropped below target.
    '''
    while True:
        r = requests.get(url,headers=headers)
        if r.status_code == 200:
            r = r.content
            soup = bs(r,'lxml')
            # extracting discount price
            try:
                disprice = float(soup.find('div',class_ = 'Nx9bqj CxhGGd').text[1:].replace(',',''))
                name = soup.find('span',class_ = 'VU-ZEz').text
            except:
                disprice = 'Not available'
        else:
            print (f'Reponse code --> {r.status_code}')
            print(f'Cannot proceed. Retrying in {recheck_hour} hours....')
            time.sleep(recheck_hour*60)
            continue 
        
        if disprice == 'Not available': # skip to next loop if price is not fetched
            print(f'Unable to fetch. Retrying in {recheck_hour} hours....')
            time.sleep(recheck_hour*60)
            continue
        
        if disprice <= target_price: #checking price to notify
            notify("Price Drop Alert!",f"The price for {name} \nhas dropped to {disprice}\nBuy now!")
            break
        
        print(f'Price is {disprice}. Trying again in {recheck_hour} hours....')
        time.sleep(recheck_hour*60*60)


