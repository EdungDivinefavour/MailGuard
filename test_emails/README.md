# Test Email Samples

Sample emails for testing different scenarios with MailGuard.

## Email Files

### 01_clean_email.txt
Clean email with no sensitive data. Should pass through without being flagged.

### 02_credit_card.txt
Contains a credit card number (4532-1234-5678-9010). Should be flagged and blocked.

### 03_sin_number.txt
Contains a Canadian SIN (123-456-789). Should be flagged and blocked.

### 04_ssn_number.txt
Contains a US SSN (123-45-6789). Should be flagged and blocked.

### 05_multiple_sensitive.txt
Has multiple sensitive patterns (SIN, credit card, email, phone). Should be blocked.

### 06_email_addresses.txt
Just email addresses. May be tagged but probably won't be blocked.

### 07_mixed_content.txt
Regular business email with one external email address. Might get tagged.

## How to Use

Run the test script:

```bash
python test_email.py
```

Pick a number from the menu to send that email type. The script reads the file, sends it through the proxy, and shows you what happened.

## Testing Checklist

Use these to verify everything works:

- [ ] Clean emails pass through (01_clean_email.txt)
- [ ] Credit cards get blocked (02_credit_card.txt)
- [ ] SIN numbers get blocked (03_sin_number.txt)
- [ ] SSN numbers get blocked (04_ssn_number.txt)
- [ ] Multiple patterns trigger blocking (05_multiple_sensitive.txt)
- [ ] Email addresses get tagged but not blocked (06_email_addresses.txt)
- [ ] Mixed content is handled correctly (07_mixed_content.txt)

## Notes

All the sensitive data in these files is fake - just for testing. Credit cards aren't valid, SIN/SSN numbers are made up. Feel free to modify them for your own tests.

