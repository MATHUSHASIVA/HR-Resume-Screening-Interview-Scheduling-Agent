"""
Manage interview bookings - view, cancel, or clear all.
"""

import json
from pathlib import Path
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


def save_bookings(bookings):
    """Save bookings to file."""
    booking_file = Path("data/booked_slots.json")
    booking_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(booking_file, 'w') as f:
            json.dump(bookings, f, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving bookings: {e}{Style.RESET_ALL}")
        return False


def display_menu():
    """Display main menu."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📅 INTERVIEW BOOKING MANAGER{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} View all bookings")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Cancel a specific booking")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Clear all bookings")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Exit")
    print()


def view_bookings():
    """View all bookings."""
    bookings = load_bookings()
    
    if not bookings:
        print(f"{Fore.YELLOW}📅 No bookings found.{Style.RESET_ALL}\n")
        return
    
    print(f"\n{Fore.GREEN}Total Bookings: {len(bookings)}{Style.RESET_ALL}\n")
    
    for i, booking in enumerate(bookings, 1):
        candidate = booking.get('candidate_name', 'Unknown')
        date = booking.get('date', 'N/A')
        time = booking.get('time', 'N/A')
        timezone = booking.get('timezone', 'N/A')
        
        print(f"{Fore.YELLOW}{i}.{Style.RESET_ALL} {candidate} - {date} at {time} ({timezone})")
    
    print()


def cancel_booking():
    """Cancel a specific booking."""
    bookings = load_bookings()
    
    if not bookings:
        print(f"{Fore.YELLOW}📅 No bookings to cancel.{Style.RESET_ALL}\n")
        return
    
    view_bookings()
    
    try:
        choice = input(f"{Fore.CYAN}Enter booking number to cancel (or 0 to go back): {Style.RESET_ALL}")
        index = int(choice) - 1
        
        if index == -1:
            return
        
        if 0 <= index < len(bookings):
            cancelled = bookings.pop(index)
            if save_bookings(bookings):
                print(f"{Fore.GREEN}✓ Cancelled booking for {cancelled['candidate_name']}{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.RED}✗ Failed to cancel booking{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}Invalid booking number{Style.RESET_ALL}\n")
    
    except ValueError:
        print(f"{Fore.RED}Invalid input{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}\n")


def clear_all_bookings():
    """Clear all bookings."""
    bookings = load_bookings()
    
    if not bookings:
        print(f"{Fore.YELLOW}📅 No bookings to clear.{Style.RESET_ALL}\n")
        return
    
    print(f"{Fore.RED}⚠️  WARNING: This will delete all {len(bookings)} booking(s)!{Style.RESET_ALL}")
    confirm = input(f"{Fore.CYAN}Type 'YES' to confirm: {Style.RESET_ALL}")
    
    if confirm.upper() == 'YES':
        if save_bookings([]):
            print(f"{Fore.GREEN}✓ All bookings cleared{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.RED}✗ Failed to clear bookings{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}Cancelled{Style.RESET_ALL}\n")


def main():
    """Main program loop."""
    while True:
        display_menu()
        
        try:
            choice = input(f"{Fore.CYAN}Select an option (1-4): {Style.RESET_ALL}")
            
            if choice == '1':
                view_bookings()
            elif choice == '2':
                cancel_booking()
            elif choice == '3':
                clear_all_bookings()
            elif choice == '4':
                print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
                break
            else:
                print(f"{Fore.RED}Invalid option. Please choose 1-4.{Style.RESET_ALL}\n")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
