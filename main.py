import time
import xml.etree.ElementTree as ET

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
    meta = ET.SubElement(garage, "meta")
    next_booking_id = ET.SubElement(meta, "next_booking_id")
    next_booking_id.text = "1"
    current_time_element = ET.SubElement(meta, "current_time")
    current_time_element.text = time.strftime("%H:%M")
    tree = ET.ElementTree(garage)
    ET.indent(tree, space="\t", level=0) #for pretty printing
    tree.write("data.xml")

def main_menu():
    print("Welcome to the Application!")
    print("Please select an option:")
    print("1. Book lot")
    print("2. List lots")
    print("3. Remove reservation")
    print("4. Modify lot")
    print("5. Set time")
    print("6. Exit")

    choice = input("Enter your choice (1-6): ")
    return choice

def modify_menu():
    print("1. Modify lot ID")
    print("2. Modify reservation times")
    print("3. Back")

    choice = input("Enter your choice (1-3): ")
    return choice
    

#modify lot function
def modify_lot():
    booking_id = input("Enter the booking ID to of the booking you are looking to modify: ")
    data = ET.open("data.xml")
    lots = data.getroot().find("lots").findall("lot")
    bookings = lots.getroot().findall("bookings")
    if not bookings:
        print("No bookings found.")
        return
    for lot in lots:
        for booking in bookings:
            if booking.get("id") == booking_id:
                booking_lot_id = lot.get("id").text
                booking_plate = booking.find("plate").text
                booking_arrival = booking.find("arrival").text
                booking_departure = booking.find("departure").text
                print(f"{booking_id} => Lot: {booking_lot_id}, Plate: {booking_plate}, Reservation: ({booking_arrival}-{booking_departure})")
                done = False         
                while not done:   
                    modify_choice = modify_menu()
                    if modify_choice == "1":
                        tmp = input("Enter the new lot ID: ")
                        # Check if the new lot ID exists
                        new_lot = data.getroot().find(f"lots/lot[@id='{tmp}']")
                        if new_lot is None:
                            print(f"Lot ID {tmp} does not exist.")
                            continue
                        # Check if the new lot is disabled
                        if new_lot.get("disabled") == "true":
                            allowed = input(f"Lot ID {tmp} is a handicapped lot, are you allowed to park here? (y/n): ")
                            if allowed.lower() != "y":
                                continue
                        # Check if the new lot is already booked
                        if tmp == booking_lot_id:
                            print(f"Booking is already in lot {tmp}.")
                            continue
                        new_lot_id = tmp
                    elif modify_choice == "2":
                        print(f"Current reservation times: ({booking_arrival}-{booking_departure})")
                        print("Make sure departure time is later than arrival time and does not overlap with existing bookings in the same lot.")
                        tmp_arrival = input("Enter the new arrival time (HH:MM): ")
                        tmp_departure = input("Enter the new departure time (HH:MM): ")
                        # Validate the new arrival and departure times
                        try:
                            arrival_hours, arrival_minutes = map(int, tmp_arrival.split(':'))
                            departure_hours, departure_minutes = map(int, tmp_departure.split(':'))
                            if not (0 <= arrival_hours < 24 and 0 <= arrival_minutes < 60 and
                                    0 <= departure_hours < 24 and 0 <= departure_minutes < 60):
                                print("Invalid time format. Please enter valid times.")
                                continue
                            if tmp_arrival >= tmp_departure:
                                print("Departure time must be later than arrival time and no overnight parking! >:(")
                                continue
                        except ValueError:
                            print("Invalid input. Please enter time in HH:MM format.")
                            continue    
                            
                        confirm = input(f"Your new booking is ({tmp_arrival}-{tmp_departure}). (y/n)")
                        if confirm.lower() == "y":
                            new_arrival = tmp_arrival
                            new_departure = tmp_departure
                    elif modify_choice == "3":
                        return

                    if new_lot_id:
                        #Check if reservation times overlap with existing bookings in the new lot
                        new_lot_bookings = new_lot.find("bookings").findall("booking")
                        overlap = False
                        for new_booking in new_lot_bookings:
                            new_booking_arrival = new_booking.find("arrival").text
                            new_booking_departure = new_booking.find("departure").text
                            if (new_arrival < new_booking_departure and new_departure > new_booking_arrival or booking_arrival < new_booking_departure and booking_departure > new_booking_arrival):
                                overlap = True
                                break
                        if overlap:
                            print(f"Reservation times overlap with existing bookings in lot {new_lot_id}, change reservation times or select a different lot.")
                        

            
                
                
                
                data.write("data.xml")
                print(f"Booking {booking_id} modified to lot {new_lot_id}.")
                return
            else:
                print(f"No booking found with ID {booking_id}.")
                modify_lot()  # Call the function again to allow the user to try again
    


#Set time function
def set_time():
    time_input = input("Enter the current time (HH:MM): ")
    try:
        # Validate and set the time
        hours, minutes = map(int, time_input.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            current_time = f"{hours:02d}:{minutes:02d}"
            data = ET.parse("data.xml")
            meta = data.getroot().find("meta")
            current_time_element = meta.find("current_time")
            current_time_element.text = current_time
            data.write("data.xml")            
            print(f"Time set to {current_time}.")
        else:
            print("Invalid time format. Please enter a valid time.")
    except ValueError:
        print("Invalid input. Please enter time in HH:MM format.")


#If the XML file does not exist, create it
#If it does exist set system clock as current time
try:
    with open("data.xml", "r") as file:
        data = ET.parse("data.xml")
        meta = data.getroot().find("meta")
        current_time_element = meta.find("current_time")
        current_time_element.text = time.strftime("%H:%M")
        data.write("data.xml")
except FileNotFoundError:
    build_xml_file()


#Call menu, handle choice
while True:
    user_choice = main_menu()

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
        # Call the function to modify a lot
        modify_lot()
    elif user_choice == '5':
        # Call the function to set time
        set_time()
    elif user_choice == '6':
        break
    else:
        print("Invalid choice. Please try again.")