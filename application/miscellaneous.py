from file_reader import read_json_file

# Indian states
states = [
    'All',
    'Andhra Pradesh',
    'Assam',
    'Bihar',
    'Chandigarh',
    'Chattisgarh',
    'Goa',
    'Gujarat',
    'Haryana',
    'Himachal Pradesh',
    'Jammu and Kashmir',
    'Jharkhand',
    'Karnataka',
    'Kerala',
    'Madhya Pradesh',
    'Maharashtra',
    'Manipur',
    'Mizoram',
    'NCT of Delhi',
    'Nagaland',
    'Odisha',
    'Pondicherry',
    'Punjab',
    'Rajasthan',
    'Tamil Nadu',
    'Telangana',
    'Tripura',
    'Uttar Pradesh',
    'Uttrakhand',
    'West Bengal'
]


# Train Stations (from_ and to_)
stations_to_from = read_json_file(file_name='stations_to_from.json')
from_stations = list(set(stations_to_from['from_stations']))