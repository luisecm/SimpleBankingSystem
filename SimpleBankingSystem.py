import sys
import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()
random.seed = 0
new_credit_card_number = 0
new_pin_number = 0
switch = 0
new_account_number = 0
results1 = None
option_account_logged = ""
where_to_transfer = 0
destination_exists = 0
current_balance = 0
log_into_option_card = 0
how_much_to_transfer = 0

def find_luhn_checksum():
    global new_credit_card_number
    new_account_number_to_match = [int(x) for x in str(new_credit_card_number)]
    for x in range(0, len(new_account_number_to_match), 2):
        new_account_number_to_match[x] = new_account_number_to_match[x] * 2
    for y in range(len(new_account_number_to_match)):
        if new_account_number_to_match[y] > 9:
            new_account_number_to_match[y] -= 9 
    last_digit = 0
    te_lo_sumo = sum(new_account_number_to_match)
    while((last_digit + te_lo_sumo) % 10 != 0):
        last_digit += 1
    new_credit_card_number = int(str(new_credit_card_number) + str(last_digit))

def login_account():
    global results1
    global cur
    global conn
    global switch
    global credit_cards_on_system
    global log_into_option_card
    switch = 0
    log_into_option_card = int(input("Enter your card number: "))
    log_into_option_pin = input("Enter your PIN number: ")
    login_query = "SELECT count(*) FROM card WHERE number = " + str(log_into_option_card) + " AND pin = '" + log_into_option_pin + "'"
    cur.execute(login_query)
    conn.commit()
    results1 = cur.fetchone()[0]
    if results1 == 0:
        print("Wrong card number or PIN!")
        main_menu()
    elif results1 == 1:
        print("You have successfully logged in!")
        account_logged()

def account_logged():
    global option_account_logged
    print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
    option_account_logged = input()
    if option_account_logged == '1':
        get_balance()
    elif option_account_logged == '2':
        add_income()
    elif option_account_logged == '3':
        make_transfer()
    elif option_account_logged == '4':
        delete_account()
    elif option_account_logged == '5':
        print("Logged out from account!")
        main_menu()
    elif option_account_logged == '0':
        goodbye()

def get_balance():
    global log_into_option_card
    global results1
    global cur
    global conn
    show_balance_query = "SELECT balance FROM card WHERE number = " + str(results1) + ";"
    cur.execute(show_balance_query)
    conn.commit()
    new_balance = int(cur.fetchone()[0])
    print("Balance: " + str(new_balance))
    account_logged()

def add_income():
    global log_into_option_card
    global cur
    global conn
    new_income = int(input("Enter income: "))
    show_balance_query = "SELECT balance FROM card WHERE number = " + str(log_into_option_card) + ";"
    cur.execute(show_balance_query)
    conn.commit()
    while True:
        new_balance = cur.fetchone()[0]
        if new_balance is None:
            break
        new_balance = int(new_balance)
        new_balance += new_income
        add_balance_query = "UPDATE card SET balance = " + str(new_balance) + " WHERE number = " + str(log_into_option_card) + ";"
        cur.execute(add_balance_query)
        conn.commit()
        print("Income was added!")
        account_logged()

def make_transfer():
    global log_into_option_card
    global cur
    global conn
    global where_to_transfer
    global how_much_to_transfer
    global current_balance
    global where_to_transfer
    print("Transfer")
    where_to_transfer = int(input("Enter card number: "))
    if validate_luhn_algorith() == True:
        if validate_destination_is_not_same() == True:
            if validate_destination_exists() == True:
                how_much_to_transfer = int(input("Enter how much money you want to transfer: "))
                show_balance_query = "SELECT balance FROM card WHERE number = " + str(log_into_option_card) + ";"
                cur.execute(show_balance_query)
                conn.commit()
                while True:
                    current_balance = cur.fetchone()[0]
                    if current_balance is None:
                        current_balance = 0
                        break
                    current_balance = int(current_balance)
                    validate_enough_money()
            else:
                print("Such a card does not exist.")
                account_logged()
        else:
            print("You can't transfer money to the same account")
            account_logged()
    else:
        print("Probably you made a mistake in the card number. Please try again!")
        account_logged()

