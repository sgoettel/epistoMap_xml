# epistoMap

1. [Prerequisites](#prerequisites)
2. [Input](#input)
3. [Processing](#processing)
4. [Output](#output)
5. [Merge multiple CMIF/XML files](#merge-multiple-cmifxml-files)
6. [Sample Visualizations](#sample-visualizations)

This script creates an interactive map visualization of letters sent between people from different locations using [Folium](https://python-visualization.github.io/folium/). It reads input data from a XML file, processes it, and generates an HTML file containing the map with sender and receiver markers and polylines connecting them.

<img src="/image/epistomap_bruemmer.png" alt="Output of the example XML, Nachlass Franz Brümmer" width="600" height="500">

**To run the script, simply execute it in your terminal or command prompt:**

`$ python3 epistoMap_xml.py path/to/your/file1.xml` 

After the script finishes running, you'll find the generated HTML files in the same directory. The output files will be named using the format `epistoMap_output_[originalfilename].html`.

**If you want to test one or more XML files**, you can do a dry-run mode, which can be enabled using `--dry-run`. In this mode, the script will parse the input XML files and provide a summary of the number of usable <correspDesc> elements, e.g.

`$ python3 epistoMap_xml.py --dry-run file1.xml file2.xml file3.xml` etc.
<<<<<< features

If you have multiple [CMIFs](https://correspsearch.net/en/documentation.html) or more than one XML file that you want to visualize, you can use `mergexml.py` to combine all <correspDesc> elements into a single XML file (see [merge XML files](#merge-multiple-cmifxml-files)).

## Prerequisites

To run you need Python 3.x along with Folium, Pandas, lxml and requests libraries.

You can install these packages using pip:

`$ pip install folium pandas lxml requests` 

## Input

The input XML file should follow the TEI encoding guidelines and contain `<correspDesc>` elements with metadata about the correspondences in the Correspondence Metadata Interchange-Format (CMIF). Each `<correspDesc>` element should have `<correspAction>` elements for "sent" and "received" actions, including `<persName>`, `<placeName>`, and `<date>` elements. To identify unique sender/receiver and their respective location, it's essential to include any kind of ID in the `@ref` attribute of the `<persName>` and a GeoNames URL in the `@ref` attribute of the `<placeName>` element. The script is compatible with CMIF input data, and you can find a vast collection of files on [correspsearch.net](https://correspsearch.net/en/home.html) or their [GitHub repository](https://github.com/correspSearch/csStorage).

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
    </correspAction>
</correspDesc>
~~~

Any `<correspDesc>` element missing essential information is skipped! Otherwise there wouldn't be an accurate visualization.

## Processing

- The script reads the input data using pandas and processes it to extract unique sender-receiver pairs. It uses the `@ref` attribute from `<persName>` (or `<orgName>`) elements in the input XML files and processes it as unique identifiers for individuals, which are then used for creating sender and receiver markers in the map visualization.
- The script allows users to adjust certain constants, such as the `OFFSET` and `POLYLINE_WEIGHT_MULTIPLIER`. The `OFFSET` is used to randomly shift the location of markers on the map, preventing overlapping markers when they are located at the same coordinates. The `POLYLINE_WEIGHT_MULTIPLIER` is a constant used to adjust the thickness of the polylines representing correspondences, with a higher number of correspondences between sender/receiver resulting in a thicker polyline.
- The script extracts GeoNames IDs from the `@ref` attribute of the `<placeName>` elements in the input XML data. It then uses these IDs to query the GeoNames API. NB: GeoNames has a daily limit of about 1000 requests, after which it stops access. Using an account and API access doesn't really change this limit (I'm still trying to find a way around this..).
- In the script, the function `populate_location_pairs()` is responsible for grouping the letters based on sender and receiver IDs. It creates a dictionary holding the necessary information for each unique sender-receiver pair, ensuring that a sender or receiver is only displayed once when they are at the exact same location.
- It employs the folium library to create an interactive map

## Output

The output is an interactive HTML map with some features. Senders and receivers are represented by distinct markers (arrow-up for senders, arrow-down for receivers) with polyline (randomly colored) connections between sender and receiver locations. When clicking on a polyline, a popup appears displaying information about the correspondence, including the sender's and receiver's names, and the date(s) of the correspondence. If a `<correspDesc>` element contains a `@ref` URL, then the URL will be saved as a link for the respective date in the popup. Same goes for the `<persName>`: The `@ref` is used as an URL for the plain text of the name in the popup of a sender and receiver marker. If you would like to change the map, e.g., to `OpenStreetMap`, you can update the `tiles` parameter in the `folium.Map()` function.

## Merge multiple CMIF/XML files

Want to visualize multiple CMIFs? Use `mergexml.py`. This script combines all `<correspDesc>` elements from XML files in a single directory.

How it works:

`$ python3 mergexml.py path/to/your/folder` 

1. **TEI Header**: The script grabs the first XML file it finds based on the `os.listdir()` output to use its TEI header.
2. **Combine Elements**: It then goes through all the XML files in the directory, collecting all the `<correspDesc>` elements.
3. **Validation**: After combining, it double-checks to make sure everything's alright. It counts all the original `<correspDesc>` elements and compares that number with the combined total in `combined.xml`.

If all goes well, the total number of `<correspDesc>` elements should match between the original and combined files. You can then use epistoMap on your new `combined.xml`.

## Sample Visualizations

Some sample visualizations created using epistoMap; more to come

[Correspondence of Alexander von Humboldt](https://rawcdn.githack.com/sgoettel/epistoMap_xml/148f08f3d2e1dc4b65db36ab6034e9b972687f77/sample_visualizations/epistoMap_output_avhumboldt_combined.html) (all [CMIFs from Humboldt](https://github.com/correspSearch/csStorage/tree/dev/avhumboldt) combined)


[Correspondence of Franz Brümmer](https://rawcdn.githack.com/sgoettel/epistoMap_xml/148f08f3d2e1dc4b65db36ab6034e9b972687f77/sample_visualizations/epistoMap_output_bruemmer_nachlass.html)
