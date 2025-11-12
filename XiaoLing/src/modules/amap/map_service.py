import requests
import random

def recommend_place(emotion: str, user_location: str, purpose: str, amap_key: str = None):
    """
    调用高德API（或使用模拟数据）推荐地点
    """
    # 若未提供真实key，使用模拟数据
    if amap_key is None:
        mock_places = {
            "安静": ["书亦烧仙草·图书店店", "浮光咖啡", "城市森林公园"],
            "热闹": ["星光夜市", "环城步行街", "音乐酒吧·LiveHouse"],
            "咖啡": ["Seesaw Coffee", "Manner Coffee", "Blue Bottle Coffee"],
            "公园": ["望京公园", "世纪公园", "青年湖公园"]
        }
        tag = "安静" if "烦" in emotion or "累" in emotion else "热闹"
        return random.sample(mock_places.get(tag, mock_places["安静"]), 3)
    
    # 调用高德 Place API
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": amap_key,
        "keywords": purpose,
        "city": user_location,
        "children": 1,
        "offset": 5,
        "page": 1,
        "extensions": "base"
    }
    r = requests.get(url, params=params)
    data = r.json()
    
    pois = data.get("pois", [])
    pois_info = []
    for poi in pois:
        loc = poi.get("location", "")
        if "," in loc:
            lng, lat = loc.split(",")
        else:
            lng, lat = "", ""
        pois_info.append(
            {
                "name": poi.get("name"),
                "address": poi.get("address"),
                "type": poi.get("type"),
                "lat": lat,
                "lng": lng,
            }
        )
    return pois_info if pois else ["暂时找不到合适的地方～"]
