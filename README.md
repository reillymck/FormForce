# FormForce

**A Brute Force Tool for Web Forms**

## Installation

To install FormForce, run:

make install

If you don't have `make` installed on your system and are using Windows PowerShell, you can run the following commands instead:

pip install pylint
pip install -r requirements.txt

## Testing

To run tests, execute:

make test

If you don't have `make` installed on your system and are using Windows PowerShell, run:

python -m unittest discover -s test -p "test_*.py"

However, the above will also run a large amount of other tests since our test inherits from the unittest class, so to only run the test we set up, you can 
run this command instead in powershell

python -m unittest tests.test_form_force.TestBruteForceForm.test_brute_force_valid_credentials

