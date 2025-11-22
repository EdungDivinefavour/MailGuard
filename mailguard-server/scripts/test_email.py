"""Test script for sending test emails from files through the proxy."""
import smtplib
from email.message import EmailMessage
import sys
from pathlib import Path

def list_test_emails():
    """List all available test email files."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    test_dir = script_dir / 'fixtures'
    if not test_dir.exists():
        print("✗ Error: test fixtures directory not found.")
        return []
    
    files = sorted(test_dir.glob('*.txt'))
    return [f for f in files if f.name != 'README.md']

def send_email_from_file(file_path, proxy_host='localhost', proxy_port=2525):
    """Send an email from a test file through the proxy."""
    
    # Read email content from file
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"✗ Error: File not found: {file_path}")
        sys.exit(1)
    
    # Parse email headers and body
    lines = content.split('\n')
    headers = {}
    body_lines = []
    in_body = False
    
    for line in lines:
        if ':' in line and not in_body:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
        elif line.strip() == '' and not in_body:
            in_body = True
        elif in_body:
            body_lines.append(line)
    
    # Create email message
    msg = EmailMessage()
    
    # Set headers
    msg['From'] = headers.get('from', 'test@example.com')
    msg['To'] = headers.get('to', 'recipient@example.com')
    msg['Subject'] = headers.get('subject', 'Test Email')
    
    # Set body
    body = '\n'.join(body_lines).strip()
    msg.set_content(body)
    
    # Send email
    try:
        print(f"\n📧 Sending: {file_path.name}")
        print(f"   From: {msg['From']}")
        print(f"   To: {msg['To']}")
        print(f"   Subject: {msg['Subject']}")
        print(f"\nConnecting to SMTP proxy at {proxy_host}:{proxy_port}...")
        
        with smtplib.SMTP(proxy_host, proxy_port) as server:
            print("Sending test email...")
            server.send_message(msg)
            print(f"✓ Test email sent successfully!")
            print(f"   Check the web dashboard at http://localhost:5001 to see the results\n")
    except ConnectionRefusedError:
        print(f"✗ Error: Connection refused. Make sure the interceptor is running:")
        print(f"   python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        sys.exit(1)

def show_menu():
    """Display menu and get user choice."""
    files = list_test_emails()
    
    if not files:
        print("No test email files found in tests/fixtures/ directory.")
        return None
    
    print("\n" + "=" * 60)
    print("MailGuard - Test Email Sender")
    print("=" * 60)
    print("\nAvailable test emails:\n")
    
    for i, file in enumerate(files, 1):
        # Get description from filename
        name = file.stem.replace('_', ' ').title()
        print(f"  {i}. {name}")
    
    print(f"  {len(files) + 1}. Exit")
    print()
    
    while True:
        try:
            choice = input(f"Select an email to send (1-{len(files) + 1}): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(files) + 1:
                print("Exiting...")
                return None
            elif 1 <= choice_num <= len(files):
                return files[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(files) + 1}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Send test email through proxy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (choose from menu)
  python test_email.py
  
  # Send specific email directly
  python tests/test_email.py --file tests/fixtures/02_credit_card.txt
  
  # List available emails
  python test_email.py --list
        """
    )
    parser.add_argument('--file', help='Path to specific test email file to send')
    parser.add_argument('--host', default='localhost', help='Proxy host (default: localhost)')
    parser.add_argument('--port', type=int, default=2525, help='Proxy port (default: 2525)')
    parser.add_argument('--list', action='store_true', help='List available test email files')
    
    args = parser.parse_args()
    
    if args.list:
        files = list_test_emails()
        if files:
            print("\nAvailable test emails:")
            print("-" * 60)
            for file in files:
                print(f"  {file.name}")
            print("-" * 60)
        else:
            print("No test email files found.")
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"✗ Error: File not found: {args.file}")
            sys.exit(1)
        send_email_from_file(file_path, args.host, args.port)
    else:
        # Interactive mode
        selected_file = show_menu()
        if selected_file:
            send_email_from_file(selected_file, args.host, args.port)
