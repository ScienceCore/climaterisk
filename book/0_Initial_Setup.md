# Initial Setup 

## 1- How to use the 2i2c Hub

To access the 2i2c Hub, follow these simple steps:

* Access the 2i2c Hub: Go to https://2i2c.org/platform/}

# Initial Configuration Steps for 2i2c Hub and EarthData NASA Access

## 1. Accessing the 2i2c Hub

To access the 2i2c Hub, follow these simple steps:

* Go to the 2i2c Hub.

![2i2c_login](../assets/2i2c_login.png)

* Enter your credentials: username and password (Note: You must have previously sent your Github account username to be enabled for access with that account).

* If the login is successful, you will see the following screen. Choose the Start option to enter the JupyterLab environment in the cloud.
  

![2i2c_login](../assets/start_server.png)

* Finally, if you see the following JupyterLab screen, you are ready to start working.

![ambiente_trabajo_jupyter_lab](../assets/work_environment_jupyter_lab.png) 

## 2. Using NASA's Earthdata

### Brief Introduction

The NASA Earth Science Data Systems (ESDS) program oversees the lifecycle of Earth science data from all its Earth observation missions, from acquisition to processing and distribution.

For the purposes of this guide, the NASA Earthdata website is the entry point that allows full, free and open access to NASA's Earth science data collections, in order to accelerate scientific progress for the benefit of society. To access the data through this portal, users must first define their access credentials. To create an EarthData account, follow these steps:

Go to the Earth Nasa website: https://www.earthdata.nasa.gov/. Then, select the option "Use Data" and then "Register". Finally, go to https://urs.earthdata.nasa.gov/.

![earthdata_login](../assets/earthdata_login.png) 

Select the "Register for a profile" option, there choose a username and password. As a suggestion, choose ones that you remember well, as you will need them later. You will also need to complete your profile to complete the registration, where you will be asked for information such as email, country, affiliation, among others. Finally, choose "Register for Earthdata Login".

![earthdata_profile](../assets/earthdata_profile2.png) 

## 3. Data Configuration for Access from Jupyter Notebooks


Now comes the technical part: to access data from Python programs and Jupyter notebooks, it is necessary to save the credentials (from EarthData) in a special file. In this repository you will find a file called .netrc with an example (you can think of it as a template). Open that file and edit the following line:
```

machine urs.earthdata.nasa.gov login {your_username} password {your_password}
```

Then, replace `{your_username}` and `{your_password} `with your account details. Save the file and you're done! You now have everything you need to access Earth observation data through the EarthData portal. ️

To make sure everything is working properly, open the notebook titled `1_getting_started.ipynb` and follow the instructions. With this, you will be able to explore the world of NASA data!




