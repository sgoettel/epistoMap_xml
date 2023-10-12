# epistoMap


1. [Prerequisites](#prerequisites)
2. [Input](#input)
3. [Processing](#processing)
4. [Output](#output)
5. [Sample Visualizations](#sample-visualizations)

This script creates an interactive map visualization of letters sent between people from different locations using [Folium](https://python-visualization.github.io/folium/). It reads input data from a XML file, processes it, and generates an HTML file containing the map with sender and receiver markers and polylines connecting them. If your input file is a CSV, consider checking out my other script [epistoMap (CSV)](https://github.com/sgoettel/epistoMap_csv)

<img src="/image/epistomap_humboldt.png" alt="Output of the example CSV, edition humboldt digital" width="600" height="500">

To run the script, simply execute it in your terminal or command prompt:

`$ python3 epistoMap.py_xml` 

Make sure the input XML file (`epistoMap_input.xml`) is in the same directory as the script. After the script finishes running, you'll find the generated HTML file (`epistoMap_output_xml.html`) in the same directory.

## Prerequisites

To run you need Python 3.x along with Folium, Pandas, lxml and requests libraries.

You can install these packages using pip:

`$ pip install folium pandas lxml requests` 

## Input


The input XML (`epistoMap_input.xml`) file should follow the TEI encoding guidelines and contain `<correspDesc>` elements with metadata about the correspondences. Each `<correspDesc>` element should have `<correspAction>` elements for "sent" and "received" actions, including `<persName>`, `<placeName>`, and `<date>` elements. To identify the location of a sender/receiver, it's essential to include a GeoNames URL in the `@ref` attribute of the `<placeName>` element.

Example input XML structure:

~~~xml
<correspDesc>
  <correspAction type="sent">
    <persName ref="https://www.example.com/person/1">Sender Name</persName>
    <placeName ref="https://www.geonames.org/123456">Sender City</placeName>
    <date when="2022-01-01"/>
  </correspAction>
  <correspAction type="received">
    <persName ref="https://www.example.com/person/2">Receiver Name</persName>
    <placeName ref="https://www.geonames.org/654321">Receiver City</placeName>
    <date when="2022-01-02"/>
  </correspAction>
</correspDesc>
~~~

Any `<correspDesc>` element missing essential information, such as `<persName>`, `<placeName>`, or `<date>`, is skipped! Otherwise there wouldn't be an accurate visualization.

## Processing

The script reads the input data using pandas and processes it to extract unique sender-receiver pairs. It groups the letters based on sender and receiver IDs, ensuring that a sender or receiver is only displayed once when they are at the exact same location.

The script extracts GeoNames IDs from the @ref attribute of the `<placeName>` elements in the input XML data. GeoNames has a daily limit of about 1000 requests, after which it stops access. Using an account and API access doesn't really change this limit (I'm still trying to find a way around this..).

The script employs the folium library to create an interactive map with two marker clusters: one for senders and another for receivers. It uses a custom `add_offset` function to slightly offset the markers to prevent overlapping when multiple individuals are at the same location.

## Output

The output is an interactive HTML map with some features.  Senders and receivers are represented by distinct markers (arrow-up for senders, arrow-down for receivers) with polyline connections between sender and receiver locations. You easily can change the map tiles, adjust the offset value in the `add_offset` function to control the marker separation or alter the weight and popup content etc.

## Sample Visualizations


[Correspondence of Alexander von Humboldt](https://rawcdn.githack.com/sgoettel/epistoMap_xml/148f08f3d2e1dc4b65db36ab6034e9b972687f77/sample_visualizations/epistoMap_output_avhumboldt_combined.html) (all [CMIFs from Humboldt](https://github.com/correspSearch/csStorage/tree/dev/avhumboldt) combined)


[Correspondence of Franz Brümmer](https://rawcdn.githack.com/sgoettel/epistoMap_xml/148f08f3d2e1dc4b65db36ab6034e9b972687f77/sample_visualizations/epistoMap_output_bruemmer_nachlass.html)
