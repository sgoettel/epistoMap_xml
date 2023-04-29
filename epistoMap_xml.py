import folium
from folium.plugins import FastMarkerCluster
import pandas as pd
from lxml import etree
import random
import requests
import re
import argparse
import os

# Use argparse to parse the command-line arguments
parser = argparse.ArgumentParser(description="Create a map visualization from an XML file.")
parser.add_argument("input_files", nargs="+", help="One or more input XML files.")
parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without calling the GeoNames API.")
args = parser.parse_args()
input_files = args.input_files

# Constants which you can adjust here
OFFSET = 0.002
"""float: The maximum distance, in degrees of latitude and longitude, 
to randomly offset the location of a marker on the map. This is used to
prevent multiple markers from overlapping if they are located at
the same coordinates"""

POLYLINE_WEIGHT_MULTIPLIER = 1.5
"""float: The multiplier used to determine the weight/thickness 
of a polyline on the map. The weight is proportional to the number 
of letters exchanged between two people, and is calculated by multiplying 
the number of letters by this constant."""

def add_offset(lat, lng, offset):
    new_lat = lat + random.uniform(-offset, offset)
    new_lng = lng + random.uniform(-offset, offset)
    return new_lat, new_lng

def create_sender_marker(location, name):
    return folium.Marker(location=location, popup=name, icon=folium.Icon(icon="arrow-up"))

def create_receiver_marker(location, name):
    return folium.Marker(location=location, popup=name, icon=folium.Icon(icon="arrow-down"))

def populate_location_pairs(letters):
    location_pairs = {}
    for index, row in letters.iterrows():
        if pd.isnull(row["sender_place_lat"]) or pd.isnull(row["sender_place_long"]) or pd.isnull(row["receiver_place_lat"]) or pd.isnull(row["receiver_place_long"]):
            continue

        key = (row["sender_id"], row["sender_place_lat"], row["sender_place_long"], row["receiver_id"], row["receiver_place_lat"], row["receiver_place_long"])
        if key not in location_pairs:
            location_pairs[key] = {
                "count": 1,
                "sender_name": row["sender_name"],
                "receiver_name": row["receiver_name"],
                "dates": [row["date_sent"]],
                "sender_coords": (row["sender_place_lat"], row["sender_place_long"]),
                "receiver_coords": (row["receiver_place_lat"], row["receiver_place_long"]),
            }

        else:
            location_pairs[key]["count"] += 1
            location_pairs[key]["dates"].append(row["date_sent"])
    return location_pairs


def get_coordinates_from_place_id(place_id):
    if args.dry_run:
        return 0.0, 0.0
    
    url = f"https://sws.geonames.org/{place_id}/about.rdf"
    response = requests.get(url)

    if response.status_code != 200:
        return None, None

    rdf_data = response.content
    rdf_root = etree.fromstring(rdf_data)

    lat_elem = rdf_root.find(".//wgs84_pos:lat", namespaces={'wgs84_pos': 'http://www.w3.org/2003/01/geo/wgs84_pos#'})
    long_elem = rdf_root.find(".//wgs84_pos:long", namespaces={'wgs84_pos': 'http://www.w3.org/2003/01/geo/wgs84_pos#'})

    if lat_elem is not None and long_elem is not None:
        lat = float(lat_elem.text)
        long = float(long_elem.text)
        return lat, long

    return None, None

def extract_place_id_from_url(url: str) -> str:
    if url is None:
        return None
    
    match = re.search(r'\d+$', url.rstrip('/'))
    if match:
        return match.group()
    return None

