import time
import xml.etree.ElementTree as ET

#Time is system clock by default, can be set manually via the set_time function
current_time = time.strftime("%H:%M")

#XML file builder function
def build_xml_file():
    floor = ["A", "B", "C", "D"]    
    lots_per_floor = ["-2", "-1", "1", "2", "3",
                      "4", "5", "6", "7", "8",
                      "9", "10", "11", "12", "13",
                      "14", "15", "16", "17", "18",
                      "19", "20", "21", "22", "23"]

    garage = ET.Element("garage")
    lots = ET.SubElement(garage, "lots")
    for i in range(len(floor)):
        for j in range(len(lots_per_floor)):
            if j < 2:
                lot = ET.SubElement(lots, "lot", id=f"{floor[i]}{lots_per_floor[j]}", disabled="true")
                bookings = ET.SubElement(lot, "bookings")
            else:    
                lot = ET.SubElement(lots, "lot", id=f"{floor[i]}{lots_per_floor[j]}", disabled="false")
                bookings = ET.SubElement(lot, "bookings")
    meta = ET.SubElement(garage, "metadata")
    next_booking_id = ET.SubElement(meta, "next_booking_id")
    next_booking_id.text = "1"
    current_time_element = ET.SubElement(meta, "current_time")
    current_time_element.text = current_time
    tree = ET.ElementTree(garage)
    tree.write("data.xml")

#Set time function
def set_time():
    global current_time
    time_input = input("Enter the current time (HH:MM): ")
    try:
        # Validate and set the time
        hours, minutes = map(int, time_input.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            current_time = f"{hours:02d}:{minutes:02d}"
            print(f"Time set to {current_time}.")
        else:
            print("Invalid time format. Please enter a valid time.")
    except ValueError:
        print("Invalid input. Please enter time in HH:MM format.")

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

#If the XML file does not exist, create it
try:
    with open("data.xml", "r") as file:
        pass
except FileNotFoundError:
    build_xml_file()


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