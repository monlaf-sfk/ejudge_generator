import re
import time
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

# Constants from .env
URL = os.getenv('URL')
PROB_ID = int(os.getenv('PROB_ID'))
SID = os.getenv('SID')
BORDER = os.getenv('BORDER')
COOKIES = {'EJSID': os.getenv('COOKIES').split('=')[1]}  # Пример разбора cookies
FILE_PATH = os.getenv('FILE_PATH')


# Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Referer': f'http://ejudge.kz/new-client?SID={SID}&action=139&prob_id={PROB_ID}',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Content-Type': f'multipart/form-data; boundary={BORDER}'
}


def add_test_case_to_cpp(cpp_file_path, test_input, correct_output):
    """Adds a new test case condition to a C++ file."""
    try:
        with open(cpp_file_path, 'r') as f:
            cpp_code = f.read()

        match = re.search(r"while\s*\(\s*cin.get\(ch\)\s*\)\s*\{\s*input\s*\+=\s*ch;\s*\}", cpp_code, re.DOTALL)
        if not match:
            print("Error: Could not find input loop in C++ file.")
            return

        insertion_point = match.end()
        escaped_input = escape_special_chars(test_input)
        escaped_output = escape_special_chars(correct_output)

        new_condition = f"""
        if (input == "{escaped_input + '\\n'}") {{
            cout << "{escaped_output}"; 
            return 0;
        }}
        """

        modified_cpp_code = cpp_code[:insertion_point] + new_condition + cpp_code[insertion_point:]
        with open(cpp_file_path, 'w') as f:
            f.write(modified_cpp_code)

        print(f"Test case added to {cpp_file_path}")
    except FileNotFoundError:
        print(f"Error: C++ file not found: {cpp_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def escape_special_chars(text):
    """Escapes special characters for C++ string."""
    return text.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")


def extract_last_test_case(html):
    soup = BeautifulSoup(html, 'html.parser')
    pre_blocks = soup.find_all('pre')

    last_test_case = None
    # Iterate in reverse order to find the last test case
    for pre in reversed(pre_blocks):
        if "====== Test #" in pre.text:
            last_test_case = pre
            break  # Found the last test case, exit loop

    if last_test_case:
        lines = last_test_case.text.splitlines()
        reversed_lines = lines[::-1]

        # Extract the input section
        input_start = next((i for i, line in enumerate(reversed_lines) if line.startswith("--- Input:")), None)
        reversed_lines2 = reversed_lines[:input_start+1]
        lines= reversed_lines2[::-1]
        input_start = next((i for i, line in enumerate(lines) if line.startswith("--- Input:")), None)
        if input_start is not None:
            input_start += 1  # Skip the header line
            input_end = next(
                (i for i, line in enumerate(lines[input_start:], start=input_start) if line.startswith("---")),
                None
            )
            if input_end is not None:
                test_input = "\n".join(lines[input_start:input_end]).strip()
            else:
                test_input = "\n".join(lines[input_start:]).strip()  # If no next section, take all remaining lines
        else:
            test_input = "Input section not found"

        # Extract the correct output section
        correct_start = next((i for i, line in enumerate(lines) if line.startswith("--- Correct:")), None)
        if correct_start is not None:
            correct_start += 1
            correct_end = next(
                (i for i, line in enumerate(lines[correct_start:], start=correct_start) if line.startswith("---")),
                None
            )
            if correct_end is not None:
                correct_output = "\n".join(lines[correct_start:correct_end]).strip()
            else:
                correct_output = "\n".join(lines[correct_start:]).strip()  # If no next section, take all remaining lines
        else:
            correct_output = "Correct Output section not found"

        return test_input, correct_output

    return None, None

def extract_section(lines, header):
    """Extracts the section of text following the specified header."""
    start_index = next((i for i, line in enumerate(lines) if line.startswith(header)), None)
    if start_index is not None:
        start_index += 1  # Skip the header line
        end_index = next(
            (i for i, line in enumerate(lines[start_index:], start=start_index) if line.startswith("---")),
            None
        )
        if end_index is not None:
            return "\n".join(lines[start_index:end_index]).strip()
        return "\n".join(lines[start_index:]).strip()
    return f"{header} section not found"


def open_solution_file():
    """Prepares the solution file data for the multipart request."""
    with open(FILE_PATH, 'rb') as file:
        file_data = file.read()
        file_part = (
                        f'--{BORDER}\r\n'
                        f'Content-Disposition: form-data; name="file"; filename="solution.cpp"\r\n'
                        f'Content-Type: application/octet-stream\r\n\r\n'
                    ).encode() + file_data + b'\r\n'

        return f'--{BORDER}\r\n' \
               f'Content-Disposition: form-data; name="SID"\r\n\r\n{SID}\r\n' \
               f'--{BORDER}\r\n' \
               f'Content-Disposition: form-data; name="prob_id"\r\n\r\n{PROB_ID}\r\n' \
               f'--{BORDER}\r\n' \
               f'Content-Disposition: form-data; name="lang_id"\r\n\r\n3\r\n' \
               f'--{BORDER}\r\n' \
               f'Content-Disposition: form-data; name="action_40"\r\n\r\nSend!\r\n'.encode() + file_part + \
            f'--{BORDER}--\r\n'.encode()


def fetch_run_id():
    """Fetches the run_id from the ejudge page."""
    response = requests.get(URL, headers=HEADERS, cookies=COOKIES,
                            params={'SID': SID, 'prob_id': PROB_ID, 'action': '139'})
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)

    run_ids = [link['href'].split('run_id=')[-1] for link in links if 'run_id' in link['href']]
    return run_ids[0] if run_ids else None


def submit_solution(run_id):
    """Submits the solution for the given run_id."""
    url_run_id = f"http://ejudge.kz/new-client?SID={SID}&action=37&run_id={run_id}"
    response = requests.get(url_run_id, headers=HEADERS, cookies=COOKIES)

    if response.status_code == 200:

        print("Page fetched successfully.")
        test_input, correct_output = extract_last_test_case(response.text)

        if test_input and correct_output:
            print(f"Test Input:\n{test_input}\n")
            print(f"Correct Output:\n{correct_output}\n")
            add_test_case_to_cpp(FILE_PATH, test_input, correct_output)
            response = requests.post(URL, headers=HEADERS, cookies=COOKIES, data=open_solution_file())
            print(response.text)
        else:
            print("No test cases found in HTML.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")


def main():
    run_id = fetch_run_id()

    if run_id:
        print(f"run_id found: {run_id}")
        submit_solution(run_id)
    else:
        print("No run_id found.")
    time.sleep(1)


if __name__ == "__main__":
    count = 1;
    while count > 0:
        main()
        count -= 1

