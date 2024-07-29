import pandas as pd
from scrapping_module import *


def main():
    '''
    Takes the input for URL and Number of pages to search from user and
    creates a database inside the directory Scrapped databases.
    '''
    url = input('Enter the URL >')
    page = max_page(url)
    if not page:
        print('Unable to proceed. Pages not detected')
        return
    else:
        print(f'{page} total pages detected')
    
    try:
        if url.find('page=') == -1:
            pages = int(input(f'Enter number of pages to search (between 1-{page}) >'))
            if pages > page or pages == 0:
                raise Exception(f'Please enter a value between 1-{page}')
        else:
            start_id = url.find('page=')+len('page=')
            start_page = int(url[start_id:start_id+1])
            print(f'You are on page {start_page}. The scrapping will start from this page')
            pages = int(input(f'Enter number of pages to search (maximum {page-start_page-1}) >'))
            if pages > page-start_page-1 or pages == 0:
                raise Exception(f'Please enter a value between {page}-{page-start_page-1}')
    except ValueError:
        print('Please enter a valid integer')
        return
    except Exception as e:
        print(f'Unexpected error: {e}')
        return

    try:
        link_list = product_links(url,pages)
        if not link_list:
            print('Unable to proceed. Product links not generated')
            return
    except Exception as e:
        print(f'Unexpected error: {e}')
        print('Please check the URL or the number of pages to search')
        return
    

    try:
        product_details = get_details(link_list)
        if product_details is None:
            print('Unable to proceed. Product details not obtained')
            return
    except Exception as e:
        print(f'Unexpected error: {e}')
        print('Some error occured. Please run the program again')
        return
    
    dataset_name = input('Enter dataset name >')
    data = pd.DataFrame(product_details)
    data.to_csv(f'Scrapped_databases\{dataset_name}.csv')
    print('Dataset created')



if __name__ == "__main__":
    main()







   