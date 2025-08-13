from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Aircraft configurations
AIRCRAFT = {
    "Airbus A321": {
        "first_rows": 4,
        "first_seats_per_row": 4, 
        "economy_rows": 22,
        "economy_seats_per_row": 6, 
        "capacity": 144
    },
    "Boeing 737": {
        "first_rows": 3,
        "first_seats_per_row": 4,
        "economy_rows": 21,
        "economy_seats_per_row": 6,
        "capacity": 144
    },
    "Airbus A320": {
        "first_rows": 2,
        "first_seats_per_row": 4,
        "economy_rows": 22,
        "economy_seats_per_row": 6,
        "capacity": 144
    }
}

# Data Layer - In-memory storage with robust sample data
FLIGHTS = {
    "FL001": {
        "flight_number": "AA123",
        "from": "San Francisco",
        "to": "Portland",
        "depart": "2025-03-01 08:45",
        "arrive": "2025-03-01 10:05",
        "aircraft": "Boeing 737",
        "capacity": 144
    },
    "FL002": {
        "flight_number": "UA456", 
        "from": "Portland",
        "to": "Seattle",
        "depart": "2025-03-01 14:30",
        "arrive": "2025-03-01 15:45",
        "aircraft": "Airbus A320",
        "capacity": 144
    },
    "FL003": {
        "flight_number": "DL789",
        "from": "San Francisco",
        "to": "Los Angeles", 
        "depart": "2025-03-01 10:15",
        "arrive": "2025-03-01 11:30",
        "aircraft": "Boeing 737",
        "capacity": 144
    },
    "FL004": {
        "flight_number": "SW234",
        "from": "Los Angeles",
        "to": "Las Vegas",
        "depart": "2025-03-01 16:00",
        "arrive": "2025-03-01 17:15",
        "aircraft": "Boeing 737",
        "capacity": 144
    },
    "FL005": {
        "flight_number": "AS567",
        "from": "Seattle",
        "to": "Anchorage",
        "depart": "2025-03-01 09:00",
        "arrive": "2025-03-01 13:30",
        "aircraft": "Boeing 737",
        "capacity": 144
    },
    "FL006": {
        "flight_number": "HA890",
        "from": "Los Angeles",
        "to": "Honolulu",
        "depart": "2025-03-01 11:00",
        "arrive": "2025-03-01 14:30",
        "aircraft": "Airbus A321",
        "capacity": 144
    }
}

# Initialize seat maps for all flights based on aircraft configuration
def initialize_seat_map(aircraft_type):
    """Initialize seat map based on aircraft configuration"""
    aircraft_config = AIRCRAFT.get(aircraft_type, AIRCRAFT["Boeing 737"])  # Default to Boeing 737
    
    seat_map = {
        "first": {},
        "economy": {}
    }
    
    # Initialize first class seats
    for row in range(1, aircraft_config["first_rows"] + 1):
        for col in ['A', 'B', 'C', 'D']:  # First class has 4 seats per row
            seat_id = f"{row}{col}"
            seat_map["first"][seat_id] = "available"
    
    # Initialize economy class seats
    for row in range(1, aircraft_config["economy_rows"] + 1):
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:  # Economy has 6 seats per row
            seat_id = f"{row}{col}"
            seat_map["economy"][seat_id] = "available"
    
    return seat_map

SEATS = {
    flight_id: initialize_seat_map(FLIGHTS[flight_id]["aircraft"]) 
    for flight_id in FLIGHTS.keys()
}

