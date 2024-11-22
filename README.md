# Auto-Submission Script for Ejudge

This project contains a Python script that automates the process of submitting solutions to the Ejudge online platform, adding test cases to a C++ solution, and re-submitting until successful.

---

## Features

1. **Automated Run ID Retrieval**: The script fetches the latest `run_id` from the Ejudge page.
2. **Dynamic Test Case Extraction**: Extracts the last test case's input and correct output from the Ejudge submission page.
3. **Test Case Insertion**: Dynamically adds new test cases to a provided C++ solution file.
4. **Solution Submission**: Automatically submits the modified solution back to Ejudge.
5. **Error Handling**: Handles missing test case sections and ensures robust interaction with the Ejudge platform.

---

## Requirements

- Python 3.7+
- Required libraries:
  - `requests`
  - `beautifulsoup4`

Install dependencies using:
```bash
pip install -r requirements.txt
```

File Structure
```plaintext

├── solution.cpp         # The initial C++ solution file
├── main.py            # Main Python script
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

#How to Use
Clone the repository and navigate to the directory:

```bash
Копировать код
git clone https://github.com/monlaf-sfk/ejudge_generator.git
cd ejudge_generator
```
Set the required constants in the script.py file:

- URL: Base URL of the Ejudge platform.
- SID: Ejudge session ID.
- PROB_ID: Problem ID to submit the solution for.
- FILE_PATH: Path to the C++ solution file.
Run the script:

```bash
python main.py
```
The script will:

Fetch the latest run_id.
Extract and add test cases to solution.cpp.
Resubmit the modified solution.
Key Functions
add_test_case_to_cpp(cpp_file_path, test_input, correct_output)
Adds new test cases to the specified C++ file.

`fetch_run_id()`
Retrieves the latest run_id from Ejudge.

`submit_solution(run_id)`
Submits the solution and handles the process of extracting and injecting test cases.

`main()`
Orchestrates the overall workflow.

Future Improvements
---
Add support for multiple languages (not just C++).
Implement retry logic for failed submissions.
Enhance logging for better debugging.
License
This project is open-source and available under the MIT License. Feel free to use and modify as needed.

---
Contributing
---
Contributions are welcome! Fork the repository, make your changes, and submit a pull request.

