touch ~/.netrc | chmod og-rw ~/.netrc | echo machine urs.earthdata.nasa.gov >> ~/.netrc
echo login ${EARTHDATA_USERNAME} >> ~/.netrc | echo password ${EARTHDATA_PASSWORD} >> ~/.netrc