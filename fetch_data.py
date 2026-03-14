# Download real SST data (about 10MB)
import urllib.request
url = "https://psl.noaa.gov/repository/entry/get/ersst.mnmean.nc"
urllib.request.urlretrieve(url, "sst_data.nc")