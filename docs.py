import subprocess
import re


def extract_items_from_brackets(input):
  """Extracts items within the first line of brackets from output.

  Args:
    output: The output string.

  Returns:
    A list of items within the first line of brackets.
  """

  match = re.search(r"\{(.*?)\}", input, re.MULTILINE)
  if match:
    items = match.group(1).split(",")
    return items
  else:
    return []

# Example usage
# output = "This is some output {item1, item2, item3}"
# result = extract_items_from_brackets(output)
# print(result)  # Output: ['item1', 'item2', 'item3']

def call_help_for_arguments(script_path):
  """
  Calls `--help` for each argument listed in the script's help message.

  Args:
    script_path: The path to the script.
  """

  # Get the help message
  help_output = subprocess.check_output(['python', script_path, '--help'], text=True)

  # Extract the arguments
  arguments = extract_items_from_brackets(help_output.splitlines()[0])
  print("========================================")
  print(f"Available commands: {arguments}")

#   for line in help_output.splitlines():
#     if line.startswith('  -'):
#       argument = line.split()[1]
#       arguments.append(argument)

  # Call `--help` for each argument
  for argument in arguments:
    print("========================================")
    print(f"Calling --help for argument: {argument}")
    print("========================================")
    output = subprocess.check_output(['python', script_path, argument, '--help'], text=True)
    print(output)
    print("\n")

# Replace 'myscript/__init__.py' with the actual path to your script
script_path = 'sleeper_data_pypline/__init__.py'
call_help_for_arguments(script_path)