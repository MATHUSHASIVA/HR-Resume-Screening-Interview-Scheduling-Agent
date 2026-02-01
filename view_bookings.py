"""
View all booked interview slots.
"""

import json
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)


def load_bookings():
    """Load all bookings from file."""
    booking_file = Path("data/booked_slots.json")
    
    if not booking_file.exists():
        return []
    
    try:
        with open(booking_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading bookings: {e}{Style.RESET_ALL}")
        return []


def display_bookings():
    """Display all booked interview slots."""
    bookings = load_bookings()
    
    if not bookings:
        print(f"{Fore.YELLOW}📅 No interview slots booked yet.{Style.RESET_ALL}\n")
        return
    
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📅 BOOKED INTERVIEW SLOTS ({len(bookings)} total){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    for i, booking in enumerate(bookings, 1):
        candidate = booking.get('candidate_name', 'Unknown')
        date = booking.get('date', 'N/A')
        time = booking.get('time', 'N/A')
        timezone = booking.get('timezone', 'N/A')
        booked_at = booking.get('booked_at', 'N/A')
        
        # Format booked_at timestamp
        try:
            booked_dt = datetime.fromisoformat(booked_at)
            booked_str = booked_dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            booked_str = booked_at
        
        print(f"{Fore.YELLOW}Booking #{i}{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Candidate:{Style.RESET_ALL} {candidate}")
        print(f"  {Fore.WHITE}Date:{Style.RESET_ALL} {date}")
        print(f"  {Fore.WHITE}Time:{Style.RESET_ALL} {time} ({timezone})")
        print(f"  {Fore.WHITE}Booked At:{Style.RESET_ALL} {booked_str}")
        print()
    
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    display_bookings()
