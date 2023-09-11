# Reproducibly Analyzing Wildfire, Drought, and Flood Risk with NASA Earthdata Cloud


## Project summary
As the climate changes, prediction and management of the risk of wildfire, drought, and floods has become increasingly challenging. It is no longer sufficient to assume that what has been normal and historic for the last century will occur with the same frequency into the future. These natural risks are intrinsically linked to the changing distributions of surface water, precipitation, vegetation, and land use in both time and space. At the same time, there are now hundreds of petabytes of relevant Earth science data available through the NASA Earthdata Cloud that can be used to understand and forecast these water-dependent environmental risks. With the volume of Earth science data growing dramatically year over year, it is important for scientists to understand how open science and cloud-based data intensive computing can be used to reproducibly analyze and assess the changing risk profile of wildfire, drought, and floods.

In this proposed TOPS ScienceCore module, learners will learn to identify, extract, analyze, visualize, and report on data available through NASA Earthdata Cloud for three different scenarios: wildfire, drought, and flood risk. The module will build upon TOPS OpenCore and reinforce principles of reproducibility and open science-based workflows. Computationally, the scenarios will estimate changes in the hydrological water mass balance for defined regions primarily using remote sensing data. We will demonstrate best practices in “data-proximate computing” by considering examples that involve computing climatologies and other statistics from long-time series using numerical methods that scale well with the data being available on the cloud. This module will leverage scientific Python libraries such as Xarray and Dask to perform the computations. The focus of this module will be on data processing and visualization and doing so in a reproducible and transparent way.

After completing this module, learners will be able to adapt and remix the scenarios for their own open science objectives regarding environmental risks such as wildfire, drought, and flood. These risks are common worldwide yet need to be each analyzed in a regional context. The module will provide concrete examples that showcase how open science can be done.

The module will be written as an extension to the OpenCore framework and all course materials will be open, available in English and Spanish, and accessible in the vision, hearing, mobility, and attention dimensions. The ScienceCore module will be released as one or more Jupyter notebooks on GitHub with supporting material for delivering the course using the cloud either for in-person or for virtual cohorts.


## Scientific/Technical Management

### Introduction
With a changing climate, wildfires, droughts, and floods continue to be significant risks across the United States and the rest of the world [1,2]. Events that used to occur only once a century are now occurring every few years. Historical norms for frequency of extreme climate leading to episodic disaster are not sufficient to infer the frequency into the future. 

Flooding is the most significant environmental disaster affecting more than two billion people a year.  Floods cause significant damage to infrastructure, displace people, and lead to disease. The frequency of flooding has increased in recent years due to changes in rainfall and land use. 

The data from the [National Interagency Fire Center](https://www.nifc.gov/) shows significant growth in the size of wildfires in the US over the last 25 years. In some years, over 10 million acres in the US have been burned by wildfires. Canada has also experienced significant recent wildfires resulting in loss of property, livestock, and industry.

Floods and wildfires are intrinsically linked to underlying water conditions: too much or too little water. Droughts, although on a longer timescale, are also caused by too little water being retained in the environment. Droughts, wildfires, and floods can all occur over the course of a few short months in the same region. The key factor is the abundance, or absence, of precipitation (rain and snowfall) either in short-term events or long-term shifts of how that water is retained by the land.

Floods, wildfires, and droughts are at risk to increase in frequency and intensity due to fundamental shifts in extreme precipitation caused by climate change. Fundamentally, these three environmental risks are about water no longer having the distribution that they have had in the past. We can recognize that our world is changing and causing risk. How can we mitigate that risk?

[NASA Earthdata Cloud](https://www.earthdata.nasa.gov/eosdis/cloud-evolution) has moved petabytes of data into the cloud and that data is ideally suited to answering questions about climate change risk. However, practitioners don’t yet have the proper skills and training to take advantage of these amazing resources. It is no longer sufficient to search for a dataset and then download it locally. The sheer size of the available data makes this not just impractical but, in many cases, impossible. But how do scientists attempting risk assessment complete their work when it is so difficult to download the needed data to a computer to allow running their analysis code locally? The answer is to instead perform data-proximate computing by pushing the analysis code to a computer that is very close (in terms of both costs and latency using the Internet) to where the data is hosted. For data that is hosted in the commercial cloud (such as NASA Earthdata), this means running data analysis on computers in that same cloud environment.

This ScienceCore module, building on top of the OpenCore modules, will teach learners how to access the NASA Earthdata Cloud and produce dashboard-based visualizations and analyses of water sensing data. This data can then be compared with model outputs to forecasts, the new ‘normals’ for wildfire, drought, and flood risk across the world.
This risk assessment is highly localized and needs to be repeated for every country, state, city, and village. Demonstrating how to leverage NASA Earthdata cloud data in an open, reproducible way will aid thousands of scientists and analysts to produce the reports they need for their own communities. 

There is currently a barrier for scientists to use NASA Earthdata Cloud. They do not have the skills and expertise to analyze data at scale in the cloud. This ScienceCore module will teach that skill.

### Objectives and Expected Significance
Teaching a large number of users about reproducibly analyzing earth data will accelerate our ability to mitigate and adapt to climate change. So a ‘science objective’ is determining if this ScienceCore module will actually help with those adaptation efforts. 

This new ScienceCore module will solve the need to apply earth sensing data to climate risk assessment. More generally, it will serve as a template for future ScienceCore modules in this domain. As part of this work, we will not only develop the ScienceCore module but measure its effectiveness in meeting its learning objectives.

Open science is important for climate change because it helps to ensure that the research and data related to climate change is accessible to everyone. This means that anyone, regardless of their expertise or background, can review and verify the research, which helps to build trust in the findings. In addition, open science promotes collaboration and sharing of ideas among researchers, which can lead to more rapid progress in understanding and addressing climate change. By making research open and transparent, we can ensure that the best science is being used to inform decisions about how to address climate change.

### Impact of proposed work to state of the art
Climate risk needs to be reevaluated at the national, state, and municipality levels. Companies and non-governmental organizations also need to assess climate risk. NASA data contained in the Earthdata cloud is highly relevant to answering the question of assigning climate risk. This ScienceCore module will provide a template for accessing the data and then analyzing it reproducibly, in a consistent and open manner that exemplifies the best practices identified in the TOPS OpenCore content.

The intended audience for this ScienceCore module is people tasked with producing climate risk assessments. There is potential for taking the tooling and data that we collectively now have available from these global models and downscaling that information to every country, region, state, city, town, and village on anticipated climate impacts. Policy and planners at all levels are beginning to tackle the questions of taking these large, global scale data products and figuring out what they mean for their locality. The community is thinking about how the physical climate variables (e.g. temperature and precipitation) affect risks such as flooding, wildfires, droughts, sea level rise, food sustainability, among many others. 


```{tableofcontents}
```
