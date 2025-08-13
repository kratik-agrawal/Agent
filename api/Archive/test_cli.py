#!/usr/bin/env python3
"""
CLI Testing Script for Airline Reservation System
Usage: python test_cli.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def make_request(method, endpoint, data=None):
    """Helper function to make HTTP requests"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running on localhost:5000")
        return None, None

def test_search_flights():
    """Test flight search functionality"""
    print("\n🔍 Testing Flight Search...")
    
    # Test 1: Search all flights
    print("\n1. Searching all flights:")
    response, status = make_request("POST", "/flights/search", {})
    if status == 200:
        print(f"✅ Found {response['count']} flights")
        for flight in response['flights']:
            print(f"   - {flight['flight_number']} ({flight['flight_id']}): {flight['from']} → {flight['to']} ({flight['depart']})")
    
    # Test 2: Search by departure city
    print("\n2. Searching flights from San Francisco:")
    response, status = make_request("POST", "/flights/search", {"from": "San Francisco"})
    if status == 200:
        print(f"✅ Found {response['count']} flights from San Francisco")
        for flight in response['flights']:
            print(f"   - {flight['flight_number']} ({flight['flight_id']}): {flight['from']} → {flight['to']}")
    
    # Test 3: Search by arrival city
    print("\n3. Searching flights to Portland:")
    response, status = make_request("POST", "/flights/search", {"to": "Portland"})
    if status == 200:
        print(f"✅ Found {response['count']} flights to Portland")
        for flight in response['flights']:
            print(f"   - {flight['flight_number']} ({flight['flight_id']}): {flight['from']} → {flight['to']}")
    
    # Test 4: Search by date
    print("\n4. Searching flights on 2025-03-01:")
    response, status = make_request("POST", "/flights/search", {"depart_date": "2025-03-01"})
    if status == 200:
        print(f"✅ Found {response['count']} flights on 2025-03-01")
        for flight in response['flights']:
            print(f"   - {flight['flight_number']} ({flight['flight_id']}): {flight['from']} → {flight['to']}")
    
    # Test 5: Search by seat class (first class)
    print("\n5. Searching flights with first class availability:")
    response, status = make_request("POST", "/flights/search", {"class": "first"})
    if status == 200:
        print(f"✅ Found {response['count']} flights with first class")
        for flight in response['flights']:
            print(f"   - {flight['flight_number']} ({flight['flight_id']}): {flight['from']} → {flight['to']}")
            print(f"     First class: {flight.get('first_available', 0)}/{flight.get('first_total', 0)} available")
    
    # Test 6: Search by seat class (economy)
    print("\n6. Searching flights with economy class availability:")
    response, status = make_request("POST", "/flights/search", {"class": "economy"})
    if status == 200:
        print(f"✅ Found {response['count']} flights with economy class")
        for flight in response['flights']:
            print(f"   - {flight['flight_number']} ({flight['flight_id']}): {flight['from']} → {flight['to']}")
            print(f"     Economy: {flight.get('economy_available', 0)}/{flight.get('economy_total', 0)} available")

def test_view_seats():
    """Test viewing available seats"""
    print("\n💺 Testing Seat Viewing...")
    
    # Test viewing seats for FL001 (fully booked)
    print("\n1. Viewing available seats for flight FL001 (fully booked):")
    response, status = make_request("GET", "/flights/FL001/seats")
    if status == 200:
        print(f"✅ Flight FL001 has {response['total_available']} available seats")
        print(f"   Total seats: {response['total_seats']}")
        if response['total_available'] == 0:
            print("   ✅ Correctly shows 0 available seats (fully booked)")
        else:
            print(f"   First class: {response['first_class']['total_available']}/{response['first_class']['total_seats']}")
            print(f"   Economy: {response['economy_class']['total_available']}/{response['economy_class']['total_seats']}")
    
    # Test viewing seats for FL006 (popular route)
    print("\n2. Viewing available seats for flight FL006 (popular route):")
    response, status = make_request("GET", "/flights/FL006/seats")
    if status == 200:
        print(f"✅ Flight FL006 has {response['total_available']} available seats")
        print(f"   Total seats: {response['total_seats']}")
        print(f"   First class: {response['first_class']['total_available']}/{response['first_class']['total_seats']}")
        print(f"   Economy: {response['economy_class']['total_available']}/{response['economy_class']['total_seats']}")
    
    # Test viewing first class only for FL002
    print("\n3. Viewing first class seats for flight FL002:")
    response, status = make_request("GET", "/flights/FL002/seats?class=first")
    if status == 200:
        print(f"✅ Flight FL002 first class has {response['total_available']} available seats")
        print(f"   Total first class seats: {response['total_seats']}")
        print(f"   Available first class seats: {', '.join(response['available_seats'][:5])}{'...' if len(response['available_seats']) > 5 else ''}")
    
    # Test viewing economy only for FL002
    print("\n4. Viewing economy seats for flight FL002:")
    response, status = make_request("GET", "/flights/FL002/seats?class=economy")
    if status == 200:
        print(f"✅ Flight FL002 economy has {response['total_available']} available seats")
        print(f"   Total economy seats: {response['total_seats']}")
        print(f"   Available economy seats: {', '.join(response['available_seats'][:5])}{'...' if len(response['available_seats']) > 5 else ''}")
    
    # Test viewing seats for non-existent flight
    print("\n5. Viewing seats for non-existent flight:")
    response, status = make_request("GET", "/flights/INVALID/seats")
    if status == 404:
        print("✅ Correctly returned 404 for non-existent flight")

