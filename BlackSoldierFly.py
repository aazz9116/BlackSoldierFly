import network,time,dht,socket,uselect,os,urequests,usocket,ujson
from machine import Pin,PWM
value_1=0
value_2=0
value_3="2"
value_4=""
Rled=PWM(Pin(12))
Bled=PWM(Pin(15))
Gled=PWM(Pin(13))
relay_01=Pin(14,Pin.OUT,value=1)

class Response:
 def __init__(self, f):
     self.raw = f
     self.encoding = "utf-8"
     self._cached = None

 def close(self):
     if self.raw:
         self.raw.close()
         self.raw = None
     self._cached = None

 @property
 def content(self):
     if self._cached is None:
         try:
             self._cached = self.raw.read()
         finally:
             self.raw.close()
             self.raw = None
     return self._cached

 @property
 def text(self):
     return str(self.content, self.encoding)

 def json(self):
     import ujson
     return ujson.loads(self.content)
 def request(method, url, data=None, json=None, headers={}, stream=None):
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    s = usocket.socket(ai[0], ai[1], ai[2])
    try:
        s.connect(ai[-1])
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
        if not "Host" in headers:
            s.write(b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")
        if json is not None:
            assert data is None
            import ujson
            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")
        if data:
            s.write(b"Content-Length: %d\r\n" % len(data))
        s.write(b"\r\n")
        if data:
            s.write(data)

        l = s.readline()
        print(l)
        l = l.split(None, 2)
        status = int(l[1])
        reason = ""
        if len(l) > 2:
            reason = l[2].rstrip()
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            #print(l)
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
            elif l.startswith(b"Location:") and not 200 <= status <= 302:
                raise NotImplementedError("Redirects not yet supported")
    except OSError:
        s.close()
        raise

    resp = Response(s)
    resp.status_code = status
    resp.reason = reason
    return resp

 def get(url, **kw):
    return Response.request("GET", url, **kw)


def Openn_cmd(temp):
     if(temp==1):
       relay_01.value(1)
     if(temp==0):
       relay_01.value(0)
def Openn_dht():
      value_4="0"
      sensor = dht.DHT11(Pin(0))
      sensor.measure()
      value_1=sensor.temperature()
      value_2=sensor.humidity()
      if(value_1<=27):
        Openn_cmd(0)
        value_4="1"
        temp_temper="{0}°C 溫度太低".format(value_1)
        print(temp_temper)
      elif(value_1>27 and value_1<=33):
        G=1000
        RGB_led(R,G,B)
        #print(f"{temp_temper}°C 溫度過低2")
        temp_temper="{0}°C 溫度正常".format(value_1)
        value_4=""
        Openn_cmd(1)
        print(temp_temper)
      else:
        temp_temper="{0}°C 溫度過高".format(value_1)
        value_4=""
        print(temp_temper)
    
      if(value_2<60):
        temp_humi="{0} % 過於乾燥".format(value_2)
        #value_4=""
        print(temp_humi)
      elif(value_2 >=60 and value_2<90):
        temp_humi="{0} % 濕度正常".format(value_2)
        #value_4=""
        print(temp_humi)
      else:
        temp_humi="{0} % 過於潮濕".format(value_2)
        #value_4=""
        print(temp_humi)
      Response.get("https://script.google.com/macros/s/AKfycbz0pL0Ck3AO9eOjFEOjRDWIP6qZCoXjRzTkBfdOxdBnAqsVXYof/exec?value_1="+str(value_1)+'&value_2='+str(value_2)+'&value_3='+value_3+'&value_4='+value_4)
      #res.text# json()載入並解析 JSON 格式資料
      print("資料上傳成功")
print("啟動中...")
sta_if = network.WLAN(network.STA_IF)     # 取得無線網路介面
sta_if.active(True)                       # 啟用無線網路
sta_if.connect('AP_Name', 'AP_Password')  # 連結無線網路
while not sta_if.isconnected():
    pass #等待無線網路連上
print("Wifi 連線成功")
con_temp=0
con_temp2=0
con2_temp=0
con2_temp2=0 
while True:
    res = Response.get("https://script.google.com/macros/s/AKfycbz0pL0Ck3AO9eOjFEOjRDWIP6qZCoXjRzTkBfdOxdBnAqsVXYof/exec?value_re=4")#持續接收伺服器端指令
    j = res.text #json()載入並解析 JSON 格式資料 .text讀取所有回傳
    str1 = "userHtml"
    nPos = ""
    nPos1 = ""
    nPos = j.index(str1)
    nPos=j[nPos+17:nPos+18] #鎖定控制指令位子並存取
    j=""
    j = res.text
    nPos2 = j.index(str1)
    nPos2=j[nPos2+18:nPos2+19]
    print("nPos1:"+nPos+"/nPos2:"+nPos2)#17
    con_temp=nPos
    con2_temp=nPos2
    if con_temp!=con_temp2 : #判斷指令是否更新
        if nPos!=None:
            print("伺服器回應: "+nPos)
            if nPos=="5":
                Openn_cmd(0)
            elif nPos=="6":
                Openn_cmd(1)
            else :
                print("伺服器指令格式錯誤:未執行")
        else:
            print("沒有收到回應")
    else:
        print("控制指令未更新")
        if nPos2=="0":
            print("執行常駐程序")
            Openn_dht()
    res=""
    j=""
    con_temp2=nPos #儲存紀錄本次執行的指令
    con2_temp2=nPos2
    time.sleep(10)    
Openn_cmd(1)






