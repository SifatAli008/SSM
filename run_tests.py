import unittest
import sys
import os
import time

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def run_tests():
    """Run all tests in the tests directory"""
    # Ensure the parent directory is in the path so modules can be imported
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    start_time = time.time()
    print("🧪 Running Smart Shop Manager tests...")
    
    # Find all test modules in the tests directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    test_loader = unittest.TestLoader()
    
    # Check if tests directory exists
    if not os.path.exists(test_dir):
        print(f"⚠️ Tests directory not found at '{test_dir}'. Creating it...")
        os.makedirs(test_dir)
        print("✅ Tests directory created")
    
    # Discover and run all tests
    test_suite = test_loader.discover(test_dir)
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = test_runner.run(test_suite)
    
    # Print summary
    end_time = time.time()
    run_time = end_time - start_time
    
    print("\n===== Test Results =====")
    print(f"⏱️ Total run time: {run_time:.2f} seconds")
    print(f"🧪 Tests run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    # Return non-zero exit code if tests failed or had errors
    if result.failures or result.errors:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(run_tests()) 