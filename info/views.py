from django.shortcuts import render, HttpResponse, redirect
import requests
import xml.etree.ElementTree as ET

def routeColorAndType(typeCodeStr):
    text = "시내버스"
    color = "#ffffff"
    textColor = "#ffffff"

    typeCode = int(typeCodeStr)

    if typeCode == 11 or typeCode == 21:
        text = "직행좌석버스"
        color = "#EE2737"
    elif typeCode == 15:
        text = "경기순환버스"
        color = "#EE2737"
    elif typeCode == 12 or typeCode == 22:
        text = "일반좌석버스"
        color = "#0085CA"
    elif typeCode == 13 or typeCode == 23:
        text = "일반버스"
        color = "#009775"
    elif typeCode == 30:
        text = "마을버스"
        color = "#F2A000"
    elif typeCode == 15:
        text = "맞춤형버스"
        color = "#B62367"
    elif typeCode == 14:
        text = "광역급행버스 (M버스)"
        color = "#000000"
        textColor = "#00BFFF"
    elif typeCode == 41 or typeCode == 42 or typeCode == 43:
        text = "시외버스"
        color = "#8800ad"
    elif typeCode == 51 or typeCode == 52 or typeCode == 53:
        text = "공항버스"
        color = "#0085CA"

    return {
        "type": text,
        "bgColor": color,
        "txtColor": textColor
    }


# Create your views here.
def index(req):
    return render(req, "index.html")

def search(req):
    q = req.GET.get('q', 'NULL値なし값없음')
    if q == 'NULL値なし값없음' or q == '':
        return redirect('/')
    
    busRes = requests.get(f"http://apis.data.go.kr/6410000/busrouteservice/getBusRouteList?serviceKey=T8aTxlHEaonYss%2BarjTmxYdFTEk5y%2FGWpOFXPibDQ7a98I%2Fjimly0PjpIL01pVFNcN3tNARXitmc58WsBBC%2FUg%3D%3D&keyword={q}")
    busXml = ET.fromstring(busRes.text)
    try:
        busInfos = busXml.find("msgBody").findall("busRouteList")
    except:
        busInfos = []

    busRouteList = []

    for busInfo in busInfos:
        forUI = routeColorAndType(busInfo.findtext("routeTypeCd"))
        busRoute = {
            "routeID": busInfo.findtext("routeId"),
            "routeNm": busInfo.findtext("routeName"),
            "region": busInfo.findtext("regionName"),
            "type": forUI["type"],
            "bgColor": forUI["bgColor"],
            "txtColor": forUI["txtColor"]
        }
        busRouteList.append(busRoute)

    stopRes = requests.get(f"http://apis.data.go.kr/6410000/busstationservice/getBusStationList?serviceKey=T8aTxlHEaonYss%2BarjTmxYdFTEk5y%2FGWpOFXPibDQ7a98I%2Fjimly0PjpIL01pVFNcN3tNARXitmc58WsBBC%2FUg%3D%3D&keyword={q}")
    stopXml = ET.fromstring(stopRes.text)
    try:
        stopInfos = stopXml.find("msgBody").findall("busStationList")
    except:
        stopInfos = []

    stopList = []

    for stopInfo in stopInfos:
        stop = {
            'stopID': stopInfo.findtext("stationId"),
            'stopNm': stopInfo.findtext("stationName"),
            'stopARS': stopInfo.findtext("mobileNo"),
            'region': stopInfo.findtext("regionName"),
        }
        stopList.append(stop)

    context = {
        'q': q,
        'busLen': len(busInfos),
        'buses': busRouteList,
        'stopLen': len(stopInfos),
        'stops': stopList
    }
    return render(req, "search.html", context)

def bus(req):
    id = req.GET.get('id', 'NULL値なし값없음')
    if id == 'NULL値なし값없음' or id == '':
        return redirect('/')
    try:
        busRes = requests.get(f"http://apis.data.go.kr/6410000/busrouteservice/getBusRouteInfoItem?serviceKey=T8aTxlHEaonYss%2BarjTmxYdFTEk5y%2FGWpOFXPibDQ7a98I%2Fjimly0PjpIL01pVFNcN3tNARXitmc58WsBBC%2FUg%3D%3D&routeId={id}")
        busXml = ET.fromstring(busRes.text).find("msgBody").find("busRouteInfoItem")
        forUI = routeColorAndType(busXml.findtext("routeTypeCd"))

        stopRes = requests.get(f"http://apis.data.go.kr/6410000/busrouteservice/getBusRouteStationList?serviceKey=T8aTxlHEaonYss%2BarjTmxYdFTEk5y%2FGWpOFXPibDQ7a98I%2Fjimly0PjpIL01pVFNcN3tNARXitmc58WsBBC%2FUg%3D%3D&routeId={id}")
        stopXml = ET.fromstring(stopRes.text).find("msgBody").findall("busRouteStationList")
        stops = []

        for stp in stopXml:
            stop = {
                "stopId": stp.findtext("stationId"),
                "stopNm": stp.findtext("stationName"),
                "stopARS": stp.findtext("mobileNo"),
                "region": stp.findtext("regionName"),
                "isTurn": stp.findtext("turnYn")
            }
            stops.append(stop)

        context = {
            "type": forUI["type"],
            "bgColor": forUI["bgColor"],
            "txtColor": forUI["txtColor"],
            "routeNm": busXml.findtext("routeName"),
            "region": busXml.findtext("regionName"),
            "companyNm": busXml.findtext("companyName"),
            "companyTel": busXml.findtext("companyTel"),
            "startFirst": busXml.findtext("upFirstTime"),
            "startLast": busXml.findtext("upLastTime"),
            "endFirst": busXml.findtext("downFirstTime"),
            "endLast": busXml.findtext("downLastTime"),
            "minInter": busXml.findtext("peekAlloc"),
            "maxInter": busXml.findtext("nPeekAlloc"),
            "startNm": busXml.findtext("startStationName"),
            "startARS": busXml.findtext("startMobileNo"),
            "endNm": busXml.findtext("endStationName"),
            "endARS": busXml.findtext("endMobileNo"),
            "stops": stops
        }
    except:
        HttpResponse("<script>window.close()</script>")

    if len(str(context["endARS"])) == 4 and context["endARS"]:
        context["endARS"] = f"0{context["endARS"]}"
    if len(str(context["startARS"])) == 4 and context["startARS"]:
        context["startARS"] = f"0{context["startARS"]}"

    return render(req, "bus.html", context)

def stop(req):
    id = req.GET.get('id', 'NULL値なし값없음')
    if id == 'NULL値なし값없음' or id == '':
        return redirect('/')

    return render(req, "stop.html")