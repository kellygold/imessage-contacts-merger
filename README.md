# imessage-contacts-merger-macos

This Python script is designed to read messages from an SQLite database in Apple's Messages app. It allows the user to specify the location of the chat database, the address book database, and the number of messages to read.

## Requirements

- Python 3.0 or later
- SQLite3

## Usage
1. Open the terminal or command prompt on your computer.
2. Navigate to the directory where the script is located.
3. Run the script using the following command: `python messages_reader.py`
4. When prompted, enter the location of the chat database. The default location is `/Users/userName/Library/Messages/chat.db`
5. When prompted, enter the location of the address book database. The default location is `/Library/"Application Support"/AddressBook/Sources/*/AddressBook-v22.abcddb`
6. When prompted, enter the number of messages to read.
7. The script will output a JSON-formatted list of messages and a JSON-formatted list of phone numbers and contact information.


## Functions

The script contains the following functions:

### `get_chat_mapping(chatdb_location)`
This function connects to the specified chat database and returns a mapping of room names to display names.

### `read_messages(chatdb_location, n, self_number='Me', human_readable_date=True)`

This function connects to the specified chat database and retrieves the specified number of messages. It returns a list of dictionaries, where each dictionary represents a message and contains the following keys:

- "rowid": the unique identifier for the message
- "date": the date and time the message was sent or received
- "body": the text of the message
- "phone_number": the phone number associated with the message
- "is_from_me": a boolean indicating whether the message was sent or received
- "cache_roomname": the room name associated with the message
- "group_chat_name": the display name of the group chat, if applicable

### `print_messages(messages)`

This function takes a list of messages in dictionary format and prints them in JSON format to the console.

### `get_address_book(address_book_location)`
This function connects to the specified address book database and returns a list of dictionaries representing each contact in the address book. Each dictionary contains the following keys:

- "FIRST NAME": the first name of the contact
- "LAST NAME": the last name of the contact
- "FULL NUMBER": the phone number associated with the contact
- "NUMBERCLEAN": the cleaned phone number associated with the contact

## Example
Here's an example of how to use the script:

```
python conversation_data.py
Enter the location of the chat database: /Users/myusername/Library/Messages/chat.db
Enter the location of the address book database: /Users/myusername/Desktop/AddressBook.abcddb
Enter the number of messages to read: 50
```

The script will output a JSON-formatted list of the 50 most recent messages and a JSON-formatted list of phone numbers and contact information.















