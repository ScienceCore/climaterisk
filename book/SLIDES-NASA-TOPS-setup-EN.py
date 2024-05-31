# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: base
#     language: python
#     name: python3
# ---

# + [markdown] slideshow={"slide_type": "slide"}
# # First steps
# ## Setting up the 2i2c Hub and EarthData credentials
#
# <div style="display: flex; align-items: center;">
#     <img src="TOPS.png" alt="Image" style="width: 100px; height: auto; margin-right: 10px;">
#     <h3>ScienceCore:<br>Climate Risk</h3>
# </div>
#
#
#

# + [markdown] slideshow={"slide_type": "notes"}
# In this section, you will find information on how to setup your 2i2c Hub account and your EarthData credentials. Both are necessary to complete the following modules.

# + [markdown] slideshow={"slide_type": "slide"}
# ## Connect to the 2i2c Hub
#
# - Collaborative cloud service for communities in research and education. 
# - Connect to the Hub by following this link: https://showcase.2i2c.cloud/hub/login
#

# + [markdown] slideshow={"slide_type": "notes"}
# The 2i2c Hub is a collaborative cloud service for communities in research and education. 
# The classes you will find in the modules of this Jupyter book are designed to run on the 2i2c hub. 
#

# + [markdown] slideshow={"slide_type": "slide"}
# ## NASA EarthData
#
# - Platform designed to facilitate access and use of Earth science data (images, satellite observations, climate data, and environmental measurements).
# - Free and open access. 
#

# + [markdown] slideshow={"slide_type": "notes"}
# NASA's Earth Science Data Systems program oversees the life cycle of NASA’s Earth science data from all of its Earth Observation missions — from acquisition through processing and distribution. 
#
# The Earthdata platform is designed to facilitate the discovery, access, and use of Earth science data for research, applications, and decision-making purposes. It provides data in various formats, including images, satellite observations, climate data, and environmental measurements, among others.
#
# the NASA Earthdata website is the starting point for full and open access to NASA's Earth science data collections, which is provided free of cost towards accelerating scientific advancement for societal benefit. 

# + [markdown] slideshow={"slide_type": "slide"}
# ## Create EarthData credentials
#
# - Page to register: https://urs.earthdata.nasa.gov/home
# - Tutorial: https://urs.earthdata.nasa.gov/documentation/for_users/how_to_register
# - Important! Remember to save your **username** and **password**, you will need it later! 

# + [markdown] slideshow={"slide_type": "notes"}
# To access data through this portal, users are required to first set up log in credentials.
#
# You must register at this link: https://urs.earthdata.nasa.gov/home
#
# You can find a tutorial on how to do it at this link: https://urs.earthdata.nasa.gov/documentation/for_users/how_to_register
#
# Be sure to remember the username and password you set up in this step, you will need them in the next one! 
#
#

# + [markdown] slideshow={"slide_type": "slide"}
# ## Access EarthData from Python
#
# - Store the created credentials in a file. 
# - Use the `.netrc` file provided in this repository, including your data on the following line:
#
# machine urs.earthdata.nasa.gov login **{username}** password **{password}**
#
# - Save the changes and close the file. 

# + [markdown] slideshow={"slide_type": "notes"}
# To successfully access NASA data through Python programs and Jupyter notebooks, we need to store the login credentials in a file. 
#
# In this project's repository, a .netrc file is provided where users can enter their credentials.
#
# Open the .netrc file and edit where it says username and password, replacing them with the username and password you created in the previous step. 
#
# Save the changes and close the file. You are now ready to access Earth Observation data through the Earthdata portal!
#
#

# + [markdown] slideshow={"slide_type": "slide"}
# ## Actividad 1
#
# Ejecuta la notebook `1_Getting_Started.ipynb` para obtener la siguiente imagen:
#
# ![Setup1](SETUP1.png)

# + [markdown] slideshow={"slide_type": "slide"}
# ## Live coding: Let's go to the notebook `1_Getting_Started.ipynb`

# + [markdown] slideshow={"slide_type": "notes"}
# To ensure that your credentials are correctly set up and working, you can run the Jupyter notebook titled 1_Getting_Started.ipynb. 
