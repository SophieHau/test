import json
from datetime import datetime, date

def show_menu():
    while True:
        option = input('If you want to register your car type 1\nIf you want to rent a car type 2\nIf you wnat to exit type any other key\nYour choice here: ')
        if option == '1':
            register_car()
        elif option == '2':
            rent_car()
        else:
            print('Bye')   
            break         
        
def register_car():
    price_per_day = input('What is the price per day? ')
    price_per_km = input('What is the price per km? ')
    data_file = read_input_json()
    cars_list = data_file['cars']
    last_car_on_list = cars_list[-1]
    id = int(last_car_on_list['id']) + 1
    new_car = {
        'id': id,
        'price_per_day': int(price_per_day),
        'price_per_km': int(price_per_km)
    }
    cars_list.append(new_car)
    data_file['cars'] = cars_list
    update_input_json(data_file)
    
def read_input_json():
    with open('data/input.json', 'r') as file:
        data_file = json.load(file)
        return data_file
        
def read_output_json():
    with open('data/expected_output.json', 'r') as file:
        output_file = json.load(file)
        return output_file
    
def update_input_json(data):
	with open('data/input.json', 'w') as f:
		json.dump(data, f)
        
def find_car(car_id):
    data_file = read_input_json()
    for car in data_file['cars']:
        if car['id'] == car_id:
            return car

def show_cars():    
    data_file = read_input_json()
    print('Choose a car:\n')
    for car in data_file['cars']:
        print('Car #{}, {}$ per day, {}$ per km'.format(car['id'], car['price_per_day'], car['price_per_km']))
    
def choose_car():    
    choice = input('Enter the number of the car you want to rent: ')
    return int(choice)
    
def rent_car():
    data_file = read_input_json()
    show_cars()
    car_id = choose_car()
    for car in data_file['cars']:
        if car_id == car['id']:
            rental_start_year = input('Enter the rental start date. Year: ')
            rental_start_month = input('Month: ')
            rental_start_day = input('Day: ')
            rental_end_year = input('Enter the rental end date. Year: ')
            rental_end_month = input('Month: ')
            rental_end_day = input('Day: ')
            total_rental_days = calculate_rental_days(int(rental_start_year), 
                                                      int(rental_start_month), 
                                                      int(rental_start_day), 
                                                      int(rental_end_year),
                                                      int(rental_end_month), 
                                                      int(rental_end_day))
            rental_price = calculate_rental_price(car_id, total_rental_days)
            
            print('The total price for this rental is {}'.format(rental_price))
            booking = input('Would you like to book it (y/n)? ')
            
            commission = calculate_commission(rental_price, total_rental_days)
            drivy_fee = commission['drivy_fee']
            owner_amount = rental_price - (commission['insurance_fee'] 
                          + commission['assistance_fee'] + drivy_fee)
            
            options_list = []
            
            gps = input('would you like to add GPS for 5€/day (y/n)? ')
            if gps == 'y':
                owner_amount = add_gps(gps, owner_amount, total_rental_days)
                options_list.append('gps')
            
            baby_seat = input('would you like to add a baby seat (y/n)? ')
            if baby_seat == 'y':
                owner_amount = add_baby_seat(baby_seat, owner_amount, total_rental_days)
                options_list.append('baby_seat')
            
            additional_insurance = input('Would you like to add insurance (y/n) ?')
            if additional_insurance == 'y':
                drivy_fee = add_insurance(additional_insurance, commission['drivy_fee'], total_rental_days)
                options_list.append('additional_insurance')
            
            actions = [
                {
                  "who": "driver",
                  "type": "debit",
                  "amount": rental_price
                },
                {
                  "who": "owner",
                  "type": "credit",
                  "amount": owner_amount
                },
                {
                  "who": "insurance",
                  "type": "credit",
                  "amount": commission['insurance_fee']
                },
                {
                  "who": "assistance",
                  "type": "credit",
                  "amount": commission['assistance_fee']
                },
                {
                  "who": "drivy",
                  "type": "credit",
                  "amount": commission['drivy_fee']
                }
            ]
            
            rentals = read_output_json()
            rentals_list = rentals['rentals']
            last_rental_on_list = rentals_list[-1]
            id = int(last_rental_on_list['id']) + 1
            if booking == 'y':
                new_rental = {
                    'id': id,
                    'options': options_list,
                    'actions': actions
                }
                rentals_list.append(new_rental)
                rentals['rentals'] = rentals_list
                with open('data/expected_output.json', 'w') as j:            
                    json.dump(rentals, j)

def add_gps(gps, owner_amount, total_rental_days):
    new_owner_amount = owner_amount + 5 * total_rental_days
    return new_owner_amount

def add_baby_seat(baby_seat, owner_amount, total_rental_days):
    new_owner_amount = owner_amount + 2 * total_rental_days
    return new_owner_amount
    
def add_insurance(additional_insurance, drivy_fee, total_rental_days):
    new_drivy_fee = drivy_fee + 10 * total_rental_days
    return new_drivy_fee

def calculate_rental_days(rental_start_year, rental_start_month, rental_start_day, rental_end_year, rental_end_month, rental_end_day):
    t1 = date(rental_start_year, rental_start_month, rental_start_day)
    t2 = date(rental_end_year, rental_end_month, rental_end_day)
    delta = t2 - t1
    total_days = delta.days
    return total_days
                        
def calculate_rental_price(car_id, total_rental_days):
    car = find_car(car_id)
    rental_distance = input('What distance will you travel? ')
    rental_price_days = calculate_discount(total_rental_days, car['price_per_day'])
    rental_price_days = int(rental_price_days)
    rental_price_km = int(rental_distance) * car['price_per_km']
    rental_total_price = rental_price_days + rental_price_km
    return rental_total_price
        
def calculate_discount(total_rental_days, price_per_day):    
    discount_one = price_per_day - (price_per_day * 10 / 100)
    discount_two = price_per_day - (price_per_day * 30 / 100)
    discount_three = price_per_day - (price_per_day / 2)
    
    if total_rental_days > 1 and total_rental_days <= 4:
        total = price_per_day + (total_rental_days - 1) * discount_one
        return total
    elif total_rental_days > 4 and total_rental_days <= 10:
        total = price_per_day + (total_rental_days - 1) * discount_one 
        + (total_rental_days - 4) * discount_two
        return total
    elif total_rental_days > 10:
        total = price_per_day + (total_rental_days - 1) * discount_one 
        + (total_rental_days - 4) * discount_two 
        + (total_rental_days - 10) * discount_three
        return total


def calculate_commission(rental_price, total_rental_days):
    commission = rental_price * 0.3
    insurance_fee = commission / 2
    assistance_fee = total_rental_days
    drivy_fee = commission - insurance_fee - assistance_fee
    
    commission = {
        'insurance_fee': int(insurance_fee),
        'assistance_fee': int(assistance_fee),
        'drivy_fee': int(drivy_fee)
    }

    return commission
            
show_menu()
