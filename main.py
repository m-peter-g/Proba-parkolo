#Structured menu for user to select the desired option
def display_menu():
    print("Welcome to the Application!")
    print("Please select an option:")
    print("1. Book lot")
    print("2. List lots")
    print("3. Remove reservation")
    print("4. Set time")
    print("5. Exit")

    choice = input("Enter your choice (1-5): ")
    return choice

#Call menu, handle choice
while True:
    user_choice = display_menu()

    if user_choice == '1':
        # Call the function to book a lot
        book_lot()
    elif user_choice == '2':
        # Call the function to list lots
        list_lots()
    elif user_choice == '3':
        # Call the function to remove a reservation
        remove_reservation()
    elif user_choice == '4':
        # Call the function to set time
        set_time()
    elif user_choice == '5':
        break
    else:
        print("Invalid choice. Please try again.")