def parse_xml_data(xml_data):
    root = etree.fromstring(xml_data)
    correspondences = root.findall(".//tei:correspDesc", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

    data = []
    for corresp in correspondences:
        sent = corresp.find("tei:correspAction[@type='sent']", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        received = corresp.find("tei:correspAction[@type='received']", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        if sent is None or received is None:
            continue

        # Check for missing persName, placeName, and date elements
        if (sent.find("tei:persName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) is None and
            sent.find("tei:orgName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) is None) or \
           sent.find("tei:placeName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) is None or \
           sent.find("tei:date", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) is None or \
           (received.find("tei:persName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) is None and
            received.find("tei:orgName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) is None) or \
           received.find("tei:placeName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}) is None:
           
            continue

        sender = sent.find("tei:persName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        if sender is None:
            sender = sent.find("tei:orgName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        sender_id = sender.get("ref")
        sender_name = sender.text

        receiver = received.find("tei:persName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        if receiver is None:
            receiver = received.find("tei:orgName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        receiver_id = receiver.get("ref")
        receiver_name = receiver.text

        sender_place = sent.find("tei:placeName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        sender_place_id = sender_place.get("ref")
        sender_place_id = extract_place_id_from_url(sender_place_id)
        sender_place_lat, sender_place_long = get_coordinates_from_place_id(sender_place_id)

        receiver_place = received.find("tei:placeName", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        receiver_place_id = receiver_place.get("ref")
        receiver_place_id = extract_place_id_from_url(receiver_place_id)
        receiver_place_lat, receiver_place_long = get_coordinates_from_place_id(receiver_place_id)


        
        date_sent = sent.find("tei:date", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
        date_sent_attributes = date_sent.attrib
        if 'when' in date_sent_attributes:
            date = date_sent_attributes['when']
        elif 'notBefore' in date_sent_attributes:
            date = date_sent_attributes['notBefore']
        elif 'notAfter' in date_sent_attributes:
            date = date_sent_attributes['notAfter']
        else:
            date = date_sent.text



        data.append({
            'sender_id': sender_id,
            'sender_name': sender_name,
            'sender_place_lat': sender_place_lat,
            'sender_place_long': sender_place_long,
            'receiver_id': receiver_id,
            'receiver_name': receiver_name,
            'receiver_place_lat': receiver_place_lat,
            'receiver_place_long': receiver_place_long,
            'date_sent': date
        })

    total_corresp_desc = len(correspondences)
    successfully_parsed_corresp_desc = len(data)
    
    return pd.DataFrame(data), total_corresp_desc, successfully_parsed_corresp_desc

# Process each input file
for input_file in args.input_files:
    with open(input_file, "rb") as file:
        xml_data = file.read()

    # Parse XML data
    letters, total_corresp_desc, successfully_parsed_corresp_desc = parse_xml_data(xml_data)

    # Update print statement to show input file name and number of successful correspondences
    print(f"Done. File: {input_file} - Out of {total_corresp_desc} <correspDesc> elements, {successfully_parsed_corresp_desc} contained all necessary data to visualize on the map.")

# Initialize
world_map = folium.Map(location=[50.0, 10.0], tiles="cartodb positron", zoom_start=5)
marker_cluster_senders = FastMarkerCluster(data=[], name="Senders")
marker_cluster_receivers = FastMarkerCluster(data=[], name="Receivers")
location_pairs = populate_location_pairs(letters)

sender_markers = {}
receiver_markers = {}

offset_sender_coords = {}
offset_receiver_coords = {}

# Loop over the location_pairs dictionary and create markers and polylines
for (sender_id, sender_lat, sender_long, receiver_id, receiver_lat, receiver_long), data in location_pairs.items():
    sender_key = (sender_id, sender_lat, sender_long)
    if sender_key not in offset_sender_coords:
        offset_sender_coords[sender_key] = add_offset(sender_lat, sender_long, OFFSET)

    receiver_key = (receiver_id, receiver_lat, receiver_long)
    if receiver_key not in offset_receiver_coords:
        offset_receiver_coords[receiver_key] = add_offset(receiver_lat, receiver_long, OFFSET)

    if sender_key not in sender_markers:
        sender_marker = create_sender_marker(location=offset_sender_coords[sender_key], name=data["sender_name"])
        sender_markers[sender_key] = sender_marker
        marker_cluster_senders.add_child(sender_marker)

    if receiver_key not in receiver_markers:
        receiver_marker = create_receiver_marker(location=offset_receiver_coords[receiver_key], name=data["receiver_name"])
        receiver_markers[receiver_key] = receiver_marker
        marker_cluster_receivers.add_child(receiver_marker)

    polyline_weight = POLYLINE_WEIGHT_MULTIPLIER * data["count"]
    polyline_popup = f"{data['sender_name']} to {data['receiver_name']} on " + " and ".join([f"{date}" for date in data["dates"]])

    folium.PolyLine(
        locations=[
            offset_sender_coords[sender_key],
            offset_receiver_coords[receiver_key],
        ],
        color="black",
        weight=polyline_weight,
        popup=folium.Popup(polyline_popup, max_width=300),
    ).add_to(world_map)


# Add marker clusters to map and create layer control
world_map.add_child(marker_cluster_senders)
world_map.add_child(marker_cluster_receivers)
folium.LayerControl().add_to(world_map)

# output data here
output_filename = f"epistoMap_output_{os.path.splitext(os.path.basename(input_file))[0]}.html"
world_map.save(output_filename)
