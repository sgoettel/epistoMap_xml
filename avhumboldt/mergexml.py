import xml.etree.ElementTree as ET
import os

# Verzeichnis, in dem sich Ihre XML-Dateien befinden
xml_directory = os.getcwd()
# Neuer XML-Dateipfad
new_xml_path = os.path.join(xml_directory, "combined.xml")
# Eine Liste aller XML-Dateinamen im angegebenen Verzeichnis
xml_files = [f for f in os.listdir(xml_directory) if f.endswith('.xml')]

# Nehmen Sie den Header aus der ersten XML-Datei
tree = ET.parse(os.path.join(xml_directory, xml_files[0]))
root = tree.getroot()

# Finden Sie das <profileDesc>-Element im Baum
profile_desc = root.find('.//{http://www.tei-c.org/ns/1.0}profileDesc')

# Entfernen Sie alle vorhandenen <correspDesc>-Elemente
for elem in profile_desc.findall('{http://www.tei-c.org/ns/1.0}correspDesc'):
    profile_desc.remove(elem)

# Durchlaufen Sie alle XML-Dateien und fügen Sie <correspDesc>-Elemente hinzu
for xml_file in xml_files:
    current_tree = ET.parse(os.path.join(xml_directory, xml_file))
    current_root = current_tree.getroot()
    
    # Finde alle <correspDesc>-Elemente in der aktuellen Datei
    for corresp_desc in current_root.findall('.//{http://www.tei-c.org/ns/1.0}correspDesc'):
        profile_desc.append(corresp_desc)

# Speichern Sie den neuen Baum in einer neuen XML-Datei
tree.write(new_xml_path)

print("Zusammenführen abgeschlossen!")