def validate_enough_money():
    global current_balance
    global how_much_to_transfer
    global conn
    global cur
    global log_into_option_card
    global where_to_transfer
    if how_much_to_transfer > current_balance:
        print("Not enough money!")
        account_logged()
    else:
        balance_of_destination = "SELECT balance FROM card WHERE number = " + str(where_to_transfer) + ";"
        cur.execute(balance_of_destination)
        conn.commit()
        while True:
            current_balance_destiny = cur.fetchone()[0]
            if current_balance_destiny is None:
                current_balance_destiny = 0
                break
            current_balance_destiny = int(current_balance_destiny)
            current_balance_destiny += how_much_to_transfer
            current_balance -= how_much_to_transfer
            make_transfer_query_2 = "UPDATE card SET balance = " + str(current_balance_destiny) + " WHERE number = " + str(where_to_transfer) + ";"
            cur.execute(make_transfer_query_2)
            conn.commit()
            make_transfer_query = "UPDATE card SET balance = " + str(current_balance) + " WHERE number = " + str(log_into_option_card) + ";"
            cur.execute(make_transfer_query)
            conn.commit()
            print("Success!")
            account_logged()

def validate_luhn_algorith():
    global where_to_transfer
    where_to_transfer_temp = [int(x) for x in str(where_to_transfer)]
    for x in range(0, len(where_to_transfer_temp), 2):
        where_to_transfer_temp[x] = where_to_transfer_temp[x] * 2
    for y in range(len(where_to_transfer_temp)):
        if where_to_transfer_temp[y] > 9:
            where_to_transfer_temp[y] -= 9
    if sum(where_to_transfer_temp) % 10 == 0:
        return True
    else:
        return False

def validate_destination_is_not_same():
    global where_to_transfer
    global log_into_option_card
    if where_to_transfer != log_into_option_card:
        return True
    else:
        return False

def validate_destination_exists():
    global where_to_transfer
    global destination_exists
    find_destination_account = "SELECT count(*) FROM card WHERE number = " + str(where_to_transfer) + ";"
    cur.execute(find_destination_account)
    destination_exists = cur.fetchone()[0]
    conn.commit()
    if destination_exists >= 1:
        return True
    elif destination_exists == 0:
        return False

def delete_account():
    global log_into_option_card
    global cur
    global conn
    delete_account_query = "DELETE FROM card WHERE number = " + str(log_into_option_card) + ";"
    cur.execute(delete_account_query)
    conn.commit()
    print("The account has been closed!")
    main_menu()

def create_account():
    global cur
    global con
    global new_account_number
    global new_credit_card_number
    global new_pin_number
    new_account_number = "%09d" % random.randint(0,999999999)
    new_credit_card_number = int(str(400000) + new_account_number)
    new_pin_number = "%04d" % random.randint(0,9999)
    find_luhn_checksum()
    print("Your card has been created")
    print("Your card number:" + str(new_credit_card_number))
    print("Your card PIN: ")
    print(new_pin_number)
    next_id = str(new_credit_card_number)
    next_id = next_id[6:15]
    insert_query = "INSERT INTO card (id, number, pin, balance) VALUES (" + next_id + ", '" + str(new_credit_card_number) + "', '" + str(new_pin_number) + "', 0);"
    cur.execute(insert_query)
    conn.commit()
    main_menu()


def main_menu():
    print("")
    print("""1. Create an account
2. Log into account
0. Exit""")
    main_menu_option = int(input())
    if main_menu_option == 0:
        goodbye()
    elif main_menu_option == 1:
        create_account()
    elif main_menu_option == 2:
        login_account()

def goodbye():
    global conn
    print("Bye!")
    conn.close()
    sys.exit()

main_menu()
