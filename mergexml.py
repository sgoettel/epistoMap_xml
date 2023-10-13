import xml.etree.ElementTree as ET
import os
import sys

def main(directory_path):
    xml_directory = directory_path
    new_xml_path = os.path.join(xml_directory, "combined.xml")
    xml_files = [f for f in os.listdir(xml_directory) if f.endswith('.xml') and f != "combined.xml"]

    if not xml_files:
        print("No XMLs found in the specified directory.")
        return

    # Use header from the first XML file
    tree = ET.parse(os.path.join(xml_directory, xml_files[0]))
    root = tree.getroot()
    profile_desc = root.find('.//{http://www.tei-c.org/ns/1.0}profileDesc')

    # Remove existing <correspDesc> elements
    for elem in profile_desc.findall('{http://www.tei-c.org/ns/1.0}correspDesc'):
        profile_desc.remove(elem)

    total_elements = 0  # total numbers of <correspDesc> elements from all XML files

    # look through all XML files and add <correspDesc> elements
    for xml_file in xml_files:
        current_tree = ET.parse(os.path.join(xml_directory, xml_file))
        current_root = current_tree.getroot()
        current_elements = current_root.findall('.//{http://www.tei-c.org/ns/1.0}correspDesc')
        total_elements += len(current_elements)

        for corresp_desc in current_elements:
            profile_desc.append(corresp_desc)

    # save the new tree
    ET.register_namespace('', 'http://www.tei-c.org/ns/1.0')
    tree.write(new_xml_path, encoding='utf-8', xml_declaration=True)

    # Vverify the number of <correspDesc elements
    new_tree = ET.parse(new_xml_path)
    new_root = new_tree.getroot()
    new_elements_count = len(new_root.findall('.//{http://www.tei-c.org/ns/1.0}correspDesc'))

    if new_elements_count == total_elements:
        print(f"Merge complete! Out of a total of {total_elements}, {new_elements_count} <correspDesc> elements were combined.")
    else:
        print(f"Something went wrong. The number of <correspDesc> elements do not match. Out of {total_elements}, only {new_elements_count} <correspDesc> elements were combined.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide the path to a folder.")
    else:
        main(sys.argv[1])