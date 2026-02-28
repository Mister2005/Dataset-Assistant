"""
Test script to verify the setup and chart generation
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Test 1: Load the dataset
print("Test 1: Loading Titanic dataset...")
try:
    df = pd.read_csv("titanic.csv")
    print(f"✓ Dataset loaded successfully: {len(df)} rows, {len(df.columns)} columns")
except Exception as e:
    print(f"✗ Failed to load dataset: {e}")
    exit(1)

# Test 2: Generate a simple chart
print("\nTest 2: Generating a test chart...")
try:
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Age'].dropna(), bins=30, kde=True)
    plt.title('Distribution of Passenger Ages')
    plt.xlabel('Age')
    plt.ylabel('Number of Passengers')
    plt.savefig('test_chart.png', bbox_inches='tight', dpi=100)
    plt.close()
    
    if os.path.exists('test_chart.png'):
        file_size = os.path.getsize('test_chart.png')
        print(f"✓ Chart generated successfully: test_chart.png ({file_size} bytes)")
        os.remove('test_chart.png')
    else:
        print("✗ Chart file was not created")
except Exception as e:
    print(f"✗ Failed to generate chart: {e}")
    exit(1)

# Test 3: Check environment variables
print("\nTest 3: Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"✓ GOOGLE_API_KEY is set (length: {len(api_key)})")
else:
    print("✗ GOOGLE_API_KEY is not set in .env file")
    print("  Please create a .env file with: GOOGLE_API_KEY=your_api_key_here")

print("\n" + "="*50)
print("Setup verification complete!")
print("="*50)
