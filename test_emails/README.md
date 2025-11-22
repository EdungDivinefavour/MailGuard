# Test Email Samples

This folder contains sample emails for testing different scenarios with MailGuard.

## Email Files

### 01_clean_email.txt
**Type**: Benign/Clean  
**Contains**: No sensitive data  
**Expected Result**: Should pass through without being flagged  
**Policy**: ALLOW

### 02_credit_card.txt
**Type**: Sensitive - Credit Card  
**Contains**: Credit card number (4532-1234-5678-9010)  
**Expected Result**: Should be flagged and blocked  
**Policy**: BLOCK

### 03_sin_number.txt
**Type**: Sensitive - SIN  
**Contains**: Canadian Social Insurance Number (123-456-789)  
**Expected Result**: Should be flagged and blocked  
**Policy**: BLOCK

### 04_ssn_number.txt
**Type**: Sensitive - SSN  
**Contains**: US Social Security Number (123-45-6789)  
**Expected Result**: Should be flagged and blocked  
**Policy**: BLOCK

### 05_multiple_sensitive.txt
**Type**: Multiple Sensitive Data  
**Contains**: SIN, Credit Card, Email, Phone  
**Expected Result**: Should be flagged and blocked  
**Policy**: BLOCK

### 06_email_addresses.txt
**Type**: Email Addresses Only  
**Contains**: Multiple email addresses (not sensitive by default)  
**Expected Result**: May be tagged but not blocked  
**Policy**: TAG

### 07_mixed_content.txt
**Type**: Mixed Content  
**Contains**: Regular business email with one external email address  
**Expected Result**: May be tagged for email address  
**Policy**: TAG or ALLOW

## How to Use

### Send Test Emails

Use the interactive test script:

```bash
python test_email.py
```

This will show a menu with all available test emails. Choose a number to send that email type.

The script will:
1. Read the email content from the selected file
2. Send it through the SMTP proxy (localhost:2525)
3. Show success/error messages
4. Allow you to choose another email or quit

## Testing Checklist

Use these emails to verify:

- [ ] Clean emails pass through (01_clean_email.txt)
- [ ] Credit cards are detected and blocked (02_credit_card.txt)
- [ ] SIN numbers are detected and blocked (03_sin_number.txt)
- [ ] SSN numbers are detected and blocked (04_ssn_number.txt)
- [ ] Multiple sensitive patterns trigger blocking (05_multiple_sensitive.txt)
- [ ] Email addresses are tagged but not blocked (06_email_addresses.txt)
- [ ] Mixed content is handled correctly (07_mixed_content.txt)

## Notes

- All sensitive data in these files is **fake/test data** for testing purposes only
- Credit card numbers are not valid (for testing only)
- SIN/SSN numbers are randomly generated (not real)
- Modify the content as needed for your specific test scenarios

