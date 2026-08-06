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

def to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def print_lot_schedule(lot_id):
    data = ET.parse("data.xml")
    root = data.getroot().find("lots")
    lot = root.find(f"lot[@id='{lot_id}']")
    bookings = lot.find("bookings").findall("booking")
    if not bookings:
        print(f"Lot {lot_id} has no bookings.")
    else:
        print(f"Lot {lot_id} has the following bookings:")
        for booking in bookings:
            print(f"({booking.get('arrival')}-{booking.get('departure')}) ({booking.get('plate')})")

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
    print("3. Confirm changes")
    print("4. Cancel changes")

    choice = input("Enter your choice (1-4): ")
    return choice
    
def list_menu():
    print("1. List all lots")
    print("2. List lots by floor")
    print("3. List lots by availability")
    print("4. Back to main menu")

    choice = input("Enter your choice (1-4): ")
    return choice

#book lot function
def book_lot():
    data = ET.parse("data.xml")
    root = data.getroot().find("lots")
    plate = input("Enter your license plate number: ")
    #Plate format validation ABC-123
    if not plate.replace("-", "").replace(" ", "").isalnum() or len(plate.replace("-", "").replace(" ", "")) != 6:
        print("Invalid license plate format. Please enter a valid license plate (ABC-123).")
        book_lot()
        return
    lot_id = input("Enter the lot ID you want to book: ")
    lots = root.findall("lot")
    lot = root.find(f"lot[@id='{lot_id}']")
    
    if lot is None:
        print(f"Lot {lot_id} does not exist.")
        book_lot()
        return
    if lot.get("id") == lot_id:
        if lot.get("disabled") == "true":
            allowed = input(f"Lot {lot_id} is a handicapped lot, are you allowed to park here? (y/n): ")
            if allowed.lower() != "y":
                print("You are not allowed to book this lot.")
                book_lot()
        print_lot_schedule(lot_id)             
    print("Make sure departure time is later than arrival time and does not overlap with existing bookings in the same lot.")
    arrival = input("Enter the arrival time (HH:MM): ")
    departure = input("Enter the departure time (HH:MM): ")
    # Validate the arrival and departure times
    try:
        arrival_hours, arrival_minutes = map(int, arrival.split(':'))
        departure_hours, departure_minutes = map(int, departure.split(':'))
        if not (0 <= arrival_hours < 24 and 0 <= arrival_minutes < 60 and
                0 <= departure_hours < 24 and 0 <= departure_minutes < 60):
            print("Invalid time format. Please enter valid times.")
            book_lot()
        if to_minutes(arrival) >= to_minutes(departure):
            print("Departure time must be later than arrival time and no overnight parking! >:(")
            book_lot()
            return
    except ValueError:
        print("Invalid input. Please enter time in HH:MM format.")
        book_lot()
    #Check if reservation times overlap with existing bookings in the lot
    bookings = lot.find("bookings").findall("booking")
    overlap = False
    for booking in bookings:
        booking_arrival = booking.get("arrival")
        booking_departure = booking.get("departure")
        if to_minutes(arrival) < to_minutes(booking_departure) and to_minutes(departure) > to_minutes(booking_arrival):
            overlap = True
            break
    if overlap:
        print("Reservation times overlap with existing bookings in this lot, change reservation times or select a different lot.")
        book_lot()
        return
    # Get the next booking ID
    meta = data.getroot().find("meta")
    next_id_element = meta.find("next_booking_id")
    booking_id = next_id_element.text
    new_booking = ET.SubElement(lot.find("bookings"), "booking", id=booking_id, plate=plate, arrival=arrival, departure=departure)
    next_id_element.text = str(int(booking_id) + 1)   # increment for next time
    ET.indent(data, space="\t", level=0)
    data.write("data.xml")

#list lots function
def list_lots():
    data = ET.parse("data.xml")
    root = data.getroot().find("lots")
    lots = root.findall("lot")
    list_choice = list_menu()
    if list_choice == "1":
        for lot in lots:
            print(f"Lot: {lot.get('id')}")
    elif list_choice == "2":
        floor = input("Enter the floor (A, B, C, D): ")
        for lot in lots:
            if lot.get("id").startswith(floor):
                print(f"Lot: {lot.get('id')}")
    elif list_choice == "3":  #checks current time against lot schedules
        current_time = data.getroot().find("meta").find("current_time").text
        print(f"Current time: {current_time}")
        for lot in lots:
            bookings = lot.find("bookings").findall("booking")
            is_available = True
            for booking in bookings:
                if to_minutes(booking.get("arrival")) <= to_minutes(current_time) < to_minutes(booking.get("departure")):
                    is_available = False
                    break
            if (is_available):
                print(f"Lot: {lot.get('id')} Available.")
            else:
                print(f"Lot: {lot.get('id')} Not Available.")
    elif list_choice == "4":
        return
    check = input("Would you like to check the schedule of a specific lot? (y/n): ")
    if check.lower() == "y":
        lot_id = input("Enter the lot ID to check the schedule: ")
        print_lot_schedule(lot_id)
    

