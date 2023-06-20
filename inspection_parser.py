import sys
import os
import xml.etree.ElementTree as parser

def parse_severity(str):
    if str == "error":
        return "ERROR"
    if str == "warning":
        return "WARNING"
    if str == "information":
        return "INFO"
    if str == "style":
        return "WEAK WARNING"
    if str == "performance":
        return "WARNING"
    if str == "portability":
        return "WEAK"
    
if len(sys.argv) != 2:
    print("Wrong number of arguments!", file=sys.stderr)

basePath = os.getcwd()
xml = parser.parse(sys.argv[1])

if len(sys.argv) > 2:
    basePath = os.path.abspath(sys.argv[2])

root = xml.getroot()

errors = root.findall('./errors/error')

##teamcity[inspectionType id='<id>' name='<name>' description='<description>' category='<category>']
for error in errors:
    curr = error.attrib
    print("##teamcity[inspectionType id='{}' name='{}' description='{}' category='{}']".format(curr['id'], curr['id'], curr['msg'].translate(str.maketrans({"'": "|'", "[": "|[", "]": "|]", "|": "||", "\n": "|n"})), curr['severity']))

print()
print()

##teamcity[inspection typeId='<inspection type identity>' message='<instance description>' file='<file path>' line='<line>' additional attribute='<additional attribute>']
for error in errors:
    curr = error.attrib
    file = ""
    line = ""
    locations = error.findall('location')

    msg = curr["msg"].replace('\'','')

    msg = msg.translate(str.maketrans({"'": "|'", "[": "|[", "]": "|]", "|": "||", "\n": "|n"}))

    ##teamcity[buildStatus status='<status_value>' text='{build.status.text} and some aftertext']
    stat = parse_severity(curr["severity"])
    if stat == "ERROR":
        print(" ##teamcity[buildStatus status='FAILURE' text='ERROR and {}']".format(msg))

    

    for location in locations:
        cr = location.attrib
        
        if file == "":
            file = cr["file"].replace(basePath, '')
            line = cr["line"]

        cfile = ""
        if "file0" in cr:
            cfile = cr["file0"].replace(basePath, '') + ":"

        info = ""
        if "info" in cr:
            info = cr["info"].translate(str.maketrans({"'": "|'", "[": "|[", "]": "|]", "|": "||", "\n": "|n"}))

        if "file0" in cr or "info" in cr:
            msg = msg + "|n\t{} {}".format(cfile, info)

    if file == "":
        file = "General CppCheck"
    print("##teamcity[inspection typeId='{}' message='{}' file='{}' line='{}' SEVERITY='{}']'".format(curr['id'], msg, file, line, parse_severity(curr["severity"])))