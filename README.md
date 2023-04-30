# epistoMap

This script creates an interactive map visualization of letters sent between people from different locations using [Folium](https://python-visualization.github.io/folium/). It reads input data from a XML file, processes it, and generates an HTML file containing the map with sender and receiver markers and polylines connecting them. If your input file is a CSV, consider checking out my other script [epistoMap (CSV)](https://github.com/sgoettel/epistoMap_csv)

<img src="/image/epistomap_humboldt.png" alt="Output of the example XML, edition humboldt digital" width="600" height="500">

>**Note** While it functions as intended, there are some areas for improvement and fine-tuning that I am working on as a beginner in this field. But since it is not that easy to get a "out of the box solution" for visualizing correspondence, I think it is still a good approach. If you would like to learn more about the features that I am working to implement and the challenges I am facing, please read the docs [at epistoMap CSV](https://github.com/sgoettel/epistoMap_csv#things-to-implement), otherwise: happy mapping!

**To run the script, simply execute it in your terminal or command prompt:**

`$ python3 epistoMap_xml.py path/to/your/file1.xml` 

After the script finishes running, you'll find the generated HTML files in the same directory. The output files will be named using the format `epistoMap_output_[originalfilename].html`.

**If you want to test one or more XML files**, you can do a dry-run mode, which can be enabled using `--dry-run`. In this mode, the script will parse the input XML files and provide a summary of the number of usable <correspDesc> elements, e.g.

`$ python3 epistoMap_xml.py --dry-run file1.xml file2.xml file3.xml` etc.

## Prerequisites

To run you need Python 3.x along with Folium, Pandas, lxml and requests libraries.

You can install these packages using pip:

`$ pip install folium pandas lxml requests` 

## Input


The input XML file should follow the TEI encoding guidelines and contain `<correspDesc>` elements with metadata about the correspondences. Each `<correspDesc>` element should have `<correspAction>` elements for "sent" and "received" actions, including `<persName>`, `<placeName>`, and `<date>` elements. To identify the location of a sender/receiver, it's essential to include a GeoNames URL in the `@ref` attribute of the `<placeName>` element.

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

- The script reads the input data using pandas and processes it to extract unique sender-receiver pairs. It employs the folium library to create an interactive map with two marker clusters: one for senders and another for receivers.
- The script allows users to adjust certain constants, such as the `OFFSET` and `POLYLINE_WEIGHT_MULTIPLIER`. The `OFFSET` is used to randomly shift the location of markers on the map, preventing overlapping markers when they are located at the same coordinates.
- The script extracts GeoNames IDs from the `@ref` attribute of the `<placeName>` elements in the input XML data. It then uses these IDs to query the GeoNames API.
- The `populate_location_pairs()` function creates a dictionary that holds the necessary information for each unique sender-receiver pair.
- Polylines representing correspondences are assigned random colors.
- When clicking on a polyline, a popup appears displaying information about the correspondence, including the sender's and receiver's names, and the date(s) of the correspondence. If a `<correspDesc>` element contains a `@ref` URL, then the URL will be saved as a link for the respective date in the popup.
- The script groups the letters based on sender and receiver IDs, ensuring that a sender or receiver is only displayed once when they are at the exact same location.

## Output

The output is an interactive HTML map with some features.  Senders and receivers are represented by distinct markers (arrow-up for senders, arrow-down for receivers) with polyline connections between sender and receiver locations. You easily can change the map tiles, adjust the offset value in the `add_offset` function to control the marker separation or alter the weight and popup content etc.
