---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.2
---

<!-- #region slideshow={"slide_type": "slide"} -->
# Analyzing Flood Risk Reproducibly with NASA Earthdata Cloud

<div style="display: flex; align-items: center;">
    <img src="../../assets/TOPS.png" alt="Image" style="width: 100px; height: auto; margin-right: 10px;">
    <h3>ScienceCore:<br>Climate Risk</h3>
</div>



<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Objective

Utilize NASA's open products called Opera Dynamic Surface Water eXtent (DSWx) - Harmonized Landsat Sentinel-2 (HLS) to map the extent of flooding resulting from the September 2022 monsoon event in Pakistan.

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
In 2022, Pakistan's monsoon rains reached record levels, causing devastating floods and landslides that affected all four provinces of the country and around 14% of its population. In this example, you will see how to use NASA's open products Opera DSWx-HLS to map the extent of flooding caused by the monsoon in September 2022 in Pakistan.

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Roadmap

- Opera DSWx-HLS Products
- Set up the working environment
- Define the area of interest
- Data search and retrieval
- Data analysis
- Processing and visualization
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
First, we will define what Opera DSWx-HLS products are and what kind of information you can obtain from them.
Then, you will learn to set up your working environment, define the area of interest you want to gather information about, perform data search and retrieval, analyze and visualize it.

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## The Expected Outcome

-- Insert resulting image --
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
This is the final result you will achieve after completing the workshop activities. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Before We Start

- To participate in this class, you must accept the coexistence guidelines detailed [here]().
- If you speak, then mute your microphone to avoid interruptions from background noise. We might do it for you.
- To say something, request the floor or use the chat.
- Can we record the chat? Can we take pictures?

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
Coexistence guidelines:
- If you're in this course, you've accepted the coexistence guidelines of our community, which broadly means we'll behave in a polite and friendly manner to make this an open, safe, and friendly environment, ensuring the participation of all individuals in our virtual activities and spaces.
- If any of you see or feel that you're not comfortable enough, you can write to us privately.
- In case those of us who don't make you feel comfortable are --teachers-- you can indicate it by sending an email to --add reference email--
How to participate:
- We're going to ask you to mute/turn off your microphones while you're not speaking so that the ambient sound from each of us doesn't bother us.
- You can request the floor by raising your hand or in the chat, and --teachers-- will be attentive so that you can participate at the right time.
About recording:
- The course will be recorded, if you don't want to appear in the recording, we ask you to turn off the camera.
- If any of you want to share what we're doing on social media, please, before taking a photo or screenshot with the faces of each of the people present, ask for permission because some people may not feel comfortable sharing their image on the internet. There are no problems in sharing images of the slides or --the teacher's face--.


<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Opera DSWx-HLS Dataset

- Contains observations of surface water extent at specific locations and times (from February 2019 to September 2022).
- Distributed over projected map coordinates as mosaics.
- Each mosaic covers an area of 109.8 x 109.8 km.
- Each mosaic includes 10 GeoTIFF (layers).

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
This dataset contains observations of surface water extent at specific locations and times spanning from February 2019 to September 2022. The input dataset for generating each product is the Harmonized Landsat-8 and Sentinel-2A/B (HLS) product version 2.0. HLS products provide surface reflectance (SR) data from the Operational Land Imager (OLI) aboard the Landsat 8 satellite and the MultiSpectral Instrument (MSI) aboard the Sentinel-2A/B satellite.

Surface water extent products are distributed over projected map coordinates. Each UTM mosaic covers an area of 109.8 km × 109.8 km. This area is divided into 3,660 rows and 3,660 columns with a pixel spacing of 30 m.

Each product is distributed as a set of 10 GeoTIFF files (layers) including water classification, associated confidence, land cover classification, terrain shadow layer, cloud/cloud-shadow classification, Digital Elevation Model (DEM), and Diagnostic layer in PNG format.


<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Opera DSWx-HLS Dataset

