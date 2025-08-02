import requests
import json
import time

# Test the multi-query endpoint
url = "http://localhost:8000/hackrx/run"
payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}

# Add API key for authentication
headers = {
    "Authorization": "Bearer 7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9",
    "Content-Type": "application/json"
}

print(f"Sending request to {url}...")
start_time = time.time()

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for 4XX/5XX responses
    
    # Save the results to a file
    with open("test_results.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    
    print(f"Request completed in {time.time() - start_time:.2f} seconds")
    print(f"Results saved to test_results.json")
    print("\nSample of results:")
    results = response.json()
    
    # Print a summary of the results
    print(f"Document URL: {results.get('documents')}")
    print(f"Model used: {results.get('model_used')}")
    print(f"Processing time: {results.get('processing_time')} seconds")
    print("\nQuestions and Answers:")
    
    for i, qa in enumerate(results.get('results', [])):
        print(f"\nQ{i+1}: {qa.get('question')}")
        print(f"A{i+1}: {qa.get('answer')[:150]}..." if len(qa.get('answer', '')) > 150 else f"A{i+1}: {qa.get('answer')}")
        if qa.get('error'):
            print(f"Error: {qa.get('error')}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    # Save the error to a file
    with open("test_results.json", "w") as f:
        json.dump({"error": str(e)}, f, indent=2)
    print(f"Error saved to test_results.json")
