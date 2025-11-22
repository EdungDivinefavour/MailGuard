"""Demo script to test the detection engine directly without SMTP."""
from email_interceptor.detection_engine import DetectionEngine
from email_interceptor.policy_engine import PolicyEngine
from email.message import EmailMessage
from email_interceptor.config import Config

def demo_detection():
    """Demonstrate detection engine capabilities."""
    print("=" * 60)
    print("Email Interceptor - Detection Engine Demo")
    print("=" * 60)
    print()
    
    # Initialize engines
    detection_engine = DetectionEngine(enable_spacy=Config.ENABLE_SPACY)
    policy_engine = PolicyEngine(default_policy=Config.DEFAULT_POLICY)
    
    # Test cases
    test_cases = [
        {
            'name': 'Credit Card',
            'content': 'Please charge my Visa card: 4532-1234-5678-9010',
        },
        {
            'name': 'SIN Number',
            'content': 'My Social Insurance Number is 123-456-789',
        },
        {
            'name': 'Multiple Sensitive Data',
            'content': 'Card: 4532-1234-5678-9010, SIN: 123-456-789, Email: test@example.com',
        },
        {
            'name': 'Benign Email',
            'content': 'Hello, this is a regular business email without sensitive data.',
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 60)
        print(f"Content: {test_case['content']}")
        print()
        
        # Run detection
        detections = detection_engine.detect_patterns(
            test_case['content'],
            min_confidence=Config.MIN_CONFIDENCE
        )
        
        # Show results
        if detections:
            print(f"✓ Detected {len(detections)} pattern(s):")
            for det in detections:
                print(f"  - {det.pattern_type}: '{det.matched_text}' (confidence: {det.confidence:.2f})")
            
            # Create a mock email message
            msg = EmailMessage()
            msg['From'] = 'test@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Test Email'
            msg.set_content(test_case['content'])
            
            # Apply policy
            decision = policy_engine.evaluate(detections, msg)
            print(f"\nPolicy Decision: {decision.action.upper()}")
            print(f"Reason: {decision.reason}")
        else:
            print("✓ No sensitive data detected")
            print("Policy Decision: ALLOW")
        
        print()

if __name__ == '__main__':
    try:
        demo_detection()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