# Pre-fill some seats as reserved and purchased for more realistic data
def initialize_realistic_seat_data():
    # Flight FL001 - FULLY BOOKED (all seats purchased)
    for seat_class in ["first", "economy"]:
        for seat_id in SEATS["FL001"][seat_class].keys():
            SEATS["FL001"][seat_class][seat_id] = "purchased"
    
    # Flight FL002 - Different pattern
    # First class - mostly purchased
    SEATS["FL002"]["first"]["1A"] = "purchased"
    SEATS["FL002"]["first"]["1B"] = "purchased"
    SEATS["FL002"]["first"]["1C"] = "purchased"
    SEATS["FL002"]["first"]["1D"] = "purchased"
    SEATS["FL002"]["first"]["2A"] = "reserved"
    SEATS["FL002"]["first"]["2B"] = "reserved"
    SEATS["FL002"]["first"]["2C"] = "purchased"
    SEATS["FL002"]["first"]["2D"] = "purchased"
    
    # Economy class - scattered
    SEATS["FL002"]["economy"]["1A"] = "purchased"
    SEATS["FL002"]["economy"]["1B"] = "purchased"
    SEATS["FL002"]["economy"]["2A"] = "reserved"
    SEATS["FL002"]["economy"]["3A"] = "purchased"
    SEATS["FL002"]["economy"]["4A"] = "reserved"
    SEATS["FL002"]["economy"]["5A"] = "purchased"
    SEATS["FL002"]["economy"]["6A"] = "purchased"
    SEATS["FL002"]["economy"]["7A"] = "reserved"
    SEATS["FL002"]["economy"]["8A"] = "purchased"
    SEATS["FL002"]["economy"]["9A"] = "reserved"
    SEATS["FL002"]["economy"]["10A"] = "purchased"
    SEATS["FL002"]["economy"]["11A"] = "reserved"
    SEATS["FL002"]["economy"]["12A"] = "purchased"
    
    # Flight FL003 - More sparse
    SEATS["FL003"]["first"]["1A"] = "purchased"
    SEATS["FL003"]["first"]["2A"] = "reserved"
    SEATS["FL003"]["economy"]["1A"] = "purchased"
    SEATS["FL003"]["economy"]["3A"] = "reserved"
    SEATS["FL003"]["economy"]["5A"] = "purchased"
    SEATS["FL003"]["economy"]["7A"] = "reserved"
    SEATS["FL003"]["economy"]["9A"] = "purchased"
    SEATS["FL003"]["economy"]["11A"] = "reserved"
    SEATS["FL003"]["economy"]["13A"] = "purchased"
    SEATS["FL003"]["economy"]["15A"] = "reserved"
    SEATS["FL003"]["economy"]["17A"] = "purchased"
    SEATS["FL003"]["economy"]["19A"] = "reserved"
    SEATS["FL003"]["economy"]["21A"] = "purchased"
    
    # Flight FL004 - Mostly empty
    SEATS["FL004"]["first"]["1A"] = "purchased"
    SEATS["FL004"]["economy"]["1A"] = "purchased"
    SEATS["FL004"]["economy"]["2A"] = "reserved"
    SEATS["FL004"]["economy"]["3A"] = "purchased"
    
    # Flight FL005 - Some premium seats taken
    SEATS["FL005"]["first"]["1A"] = "purchased"
    SEATS["FL005"]["first"]["1B"] = "purchased"
    SEATS["FL005"]["first"]["1C"] = "purchased"
    SEATS["FL005"]["first"]["1D"] = "purchased"
    SEATS["FL005"]["first"]["2A"] = "reserved"
    SEATS["FL005"]["first"]["2B"] = "reserved"
    SEATS["FL005"]["first"]["2C"] = "purchased"
    SEATS["FL005"]["first"]["2D"] = "purchased"
    SEATS["FL005"]["first"]["3A"] = "reserved"
    SEATS["FL005"]["economy"]["1A"] = "purchased"
    SEATS["FL005"]["economy"]["2A"] = "reserved"
    SEATS["FL005"]["economy"]["3A"] = "purchased"
    SEATS["FL005"]["economy"]["4A"] = "reserved"
    SEATS["FL005"]["economy"]["5A"] = "purchased"
    SEATS["FL005"]["economy"]["6A"] = "reserved"
    
    # Flight FL006 - Popular route
    # First class - mostly taken
    for row in range(1, 3):  # First 2 rows mostly taken
        for col in ['A', 'B', 'C', 'D']:
            seat_id = f"{row}{col}"
            if row % 2 == 0:  # Even rows reserved
                SEATS["FL006"]["first"][seat_id] = "reserved"
            else:  # Odd rows purchased
                SEATS["FL006"]["first"][seat_id] = "purchased"
    
    # Economy class - high occupancy in first rows
    for row in range(1, 8):  # First 7 rows mostly taken
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_id = f"{row}{col}"
            if row % 2 == 0:  # Even rows reserved
                SEATS["FL006"]["economy"][seat_id] = "reserved"
            else:  # Odd rows purchased
                SEATS["FL006"]["economy"][seat_id] = "purchased"
    
    # Some scattered seats in later rows
    SEATS["FL006"]["economy"]["10A"] = "purchased"
    SEATS["FL006"]["economy"]["12A"] = "reserved"
    SEATS["FL006"]["economy"]["15A"] = "purchased"
    SEATS["FL006"]["economy"]["18A"] = "reserved"
    SEATS["FL006"]["economy"]["20A"] = "purchased"
    SEATS["FL006"]["economy"]["22A"] = "reserved"
    SEATS["FL006"]["economy"]["24A"] = "purchased"

