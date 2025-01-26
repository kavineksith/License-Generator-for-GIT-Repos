import json
import logging
from datetime import datetime

# Custom Exception Classes
class LicenseError(Exception):
    """Base class for all license-related errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidLicenseName(LicenseError):
    """Raised when an invalid license name is provided."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class LicenseGenerationError(LicenseError):
    """Raised when there is an error generating the license."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class LicenseFileError(LicenseError):
    """Raised when there is an error saving the license file."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Logger setup
logging.basicConfig(filename="license_generator.log", level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class LicenseGenerator:
    """
    Class for generating a LICENSE file for a repository based on the selected open-source license.
    """
    
    def __init__(self, license_name, user_name=None):
        """
        Initializes the license generator with the given license and user name.

        Args:
            license_name (str): Name of the license (e.g., MIT, GPL-3.0, Apache 2.0)
            user_name (str): The name of the user or organization (optional)
        """
        self.license_name = license_name
        self.user_name = user_name
        self.license_data = None
        self.current_year = datetime.now().year
        self.licenses = self.load_licenses()

    def load_licenses(self):
        """
        Load license templates from a JSON file.

        Returns:
            dict: A dictionary of licenses from the JSON file.
        """
        try:
            with open('licenses.json', 'r') as file:
                licenses = json.load(file)
            logging.info("Licenses loaded successfully.")
            return licenses
        except FileNotFoundError:
            logging.error("licenses.json file not found.")
            raise LicenseError("licenses.json file not found.")
        except json.JSONDecodeError:
            logging.error("Error decoding JSON from licenses.json.")
            raise LicenseError("Error decoding JSON from licenses.json.")

    def generate_license_text(self):
        """
        Generate the license text with the user name and year.

        Returns:
            str: The generated license text.
        """
        try:
            if self.license_name not in self.licenses:
                raise InvalidLicenseName(f"License '{self.license_name}' not found in the available licenses.")
            
            license_template = self.licenses[self.license_name]['license_text']
            
            if not self.user_name:  # If user_name is empty, set default value
                logging.warning("No user name provided. Using default: 'Your Name or Organization'.")
                self.user_name = "Your Name or Organization"
            
            # Replace placeholders with the current year and user name
            license_text = license_template.format(year=self.current_year, name=self.user_name)
            logging.info(f"License text generated for {self.license_name}.")
            return license_text
        except KeyError as e:
            logging.error(f"Error generating license text: {e}")
            raise LicenseGenerationError(f"Error generating license text: {e}")
    
    def save_license_file(self, license_text):
        """
        Save the generated license text to a file.

        Args:
            license_text (str): The generated license text to save.
        
        Raises:
            LicenseFileError: If there’s an error saving the file.
        """
        try:
            with open("LICENSE", "w") as file:
                file.write(license_text)
            logging.info("LICENSE file saved successfully.")
        except IOError as e:
            logging.error(f"Error saving LICENSE file: {e}")
            raise LicenseFileError(f"Error saving LICENSE file: {e}")
    
    def create_license(self):
        """
        Full function to generate and save the license.

        Raises:
            LicenseError: For any issues that arise during the generation process.
        """
        try:
            license_text = self.generate_license_text()
            self.save_license_file(license_text)
            logging.info("License creation process completed successfully.")
        except LicenseError as e:
            logging.error(f"Error creating license: {e}")
            raise

# Example usage:
if __name__ == "__main__":
    # User input for license name and optional user name
    license_name = input("Enter the license name (e.g., MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause): ").strip()
    
    # Ensure license_name is not empty
    if not license_name:
        logging.error("License name is required. Please provide a valid license name.")
        raise InvalidLicenseName("License name cannot be empty.")
    
    user_name = input("Enter your name or organization (or press Enter to skip): ").strip()

    # Ensure user_name is not empty if entered
    if user_name == "":
        logging.warning("No name or organization entered. Using default: 'Your Name or Organization'.")
        raise ValueError("Name or organization cannot be empty.")
    
    # Initialize LicenseGenerator
    generator = LicenseGenerator(license_name, user_name)
    
    try:
        generator.create_license()
        print(f"LICENSE file created successfully for {license_name}!")
    except (LicenseError, InvalidLicenseName, LicenseGenerationError, LicenseFileError) as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        print(f"Invalid input: {e}")
    except KeyboardInterrupt:
        logging.warning("License generation process interrupted by user.")
        print("License generation process interrupted by user.")