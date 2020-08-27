import requests

from etheremon_lib.cache_manager import cache_get_json, cache_set_json


def get_open_sea_total_volume():
	try:
		res = cache_get_json("open_sea_stats")
		if not res:
			r = requests.get(url="https://api.opensea.io/api/v1/asset_contracts/")
			data = r.json()
			total_volume = 0
			items_sold = 0
			for a in data:
				if a.get("symbol", "") in ["MON", "EMOND"]:
					total_volume += a["stats"]["total_volume"]
					items_sold += a["stats"]["items_sold"]
			res = {
				"total_volume": total_volume,
				"items_sold": items_sold,
			}
			cache_set_json("open_sea_stats", res, 1 * 60 * 60)

		return res
	except Exception:
		return 0
