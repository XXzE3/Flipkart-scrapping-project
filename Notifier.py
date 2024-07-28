from scrapping_module import price_notifier
import sys



def main():
    url = input("Enter the product link: ")
    
    try:
        target_price = float(input("Enter the target price: "))
        recheck_hours = float(input("Enter time interval to recheck (in hours): "))
    except ValueError:
        print('Enter valid numbers')
        return

    price_notifier(url,target_price,recheck_hours)
    print('Execution complete')
    sys.exit()


if __name__ == "__main__":
    main()