def test_reserve_seats():
    """Test seat reservation"""
    print("\n📝 Testing Seat Reservation...")
    
    # Test 1: Try to reserve seats on fully booked FL001
    print("\n1. Trying to reserve seats on fully booked FL001:")
    reservation_data = {
        "seat_ids": ["1A", "1B"],
        "user_id": "U42",
        "seat_class": "first"
    }
    response, status = make_request("POST", "/flights/FL001/reserve", reservation_data)
    if status == 400:
        print("✅ Correctly rejected reservation on fully booked flight")
        print(f"   Unavailable seats: {response['unavailable_seats']}")
    
    # Test 2: Reserve first class seats on available flight FL002
    print("\n2. Reserving first class seats 3A and 3B for user U42 on FL002:")
    reservation_data = {
        "seat_ids": ["3A", "3B"],
        "user_id": "U42",
        "seat_class": "first"
    }
    response, status = make_request("POST", "/flights/FL002/reserve", reservation_data)
    if status == 200:
        print(f"✅ Successfully reserved first class seats: {response['seats']}")
        print(f"   Reservation ID: {response['reservation_id']}")
        print(f"   Seat class: {response['seat_class']}")
        print(f"   Expires at: {response['expires_at']}")
        return response['reservation_id']
    else:
        print(f"❌ Failed to reserve seats: {response}")
        return None

def test_purchase_seats(reservation_id):
    """Test seat purchase"""
    print("\n💰 Testing Seat Purchase...")
    
    if not reservation_id:
        print("❌ No reservation ID available for purchase test")
        return None
    
    # Test purchasing reserved seats
    print(f"\n1. Purchasing seats with reservation {reservation_id}:")
    purchase_data = {
        "reservation_id": reservation_id,
        "user_id": "U42"
    }
    response, status = make_request("POST", "/flights/FL002/purchase", purchase_data)
    if status == 200:
        print(f"✅ Successfully purchased seats: {response['seats']}")
        print(f"   Purchase ID: {response['purchase_id']}")
        print(f"   Seat class: {response['seat_class']}")
        print(f"   Purchased at: {response['purchased_at']}")
        return response['purchase_id']
    else:
        print(f"❌ Failed to purchase seats: {response}")
        return None

def test_cancel_purchase(purchase_id):
    """Test purchase cancellation"""
    print("\n❌ Testing Purchase Cancellation...")
    
    if not purchase_id:
        print("❌ No purchase ID available for cancellation test")
        return
    
    # Test cancelling purchased seats
    print(f"\n1. Cancelling purchase {purchase_id}:")
    cancel_data = {
        "purchase_id": purchase_id,
        "user_id": "U42"
    }
    response, status = make_request("POST", "/flights/FL002/cancel", cancel_data)
    if status == 200:
        print(f"✅ Successfully cancelled seats: {response['seats']}")
        print(f"   Cancelled purchase ID: {response['purchase_id']}")
        print(f"   Seat class: {response['seat_class']}")
    else:
        print(f"❌ Failed to cancel purchase: {response}")

