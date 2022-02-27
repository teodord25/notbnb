# Notbnb
A desktop application written in python that resembles the popular lodging service "Airbnb".

## Functionalities
Functionalities of this application include, but are not strictly limited to:

### For any user (unregistered or otherwise):
- Functional GUI built with PyQt5
- Register and login system with password hashing and salting
- Existing apartment search (filtering) and browsing

### For registered users i.e. "guests":
- Apartment booking and review/cancelling of existing reservations made by the guest

### For registered hosts (apartment owners):
- Apartment adding/editing/deleting (of the apartments owned by the host)
- Review of any active reservations booked in their apartments and cancelling/accepting of these reservations

### For admins:
- Review (and filtering) of all current reservations in the application
- Registration of new hosts
- Creation/deletion of amenities that can be assigned to apartments by the host
- Blocking of users based on their username
- Data listing
 
##### Data listing such as:
- Number of confirmed reservations for a specific date/host,
- Yearly/monthly number of reservations and profit for a specific date/host
- Ratio of reservations per city and total reservations

## Extras
- The "testing" folder includes a .csv file containing autogenerated fake info (courtesy of fakenamegenerator.com)
and a python script that can be used to generate apartments, users, and reservations based on "fake_people.csv".