1. B02_BWTR (Water binary layer):
    - 1 (white) = presence of water. 
    - 0 (black) = absence of water. 

2. B03_CONF (Confidence layer):
    - % confidence in its water predictions. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
In this workshop, we will use two layers:
1. **B02_BWTR (Water binary layer):**
This layer provides us with a simple image of flooded areas. Where there is water, the layer is valued at 1 (white), and where there is no water, it takes a value of 0 (black). It's like a binary map of floods, ideal for getting a quick overview of the disaster's extent.
2. **B03_CONF (Confidence layer):**
This layer indicates how confident the DSWx-HLS system is in its water predictions. Where the layer shows high values (near 100%), we can be very sure that there is water. In areas with lower values, confidence decreases, meaning that what appears to be water could be something else, such as shadows or clouds.

To help you better visualize how this works, think of a satellite image of the flood-affected area. Areas with water appear dark blue, while dry areas appear brown or green.
The water binary layer (B02_BWTR), overlaid on the image, would shade all blue areas white, creating a simple map of water yes/no.
In contrast, the confidence layer (B03_CONF) would function as a transparency overlaid on the image, with solid white areas where confidence is high and increasing transparency towards black where confidence is low. This allows you to see where the DSWx-HLS system is most confident that its water predictions are correct.
By combining these layers, scientists and humanitarian workers can get a clear picture of the extent of floods and prioritize rescue and recovery efforts.

<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Set Up the Working Environment

TO BE COMPLETED.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
THIS NEEDS TO BE DEFINED BASED ON NOTEBOOK MODIFICATIONS. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Let's go to notebook XXXXX.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Selection of the Area of Interest (AOI)

- Initialize user-defined parameters.  
- Perform a specific data search on NASA. 
- Search for images within the DSWx-HLS collection that match the AOI.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
Next, you will learn:

1. How to initialize user-defined parameters:

* Define the search area: Draw a rectangle on the map to indicate the area where you want to search for data.
* Set the search period: Mark the start and end dates to narrow down the results to a specific time range.
* Display parameters: Print on the screen the details of the search area and the chosen dates so you can verify them.

2. Perform a specific data search on NASA:

* Connect to the database: Link to NASA's CMR-STAC API to access its files.
* Specify the collection: Indicate that you want to search for data from the "OPERA_L3_DSWX-HLS_PROVISIONAL_V0" collection.
* Perform the search: Filter the results according to the search area, dates, and a maximum limit of 1000 results.

3. Search for images (from the DSWx-HLS collection) that match the area of interest:

* Measure overlap: Calculate how much each image overlaps with the area you are interested in.
* Show percentages: Print these percentages on the screen so you can see the coverage.
* Filter images: Select only those with an overlap greater than a set limit.


<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Let's go to notebook XXXXX.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Activity 1: 

Modify the XXX parameters to define a new area of interest. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Data Search and Retrieval

- Transform filtered data into a list. 
- Display details of the first result:
    - Count the results. 
    - Show overlap. 
    - Indicate cloudiness. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "notes"} -->
In the following section, you'll learn:

1. How to transform filtered results into a list to work with them more easily.
2. How to display details of the first result to see what information it contains.
    - Count the results: how many files were found after applying the filters.
    - Show overlap: how much each file overlaps with the area you're looking for, so you know how well they cover the area.
    - Indicate cloudiness: amount of clouds in each file before filtering, so you can consider if cloud coverage is an important factor for you.



<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Let's go to notebook XXXX. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Activity 2:

TO BE DEFINED
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Data Analysis

TO BE DEFINED
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Let's go to notebook XXXX. 
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Activity 3:

TO BE DEFINED
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Processing and Visualization

TO BE DEFINED
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Live Coding: Let's go to the notebook XXXX.
<!-- #endregion -->

<!-- #region slideshow={"slide_type": "slide"} -->
## Activity 4:

TO BE DEFINED
<!-- #endregion -->
