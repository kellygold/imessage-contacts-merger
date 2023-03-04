import sqlite3
import datetime
import subprocess
import os
import json

def get_chat_mapping(chatdb_location):
    conn = sqlite3.connect(chatdb_location)
    cursor = conn.cursor()

    cursor.execute("SELECT room_name, display_name FROM chat")
    result_set = cursor.fetchall()

    mapping = {room_name: display_name for room_name, display_name in result_set}

    conn.close()

    return mapping
# Function to read messages from a sqlite database
def read_messages(chatdb_location, n, self_number='Me', human_readable_date=True):
    # Connect to the database and execute a query to join message and handle tables
    conn = sqlite3.connect(chatdb_location)
    cursor = conn.cursor()
    query = """
    SELECT message.ROWID, message.date, message.text, message.attributedBody, handle.id, message.is_from_me, message.cache_roomnames
    FROM message
    LEFT JOIN handle ON message.handle_id = handle.ROWID
    """
    if n is not None:
        query += f" ORDER BY message.date DESC LIMIT {n}"
    results = cursor.execute(query).fetchall()
    
    # Initialize an empty list for messages
    messages = []

    # Loop through each result row and unpack variables
    for result in results:
        rowid, date, text, attributed_body, handle_id, is_from_me, cache_roomname = result

        # Use self_number or handle_id as phone_number depending on whether it's a self-message or not
        phone_number = self_number if handle_id is None else handle_id

        # Use text or attributed_body as body depending on whether it's a plain text or rich media message
        if text is not None:
            body = text
        
        elif attributed_body is None: 
            continue
        
        else: 
            # Decode and extract relevant information from attributed_body using string methods 
            attributed_body = attributed_body.decode('utf-8', errors='replace')
            if "NSNumber" in str(attributed_body):
                attributed_body = str(attributed_body).split("NSNumber")[0]
                if "NSString" in attributed_body:
                    attributed_body = str(attributed_body).split("NSString")[1]
                    if "NSDictionary" in attributed_body:
                        attributed_body = str(attributed_body).split("NSDictionary")[0]
                        attributed_body = attributed_body[6:-12]
                        body = attributed_body

        # Convert date from Apple epoch time to standard format using datetime module if human_readable_date is True  
        if human_readable_date:
            date_string = '2001-01-01'
            mod_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
            unix_timestamp = int(mod_date.timestamp())*1000000000
            new_date = int((date+unix_timestamp)/1000000000)
            date = datetime.datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")

        mapping = get_chat_mapping(chatdb_location)  # Get chat mapping from database location

        try:
            mapped_name = mapping[cache_roomname]
        except:
            mapped_name = None

        messages.append(
            {"rowid": rowid, "date": date, "body": body, "phone_number": phone_number, "is_from_me": is_from_me,
             "cache_roomname": cache_roomname, 'group_chat_name' : mapped_name})

    conn.close()
    return messages


def print_messages(messages):
    print(json.dumps(messages))

def get_address_book(address_book_location):
    conn = sqlite3.connect(address_book_location)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT ZABCDRECORD.ZFIRSTNAME [FIRST NAME], ZABCDRECORD.ZLASTNAME [LAST NAME], ZABCDPHONENUMBER.ZFULLNUMBER [FULL NUMBER] FROM ZABCDRECORD LEFT JOIN ZABCDPHONENUMBER ON ZABCDRECORD.Z_PK = ZABCDPHONENUMBER.ZOWNER ORDER BY ZABCDRECORD.ZLASTNAME, ZABCDRECORD.ZFIRSTNAME, ZABCDPHONENUMBER.ZORDERINGINDEX ASC")
    result_set = cursor.fetchall()

    #Convert tuples to json
    json_output = json.dumps([{"FIRSTNAME": t[0], "LASTNAME": t[1], "FULLNUMBER": t[2]} for t in result_set])
    json_list = json.loads(json_output)
    conn.close()

    for obj in json_list:
        # Get the phone number from the object
        phone = obj["FULLNUMBER"]
        if phone is None:
            continue
        # Remove all non-numeric characters from the phone number
        phone = "".join([c for c in phone if c.isnumeric()])
        #if the phone number is 10 digits, add "+1" to the beginning, if it's 11 digits, add "+"
        if len(phone) == 10:
            phone = "+1" + phone
        elif len(phone) == 11:
            phone = "+" + phone
        # Add the phone number to the object
        obj["NUMBERCLEAN"] = phone
        
    new_json_output = json.dumps(json_list)
    return new_json_output

#combine recent messages and address book data
def combine_data(recent_messages, addressBookData):
    #convert addressBookData to a list of dictionaries
    addressBookData = json.loads(addressBookData)
    #loop through each message
    for message in recent_messages:
        phone_number = message["phone_number"]
        for contact in addressBookData:
            # if contact does not have property NUMBERCLEAN, skip it
            if "NUMBERCLEAN" not in contact:
                continue
            else:
                contact_number = contact["NUMBERCLEAN"]
            #if the phone number from the message matches the phone number from the contact add the names to the message
            if phone_number == contact_number:
                message["first_name"] = contact["FIRSTNAME"]
                message["last_name"] = contact["LASTNAME"]
    return recent_messages

# ask the user for the location of the database
chatdb_location = input("Enter the absolute path of the chat database: ")
#chatdb_location = "/Users/<userName>/Library/Messages/chat.db"
# ask the user for the location of the address book database:
address_book_location = input("Enter the absolute path of the address book database : ")
address_book_location = "~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb"
# ask the user for the number of messages to read
n = input("Enter the number of messages to read: ")
recent_messages = read_messages(chatdb_location, n)
#print_messages(recent_messages)
addressBookData = get_address_book(address_book_location)
#print(addressBookData)
combined_data = combine_data(recent_messages, addressBookData)
print_messages(combined_data)