def test_error_cases():
    """Test various error cases"""
    print("\n🚨 Testing Error Cases...")
    
    # Test 1: Reserve already reserved seats
    print("\n1. Trying to reserve already reserved seats:")
    reservation_data = {
        "seat_ids": ["1A", "1B"],  # These are already purchased
        "user_id": "U43",
        "seat_class": "first"
    }
    response, status = make_request("POST", "/flights/FL002/reserve", reservation_data)
    if status == 400:
        print("✅ Correctly rejected reservation of unavailable seats")
        print(f"   Unavailable seats: {response['unavailable_seats']}")
    
    # Test 2: Reserve with invalid seat class
    print("\n2. Trying to reserve with invalid seat class:")
    reservation_data = {
        "seat_ids": ["1A", "1B"],
        "user_id": "U43",
        "seat_class": "business"  # Invalid class
    }
    response, status = make_request("POST", "/flights/FL002/reserve", reservation_data)
    if status == 400:
        print("✅ Correctly rejected invalid seat class")
    
    # Test 3: Purchase with invalid reservation
    print("\n3. Trying to purchase with invalid reservation ID:")
    purchase_data = {
        "reservation_id": "invalid-id",
        "user_id": "U42"
    }
    response, status = make_request("POST", "/flights/FL002/purchase", purchase_data)
    if status == 404:
        print("✅ Correctly rejected invalid reservation ID")
    
    # Test 4: Cancel with invalid purchase
    print("\n4. Trying to cancel with invalid purchase ID:")
    cancel_data = {
        "purchase_id": "invalid-id",
        "user_id": "U42"
    }
    response, status = make_request("POST", "/flights/FL002/cancel", cancel_data)
    if status == 404:
        print("✅ Correctly rejected invalid purchase ID")

def test_multiple_flights():
    """Test operations across multiple flights"""
    print("\n✈️ Testing Multiple Flights...")
    
    # Test seat availability across different flights
    flights_to_test = ["FL001", "FL004", "FL006"]
    
    for flight_id in flights_to_test:
        print(f"\nChecking seats for {flight_id}:")
        response, status = make_request("GET", f"/flights/{flight_id}/seats")
        if status == 200:
            print(f"   Available: {response['total_available']}/{response['total_seats']} seats")
            print(f"   First class: {response['first_class']['total_available']}/{response['first_class']['total_seats']}")
            print(f"   Economy: {response['economy_class']['total_available']}/{response['economy_class']['total_seats']}")

def show_current_state():
    """Show current system state"""
    print("\n📊 Current System State:")
    response, status = make_request("GET", "/debug/state")
    if status == 200:
        print(f"   Active reservations: {len(response['reservations'])}")
        print(f"   Active purchases: {len(response['purchases'])}")
        
        # Show seat status for different flights
        for flight_id in ["FL001", "FL004", "FL006"]:
            seats = response['seats'].get(flight_id, {})
            first_available = sum(1 for status in seats.get("first", {}).values() if status == "available")
            first_reserved = sum(1 for status in seats.get("first", {}).values() if status == "reserved")
            first_purchased = sum(1 for status in seats.get("first", {}).values() if status == "purchased")
            
            economy_available = sum(1 for status in seats.get("economy", {}).values() if status == "available")
            economy_reserved = sum(1 for status in seats.get("economy", {}).values() if status == "reserved")
            economy_purchased = sum(1 for status in seats.get("economy", {}).values() if status == "purchased")
            
            print(f"   Flight {flight_id}:")
            print(f"     First class - Available: {first_available}, Reserved: {first_reserved}, Purchased: {first_purchased}")
            print(f"     Economy - Available: {economy_available}, Reserved: {economy_reserved}, Purchased: {economy_purchased}")

def main():
    """Main test function"""
    print("✈️  Airline Reservation System - CLI Test Suite")
    print("=" * 50)
    
    # Test all endpoints
    test_search_flights()
    test_view_seats()
    test_multiple_flights()
    
    # Test reservation and purchase flow
    reservation_id = test_reserve_seats()
    purchase_id = test_purchase_seats(reservation_id)
    test_cancel_purchase(purchase_id)
    
    # Test error cases
    test_error_cases()
    
    # Show final state
    show_current_state()
    
    print("\n🎉 Test suite completed!")
    print("\nTo run the server:")
    print("   cd api && python api.py")
    print("\nTo run tests:")
    print("   python test_cli.py")

if __name__ == "__main__":
    main() 