"""
This DocumentCloud Add-On uses exiftool to extract metadata
and saves them as key/value pairs on DocumentCloud.
"""
import os
import subprocess
import sys
import json
from documentcloud.addon import SoftTimeOutAddOn


class MetadataExtractor(SoftTimeOutAddOn):
    """An example Add-On for DocumentCloud."""
    def get_exif_data(self, file_path):
        """ Runs exiftool via a subprocess call and saves it to a dictionary """
        # Run exiftool command
        exif_process = subprocess.Popen(['exiftool', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = exif_process.communicate()

        if exif_process.returncode != 0:
            print(f"Error running exiftool: {stderr.decode('utf-8')}")
            return None

        # Convert output to dictionary
        exif_data = {}
        lines = stdout.decode('utf-8').strip().split('\n')
        for line in lines:
            key, value = line.split(':', 1)  # Split once only
            exif_data[key.strip()] = value.strip()

        return exif_data

    def main(self):
        """The main add-on functionality goes here."""
        self.set_message("Starting Add-On...")
        for document in self.get_documents():
            with open("{document.id}.pdf", "wb") as pdf_file:
                pdf_file.write(document.pdf)
            exif_data = self.get_exif_data("{document.id}.pdf")
            print(exif_data)
            # If EXIF data is retrieved successfully, add it to document.data
            if exif_data:
                data_to_add = {}
                for key in ['Author', 'Create Date', 'Creator', 'Modify Date', 'Producer']:
                    if key in exif_data:
                        stripped_key = key.replace(" ", "")
                        data_to_add[stripped_key] = exif_data[key]
                print(data_to_add)
            if data_to_add:
                for key, value in data_to_add.items():
                    if key in document.data:
                        document.data[key].append(value)
                    else:
                        document.data[key] = [value]  # Store values in a list
                document.save()
                self.set_message(f"Added EXIF data to document {document.id}")
            else:
                self.set_message(f"Failed to extract EXIF data for document {document.id}")



if __name__ == "__main__":
    MetadataExtractor().main()
