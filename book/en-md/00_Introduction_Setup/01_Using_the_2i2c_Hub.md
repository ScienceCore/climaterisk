---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Using the 2i2c Hub

<!-- #region jupyter={"source_hidden": true} -->
This notebook lays out instructions to log into the cloud infrastructure ([JupyterHub](https://jupyter.org/hub)) provided by [2i2c](https://2i2c.org) for this tutorial.

**You won't be able to complete this step until the actual day of the tutorial (you'll get the password then).**
<!-- #endregion -->

## 1. Logging into the 2i2c Hub

<!-- #region jupyter={"source_hidden": true} -->
To login to the JupyterHub provided by 2i2c, follow these steps:
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
1. **Navigate to the 2i2c Hub:** Point your web browser to [this link](https://climaterisk.opensci.2i2c.cloud).

2. **Log in with your Credentials:**

  + **Username:** Feel free to choose any username you like.  We suggest using your GitHub username to avoid conflicts.
  + **Password:** *You'll receive the password on the day of the tutorial*.

![2i2c_login](../../assets/img/2i2c_login.png)

3. **Logging In:**

The login process might take a few minutes, especially if a new virtual workspace needs to be created just for you. 
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
![start_server2](../../assets/img/start_server_2i2c.png)
<!-- #endregion -->

<!-- #region jupyter={"source_hidden": true} -->
* **What to Expect:**

By default,  logging into [`https://climaterisk.opensci.2i2c.cloud`](https://climaterisk.opensci.2i2c.cloud) automatically clones a repository to work in. If the login is successful, you will see the following screen and are ready to start working. 

![work_environment_jupyter_lab](../../assets/img/work_environment_jupyter_lab.png) 

**Notes:** Any files you work on will persist between sessions as long as you use the same username when logging in.
<!-- #endregion -->

## 2. Configuring the Cloud Environment to Access NASA EarthData from Python

<!-- #region jupyter={"source_hidden": true} -->
To access NASA's EarthData products from Python programs or Jupyter notebooks, it is necessary to save your NASA EarthData credentials in a special file called `.netrc` in your home directory.

+ You can create this file by executing the script `make_netrc.py` in a terminal:

  ```bash
  $ python make_netrc.py
  ```

   You can also choose to execute this script within this Jupyter notebook by executing the Python cell below (using the `%run` magic).

  Some caveats:
  + The script won't execute if `~/.netrc` exists already. You can delete that file or rename it if you want to preserve the credentials within.
  + The script prompts for your NASA EarthData username & password, so watch for the prompt if you execute it from a Jupyter notebook.
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%run make_netrc.py
```

<!-- #region jupyter={"source_hidden": true} -->
+ Alternatively, you can create a file called `.netrc` in your home folder (i.e., `~/.netrc`) with content as follows:
   ```
   machine urs.earthdata.nasa.gov login USERNAME password PASSWORD
   ```
   Of course, you would replace `USERNAME` and `PASSWORD` in your `.netrc` file with your actual NASA EarthData account details. Once the `.netrc` file is saved with your correct credentials, it's good practice to restrict access to the file:
   ```bash
   $ chmod 600 ~/.netrc
   ```
<!-- #endregion -->

## 3. Verifying Access to NASA EarthData Products

<!-- #region jupyter={"source_hidden": true} -->
To make sure everything is working properly, execute the script `test_netrc.py`:

```bash
$ python test_netrc.py
```

Again, you can execute this directly from this notebook using the Python cell below:
<!-- #endregion -->

```python jupyter={"source_hidden": true}
%run test_netrc.py
```

<!-- #region jupyter={"source_hidden": true} -->
If that worked smoothly, you're done! You now have everything you need to explore NASA's Earth observation data through the EarthData portal!
<!-- #endregion -->

---
