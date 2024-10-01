# FormForce

**A Brute Force Tool for Web Forms**

Contributers: Reilly McKendrick, Benjamin MacMichael, Sean Ronstadt

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

About the testing:
  * We have github actions setup to run pylint on every commit to the main branch. This checks for general python syntax errors and ensures that main code is always executable.
  * We have a unit test setup to do a basic check to make sure the http post request is working and that the reply is properly processed.
  * In test_files/ there is a username word list and password word list that we used to brute force attack the website form hosted by the Midterm 1 virtual machine. We verified a few of the passwords it found, such as admin:admin, manually to make sure it did not put out false positives. 