RAW = data/raw/yellow_tripdata_2019-01.csv
URL = https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-01.csv.gz

data: $(RAW)

$(RAW):
	@mkdir -p $(dir $@)
	curl -L $(URL) | gzip -d > $@