"""
This DocumentCloud Add-On uses exiftool to extract metadata
and saves them as key/value pairs on DocumentCloud.
"""
import os
import subprocess
import sys
import json
from documentcloud.addon import AddOn


class MetadataExtractor(AddOn):
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
            # If EXIF data is retrieved successfully, add it to document.data
            if exif_data:
                for key, value in exif_data.items():
                    stripped_key = key.replace(" ", "_")
                    if key in document.data:
                        document.data[stripped_key].append(value)
                    else:
                        document.data[stripped_key] = [value]  # Store values in a list
                document.save()
                self.set_message(f"Added EXIF data to document {document.id}")
            else:
                self.set_message(f"Failed to extract EXIF data for document {document.id}")



if __name__ == "__main__":
    MetadataExtractor().main()