# Initialize realistic seat data
initialize_realistic_seat_data()

# Pre-create some reservations and purchases
RESERVATIONS = {
    "RES004": {
        "flight_id": "FL002",
        "user_id": "U201",
        "seats": ["2A"],
        "seat_class": "first",
        "expires": datetime.now() + timedelta(minutes=15)
    },
    "RES005": {
        "flight_id": "FL002",
        "user_id": "U202",
        "seats": ["4A", "4B"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=5)
    },
    "RES006": {
        "flight_id": "FL003",
        "user_id": "U301",
        "seats": ["3A"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=20)
    },
    "RES007": {
        "flight_id": "FL003",
        "user_id": "U302",
        "seats": ["7A"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=3)
    },
    "RES008": {
        "flight_id": "FL004",
        "user_id": "U401",
        "seats": ["2A"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=18)
    },
    "RES009": {
        "flight_id": "FL005",
        "user_id": "U501",
        "seats": ["2A", "2B"],
        "seat_class": "first",
        "expires": datetime.now() + timedelta(minutes=7)
    },
    "RES010": {
        "flight_id": "FL005",
        "user_id": "U502",
        "seats": ["4A"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=14)
    },
    "RES011": {
        "flight_id": "FL006",
        "user_id": "U601",
        "seats": ["12A"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=9)
    },
    "RES012": {
        "flight_id": "FL006",
        "user_id": "U602",
        "seats": ["18A"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=11)
    },
    "RES013": {
        "flight_id": "FL006",
        "user_id": "U603",
        "seats": ["22A"],
        "seat_class": "economy",
        "expires": datetime.now() + timedelta(minutes=6)
    }
}