#remove reservation function
def remove_reservation():
    booking_id = input("Enter the ID of your booking you'd like to remove: ")
    data = ET.parse("data.xml")
    root = data.getroot().find("lots")
    lots = root.findall("lot")
    for lot in lots:
        for booking in lot.find("bookings").findall("booking"):
            if booking.get("id") == booking_id:
                print(f"Booking {booking_id} => Lot: {lot.get('id')}, Plate: {booking.get('plate')}, "
                    f"Reservation: ({booking.get('arrival')}-{booking.get('departure')})")
                confirm = input("Delete this booking? (y/n): ")
                if confirm.lower() != "y":
                    print("Cancelled.")
                    return
                lot.find("bookings").remove(booking)
                ET.indent(data, space="\t", level=0)
                data.write("data.xml")
                print(f"Booking {booking_id} removed.")
                return
    print(f"Booking ID {booking_id} not found.")

#modify lot function
def modify_lot():
    booking_id = input("Enter the booking ID to of the booking you are looking to modify: ")
    data = ET.parse("data.xml")
    root = data.getroot().find("lots")
    lots = root.findall("lot")
    
    for lot in lots:
        for booking in lot.find("bookings").findall("booking"):
            if booking.get("id") == booking_id:
                booking_lot_id = lot.get("id")
                booking_plate = booking.get("plate")
                booking_arrival = booking.get("arrival")
                booking_departure = booking.get("departure")
                new_lot = lot
                new_lot_id = booking_lot_id
                new_arrival = booking_arrival
                new_departure = booking_departure
                print(f"{booking_id} => Lot: {booking_lot_id}, Plate: {booking_plate}, Reservation: ({booking_arrival}-{booking_departure})")
                done = False
                overlap = False
                while not done:   
                    modify_choice = modify_menu()
                    if modify_choice == "1":
                        tmp = input("Enter the new lot ID: ")
                        # Check if the new lot ID exists
                        new_lot = root.find(f"lot[@id='{tmp}']")
                        if new_lot is None:
                            print(f"Lot {tmp} does not exist.")
                            continue
                        # Check if the new lot is disabled
                        if new_lot.get("disabled") == "true":
                            allowed = input(f"Lot {tmp} is a handicapped lot, are you allowed to park here? (y/n): ")
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
                            if to_minutes(tmp_arrival) >= to_minutes(tmp_departure):
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
                        # Update the booking information
                        if not overlap:
                            # Remove the booking from the old lot
                            lot.find("bookings").remove(booking)
                            # Add the booking to the new lot
                            new_lot = root.find(f"lot[@id='{new_lot_id}']")
                            new_booking = ET.SubElement(new_lot.find("bookings"), "booking", id=booking_id, plate=booking_plate, arrival=new_arrival, departure=new_departure)
                            done = True                
                    elif modify_choice == "4":
                        return

                    #Check if reservation times overlap with existing bookings in the new lot
                    new_lot_bookings = new_lot.find("bookings").findall("booking")
                    overlap = False
                    for new_booking in new_lot_bookings:
                        if new_booking.get("id") == booking_id:
                            continue  # this is the booking we're modifying, not a real collision
                        new_booking_arrival = new_booking.get("arrival")
                        new_booking_departure = new_booking.get("departure")
                        if to_minutes(new_arrival) < to_minutes(new_booking_departure) and to_minutes(new_departure) > to_minutes(new_booking_arrival):
                            overlap = True
                            break
                    if overlap:
                        print(f"Reservation times overlap with existing bookings in lot {new_lot_id}, change reservation times or select a different lot.")
                    
                ET.indent(data, space="\t", level=0)
                data.write("data.xml")
                print(f"Booking {booking_id} modified to lot {new_lot_id}, reservation times: {new_arrival}-{new_departure}.")
                break
        else:
            continue
        break

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