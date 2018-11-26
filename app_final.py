from flask import Flask
import json
import urllib.request
#import urllib
import sys
import time
import re

app = Flask(__name__)
d={}
res =""

@app.route('/<package>/<ver>')
def pack_ver(package,ver):
    global res
    res = ""
    return parse_json(package, ver , 0)

@app.route('/<package>')
def pack(package):
    global res
    res = ""
    return parse_json(package,"latest" , 0)

def check_url(key , value):
    pack_url = "https://registry.npmjs.org/" + key + "/" + value
    request = urllib.request.Request(pack_url)
    try:
        urllib.request.urlopen(request)
        return pack_url
    except urllib.request.HTTPError:
        try:
            pack_url = "https://registry.npmjs.org/" + key + "/latest"
            request = urllib.request.Request(pack_url)
            urllib.request.urlopen(request)
            return pack_url
        except:
            return "bad_url"

			def parse_val(value):
    if value.startswith("~") or value.startswith("^"):
        value = value[1:]
    if value.startswith(">="):
        value = value[3:]
    if value.find("<") > -1:
        value = value[:value.find("<")]
    return value

def parse_json(key, value , depth):
    global d
    global res
    pack_url = check_url(key, value)
    if (pack_url=="bad_url"):
        val = ("url doesn't exist for package: "+key+" and version: "+value)
        res += val
        res += ("<br />")
    else:
        if pack_url in d:
           for dep in d[pack_url]:
                res += ("&#8208" * depth)
                res += (dep[0]+", "+dep[1])
                res += ("<br />")
        else:
            d[pack_url] = []
            with urllib.request.urlopen(pack_url) as url:
                dep_data = json.loads(url.read().decode())

            if "dependencies" in dep_data:
                dependencies = dep_data['dependencies']
                for key, value in dependencies.items():
                    r = re.compile("^[0-9]+[.][0-9]+[.][0-9]+$")
                    if r.match(value) is None:
                        value = parse_val(value)
                    #print("-" * depth + key + ", " + value)
                    #for i in range(depth):
                    res+= ("&#8208"*depth)
                    res+=(key + ", " + value)
                    res+=("<br />")
                    d[pack_url].append((key, value))
                    parse_json(key, value, depth + 1)
    return res

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
