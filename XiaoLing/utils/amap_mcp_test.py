import os, sys
# sys.path.append("../")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.amap import recommend_place

places = recommend_place(
    emotion="我今天很累",
    user_location="北京", purpose="公园,酒吧", amap_key=os.getenv("AMAPKEY"))

print(places)