PURCHASES = {
    # FL001 - All seats purchased (144 seats total, 24 users)
    "PUR001": {
        "flight_id": "FL001",
        "user_id": "U001",
        "seats": ["1A", "1B", "1C", "1D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=2)
    },
    "PUR002": {
        "flight_id": "FL001",
        "user_id": "U002", 
        "seats": ["2A", "2B", "2C", "2D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=1)
    },
    "PUR003": {
        "flight_id": "FL001",
        "user_id": "U003",
        "seats": ["3A", "3B", "3C", "3D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(minutes=30)
    },
    "PUR004": {
        "flight_id": "FL001",
        "user_id": "U004",
        "seats": ["1A", "1B", "1C", "1D", "1E", "1F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=45)
    },
    "PUR005": {
        "flight_id": "FL001",
        "user_id": "U005",
        "seats": ["2A", "2B", "2C", "2D", "2E", "2F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(hours=3)
    },
    "PUR006": {
        "flight_id": "FL001",
        "user_id": "U006",
        "seats": ["3A", "3B", "3C", "3D", "3E", "3F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(hours=1, minutes=30)
    },
    "PUR007": {
        "flight_id": "FL001",
        "user_id": "U007",
        "seats": ["4A", "4B", "4C", "4D", "4E", "4F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=15)
    },
    "PUR008": {
        "flight_id": "FL001",
        "user_id": "U008",
        "seats": ["5A", "5B", "5C", "5D", "5E", "5F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=20)
    },
    "PUR009": {
        "flight_id": "FL001",
        "user_id": "U009",
        "seats": ["6A", "6B", "6C", "6D", "6E", "6F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=25)
    },
    "PUR010": {
        "flight_id": "FL001",
        "user_id": "U010",
        "seats": ["7A", "7B", "7C", "7D", "7E", "7F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=35)
    },
    "PUR011": {
        "flight_id": "FL001",
        "user_id": "U011",
        "seats": ["8A", "8B", "8C", "8D", "8E", "8F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=40)
    },
    "PUR012": {
        "flight_id": "FL001",
        "user_id": "U012",
        "seats": ["9A", "9B", "9C", "9D", "9E", "9F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=50)
    },
    "PUR013": {
        "flight_id": "FL001",
        "user_id": "U013",
        "seats": ["10A", "10B", "10C", "10D", "10E", "10F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=55)
    },
    "PUR014": {
        "flight_id": "FL001",
        "user_id": "U014",
        "seats": ["11A", "11B", "11C", "11D", "11E", "11F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=60)
    },
    "PUR015": {
        "flight_id": "FL001",
        "user_id": "U015",
        "seats": ["12A", "12B", "12C", "12D", "12E", "12F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=65)
    },
    "PUR016": {
        "flight_id": "FL001",
        "user_id": "U016",
        "seats": ["13A", "13B", "13C", "13D", "13E", "13F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=70)
    },
    "PUR017": {
        "flight_id": "FL001",
        "user_id": "U017",
        "seats": ["14A", "14B", "14C", "14D", "14E", "14F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=75)
    },
    "PUR018": {
        "flight_id": "FL001",
        "user_id": "U018",
        "seats": ["15A", "15B", "15C", "15D", "15E", "15F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=80)
    },
    "PUR019": {
        "flight_id": "FL001",
        "user_id": "U019",
        "seats": ["16A", "16B", "16C", "16D", "16E", "16F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=85)
    },
    "PUR020": {
        "flight_id": "FL001",
        "user_id": "U020",
        "seats": ["17A", "17B", "17C", "17D", "17E", "17F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=90)
    },
    "PUR021": {
        "flight_id": "FL001",
        "user_id": "U021",
        "seats": ["18A", "18B", "18C", "18D", "18E", "18F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=95)
    },
    "PUR022": {
        "flight_id": "FL001",
        "user_id": "U022",
        "seats": ["19A", "19B", "19C", "19D", "19E", "19F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=100)
    },
    "PUR023": {
        "flight_id": "FL001",
        "user_id": "U023",
        "seats": ["20A", "20B", "20C", "20D", "20E", "20F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=105)
    },
    "PUR024": {
        "flight_id": "FL001",
        "user_id": "U024",
        "seats": ["21A", "21B", "21C", "21D", "21E", "21F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=110)
    },
    # FL002 - Original pattern
    "PUR025": {
        "flight_id": "FL002",
        "user_id": "U101",
        "seats": ["1A", "1B", "1C", "1D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=2)
    },
    "PUR026": {
        "flight_id": "FL002",
        "user_id": "U102",
        "seats": ["2C", "2D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=1)
    },
    "PUR027": {
        "flight_id": "FL002",
        "user_id": "U103",
        "seats": ["1A", "1B"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=45)
    },
    "PUR028": {
        "flight_id": "FL002",
        "user_id": "U104",
        "seats": ["3A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=30)
    },
    "PUR029": {
        "flight_id": "FL002",
        "user_id": "U105",
        "seats": ["5A", "5B"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(hours=1, minutes=15)
    },
    "PUR030": {
        "flight_id": "FL002",
        "user_id": "U106",
        "seats": ["6A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=20)
    },
    "PUR031": {
        "flight_id": "FL002",
        "user_id": "U107",
        "seats": ["8A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=10)
    },
    "PUR032": {
        "flight_id": "FL003",
        "user_id": "U201",
        "seats": ["1A"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=3)
    },
    "PUR033": {
        "flight_id": "FL003",
        "user_id": "U202",
        "seats": ["1A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(hours=2)
    },
    "PUR034": {
        "flight_id": "FL003",
        "user_id": "U203",
        "seats": ["5A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(hours=1)
    },
    "PUR035": {
        "flight_id": "FL003",
        "user_id": "U204",
        "seats": ["9A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=45)
    },
    "PUR036": {
        "flight_id": "FL003",
        "user_id": "U205",
        "seats": ["13A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=30)
    },
    "PUR037": {
        "flight_id": "FL003",
        "user_id": "U206",
        "seats": ["17A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=15)
    },
    "PUR038": {
        "flight_id": "FL004",
        "user_id": "U301",
        "seats": ["1A"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=1)
    },
    "PUR039": {
        "flight_id": "FL004",
        "user_id": "U302",
        "seats": ["1A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=30)
    },
    "PUR040": {
        "flight_id": "FL004",
        "user_id": "U303",
        "seats": ["3A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=15)
    },
    "PUR041": {
        "flight_id": "FL005",
        "user_id": "U401",
        "seats": ["1A", "1B", "1C", "1D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=2)
    },
    "PUR042": {
        "flight_id": "FL005",
        "user_id": "U402",
        "seats": ["2C", "2D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=1)
    },
    "PUR043": {
        "flight_id": "FL005",
        "user_id": "U403",
        "seats": ["1A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=45)
    },
    "PUR044": {
        "flight_id": "FL006",
        "user_id": "U501",
        "seats": ["1A", "1B", "1C", "1D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=3)
    },
    "PUR045": {
        "flight_id": "FL006",
        "user_id": "U502",
        "seats": ["2A", "2B", "2C", "2D"],
        "seat_class": "first",
        "purchased_at": datetime.now() - timedelta(hours=2)
    },
    "PUR046": {
        "flight_id": "FL006",
        "user_id": "U503",
        "seats": ["1A", "1B", "1C", "1D", "1E", "1F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(hours=1)
    },
    "PUR047": {
        "flight_id": "FL006",
        "user_id": "U504",
        "seats": ["3A", "3B", "3C", "3D", "3E", "3F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=30)
    },
    "PUR048": {
        "flight_id": "FL006",
        "user_id": "U505",
        "seats": ["5A", "5B", "5C", "5D", "5E", "5F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=15)
    },
    "PUR049": {
        "flight_id": "FL006",
        "user_id": "U506",
        "seats": ["7A", "7B", "7C", "7D", "7E", "7F"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=10)
    },
    "PUR050": {
        "flight_id": "FL006",
        "user_id": "U507",
        "seats": ["10A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=5)
    },
    "PUR051": {
        "flight_id": "FL006",
        "user_id": "U508",
        "seats": ["15A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=2)
    },
    "PUR052": {
        "flight_id": "FL006",
        "user_id": "U509",
        "seats": ["20A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=1)
    },
    "PUR053": {
        "flight_id": "FL006",
        "user_id": "U510",
        "seats": ["24A"],
        "seat_class": "economy",
        "purchased_at": datetime.now() - timedelta(minutes=30)
    }
}

# Helper Functions
def generate_reservation_id():
    return str(uuid.uuid4())

def generate_purchase_id():
    return str(uuid.uuid4())

def is_seat_available(flight_id, seat_id, seat_class):
    return SEATS.get(flight_id, {}).get(seat_class, {}).get(seat_id) == "available"

def mark_seats_status(flight_id, seat_ids, status, seat_class):
    for seat_id in seat_ids:
        if flight_id in SEATS and seat_class in SEATS[flight_id] and seat_id in SEATS[flight_id][seat_class]:
            SEATS[flight_id][seat_class][seat_id] = status

def get_expired_reservations():
    current_time = datetime.now()
    expired = []
    for reservation_id, reservation in RESERVATIONS.items():
        if reservation["expires"] < current_time:
            expired.append(reservation_id)
    return expired

def cleanup_expired_reservations():
    expired = get_expired_reservations()
    for reservation_id in expired:
        reservation = RESERVATIONS[reservation_id]
        mark_seats_status(reservation["flight_id"], reservation["seats"], "available", reservation["seat_class"])
        del RESERVATIONS[reservation_id]

# Endpoint 1: Search for flights
@app.route('/flights/search', methods=['POST'])
def search_flights():
    cleanup_expired_reservations()
    
    data = request.get_json()
    from_city = data.get('from', '').lower()
    to_city = data.get('to', '').lower()
    depart_date = data.get('depart_date', '')
    seat_class = data.get('class', '').lower()  # New parameter for seat class
    
    matching_flights = []
    
    for flight_id, flight in FLIGHTS.items():
        # Check if flight matches search criteria
        matches_from = not from_city or flight['from'].lower() == from_city
        matches_to = not to_city or flight['to'].lower() == to_city
        matches_date = not depart_date or flight['depart'].startswith(depart_date)
        
        if matches_from and matches_to and matches_date:
            # Add seat class availability info
            flight_info = {
                "flight_id": flight_id,
                **flight
            }
            
            # Add seat class availability if requested
            if seat_class:
                if seat_class in ["first", "economy"]:
                    available_seats = []
                    seat_map = SEATS.get(flight_id, {}).get(seat_class, {})
                    for seat_id, status in seat_map.items():
                        if status == "available":
                            available_seats.append(seat_id)
                    
                    flight_info[f"{seat_class}_available"] = len(available_seats)
                    flight_info[f"{seat_class}_total"] = len(seat_map)
                else:
                    # Invalid seat class, skip this flight
                    continue
            
            matching_flights.append(flight_info)
    
    return jsonify({
        "flights": matching_flights,
        "count": len(matching_flights)
    })

# Endpoint 2: View available seats for a specific flight
@app.route('/flights/<flight_id>/seats', methods=['GET'])
def view_available_seats(flight_id):
    cleanup_expired_reservations()
    
    if flight_id not in FLIGHTS:
        return jsonify({"error": "Flight not found"}), 404
    
    seat_class = request.args.get('class', '').lower()  # Optional seat class filter
    
    available_seats = {
        "first": [],
        "economy": []
    }
    
    seat_map = SEATS.get(flight_id, {})
    
    if seat_class and seat_class in ["first", "economy"]:
        # Return only requested seat class
        for seat_id, status in seat_map.get(seat_class, {}).items():
            if status == "available":
                available_seats[seat_class].append(seat_id)
        
        return jsonify({
            "flight_id": flight_id,
            "seat_class": seat_class,
            "available_seats": available_seats[seat_class],
            "total_available": len(available_seats[seat_class]),
            "total_seats": len(seat_map.get(seat_class, {}))
        })
    else:
        # Return all seat classes
        for class_type in ["first", "economy"]:
            for seat_id, status in seat_map.get(class_type, {}).items():
                if status == "available":
                    available_seats[class_type].append(seat_id)
        
        total_available = len(available_seats["first"]) + len(available_seats["economy"])
        total_seats = len(seat_map.get("first", {})) + len(seat_map.get("economy", {}))
        
        return jsonify({
            "flight_id": flight_id,
            "first_class": {
                "available_seats": available_seats["first"],
                "total_available": len(available_seats["first"]),
                "total_seats": len(seat_map.get("first", {}))
            },
            "economy_class": {
                "available_seats": available_seats["economy"],
                "total_available": len(available_seats["economy"]),
                "total_seats": len(seat_map.get("economy", {}))
            },
            "total_available": total_available,
            "total_seats": total_seats
        })

# Endpoint 3: Reserve seats
@app.route('/flights/<flight_id>/reserve', methods=['POST'])
def reserve_seats(flight_id):
    cleanup_expired_reservations()
    
    if flight_id not in FLIGHTS:
        return jsonify({"error": "Flight not found"}), 404
    
    data = request.get_json()
    seat_ids = data.get('seat_ids', [])
    user_id = data.get('user_id')
    seat_class = data.get('seat_class', 'economy').lower()  # Default to economy
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    if not seat_ids:
        return jsonify({"error": "seat_ids is required"}), 400
    
    if seat_class not in ["first", "economy"]:
        return jsonify({"error": "seat_class must be 'first' or 'economy'"}), 400
    
    # Check if all seats are available
    unavailable_seats = []
    for seat_id in seat_ids:
        if not is_seat_available(flight_id, seat_id, seat_class):
            unavailable_seats.append(seat_id)
    
    if unavailable_seats:
        return jsonify({
            "error": "Some seats are not available",
            "unavailable_seats": unavailable_seats
        }), 400
    
    # Create reservation (expires in 15 minutes)
    reservation_id = generate_reservation_id()
    expires_at = datetime.now() + timedelta(minutes=15)
    
    RESERVATIONS[reservation_id] = {
        "flight_id": flight_id,
        "user_id": user_id,
        "seats": seat_ids,
        "seat_class": seat_class,
        "expires": expires_at
    }
    
    # Mark seats as reserved
    mark_seats_status(flight_id, seat_ids, "reserved", seat_class)
    
    return jsonify({
        "reservation_id": reservation_id,
        "flight_id": flight_id,
        "seat_class": seat_class,
        "seats": seat_ids,
        "expires_at": expires_at.isoformat(),
        "message": f"Reserved {len(seat_ids)} {seat_class} seat(s) for 15 minutes"
    })

# Endpoint 4: Purchase reserved seats
@app.route('/flights/<flight_id>/purchase', methods=['POST'])
def purchase_seats(flight_id):
    cleanup_expired_reservations()
    
    if flight_id not in FLIGHTS:
        return jsonify({"error": "Flight not found"}), 404
    
    data = request.get_json()
    reservation_id = data.get('reservation_id')
    user_id = data.get('user_id')
    
    if not reservation_id or not user_id:
        return jsonify({"error": "reservation_id and user_id are required"}), 400
    
    # Check if reservation exists and belongs to user
    if reservation_id not in RESERVATIONS:
        return jsonify({"error": "Reservation not found"}), 404
    
    reservation = RESERVATIONS[reservation_id]
    if reservation["flight_id"] != flight_id or reservation["user_id"] != user_id:
        return jsonify({"error": "Invalid reservation"}), 400
    
    if reservation["expires"] < datetime.now():
        return jsonify({"error": "Reservation has expired"}), 400
    
    # Create purchase
    purchase_id = generate_purchase_id()
    purchased_at = datetime.now()
    
    PURCHASES[purchase_id] = {
        "flight_id": flight_id,
        "user_id": user_id,
        "seats": reservation["seats"],
        "seat_class": reservation["seat_class"],
        "purchased_at": purchased_at
    }
    
    # Mark seats as purchased
    mark_seats_status(flight_id, reservation["seats"], "purchased", reservation["seat_class"])
    
    # Remove reservation
    del RESERVATIONS[reservation_id]
    
    return jsonify({
        "purchase_id": purchase_id,
        "flight_id": flight_id,
        "seat_class": reservation["seat_class"],
        "seats": reservation["seats"],
        "purchased_at": purchased_at.isoformat(),
        "message": f"Successfully purchased {len(reservation['seats'])} {reservation['seat_class']} seat(s)"
    })

# Endpoint 5: Cancel purchased seats
@app.route('/flights/<flight_id>/cancel', methods=['POST'])
def cancel_purchase(flight_id):
    cleanup_expired_reservations()
    
    if flight_id not in FLIGHTS:
        return jsonify({"error": "Flight not found"}), 404
    
    data = request.get_json()
    purchase_id = data.get('purchase_id')
    user_id = data.get('user_id')
    
    if not purchase_id or not user_id:
        return jsonify({"error": "purchase_id and user_id are required"}), 400
    
    # Check if purchase exists and belongs to user
    if purchase_id not in PURCHASES:
        return jsonify({"error": "Purchase not found"}), 404
    
    purchase = PURCHASES[purchase_id]
    if purchase["flight_id"] != flight_id or purchase["user_id"] != user_id:
        return jsonify({"error": "Invalid purchase"}), 400
    
    # Mark seats as available again
    mark_seats_status(flight_id, purchase["seats"], "available", purchase["seat_class"])
    
    # Remove purchase
    del PURCHASES[purchase_id]
    
    return jsonify({
        "purchase_id": purchase_id,
        "flight_id": flight_id,
        "seat_class": purchase["seat_class"],
        "seats": purchase["seats"],
        "message": f"Successfully cancelled {len(purchase['seats'])} {purchase['seat_class']} seat(s)"
    })

# Additional endpoint to get all flights (for testing)
@app.route('/flights', methods=['GET'])
def get_all_flights():
    cleanup_expired_reservations()
    
    flights_list = []
    for flight_id, flight in FLIGHTS.items():
        flights_list.append({
            "flight_id": flight_id,
            **flight
        })
    
    return jsonify({
        "flights": flights_list,
        "count": len(flights_list)
    })

# Endpoint to get current reservations and purchases (for debugging)
@app.route('/debug/state', methods=['GET'])
def get_debug_state():
    cleanup_expired_reservations()
    
    return jsonify({
        "reservations": RESERVATIONS,
        "purchases": PURCHASES,
        "seats": SEATS
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

