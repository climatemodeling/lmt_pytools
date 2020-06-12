#!/usr/bin/env python


import json, collections
from bs4 import BeautifulSoup
import sys, re
import numpy as np


gfed4s_regions={
 "BONA": "Boreal North America",
 "TENA": "Temperate North America",
 "CEAM": "Central America",
 "NHSA": "Northern Hemisphere South America",
 "SHSA": "Southern Hemisphere South America",
 "EURO": "Europe",
 "MIDE": "Middle East",
 "NHAF": "Northern Hemisphere Africa",
 "SHAF": "Southern Hemisphere Africa",
 "BOAS": "Boreal Asia",
 "CEAS": "Central Asia",
 "SEAS": "Southeast Asia",
 "EQAS": "Equatorial Asia",
 "AUST": "Australia and New Zealand"
}


Delim = ["", "::", "!!", "||"]
def read_jsontree(models, parentObj, parentScore):

    """
       This json structure is from ILAMB outputs v2.5. The structure looks like as follows:
       {top_metric1:{statistic1+region1(scoreboard1):[score_model1, score_model2, score_model3...], "children":[submetric11:{}, submetric12:{},...]}, 
       top_metric2:{statistic1+region1(scoreboard2):[score_model1, score_model2, score_model3...], "children":[submetric21:{}, submetric22:{},...]},
       ....
       }
       Return the python dictionary relecting the json structure as follows which can be used by the tabulator.js directly
       [ ]
    """
    parentList = []
    parentDict = {}
    for m in parentObj.keys():

        if "Score" not in m and m != "children":
           parentDict['metric'] = m

        childObj = parentObj[m]

        for key in childObj.keys():
            if parentScore != "None" and key == parentScore:
               parentDict['scoreboard'] = key
               for n, mod in enumerate(models):
                   parentDict[str(mod)] = childObj[key][n]

               if "children" in childObj.keys() and childObj["children"] != {}:
                  parentDict["_children"] = []
                  parentDict["_children"] = read_jsontree(models, childObj["children"], key)
               parentList.append(parentDict.copy())

            if parentScore == "None" and key != "children":
               parentDict['scoreboard'] = key

               for n, mod in enumerate(models):
                   parentDict[str(mod)] = childObj[key][n]

               if "children" in childObj.keys() and childObj["children"] != {}:
                  parentDict["_children"] = []
                  parentDict["_children"] = read_jsontree(models, childObj["children"], key)

               parentList.append(parentDict.copy())

    return parentList
        

def FlattenTreeOfTabJson(TabDict, ParentMetric, TreeLevel):


    NewTabDict=[]
    for item in TabDict:

        Fdict={}

        Fdict["metric"] = ParentMetric + Delim[TreeLevel] + item["metric"]
        for key in item.keys():
            if key != "metric" and key != "_children":
               Fdict[key] = item[key]
        NewTabDict.append(Fdict)

        if "_children" in item.keys():
            NextTreeLevel = TreeLevel + 1
            ChdDict = FlattenTreeOfTabJson(item[key], Fdict["metric"], NextTreeLevel)
            NewTabDict = NewTabDict + ChdDict

    return NewTabDict
                   

with open("ilamb_index.html") as fp:
    soup = BeautifulSoup(fp, features="lxml")

for se in soup.find_all('select'):

    if se.get_attribute_list("id")[0] == "RegionOption":
       regStrs = se.get_text()
    if se.get_attribute_list("id")[0] == "ScalarOption":
       scaStrs = se.get_text()

modList=[]
for hd in soup.find_all("th"):

   if hd.get_text() != '':
      modList.append(hd.get_text())

regList = regStrs.strip().split("\n")
scaList = scaStrs.strip().split("\n")

print('xxx', regList)
print('yyy', scaList)


models = modList


metricList=[]
with open("scalars.json", "r") as jn:
    vars=json.load(jn, object_pairs_hook=collections.OrderedDict) 

    metricList = read_jsontree(models, vars, "None")

with open ("my.json", "w") as fw:
     json.dump(metricList, fw)

# the following code is to write the JSON file in the CMEC json schema
# this one could be a __init__ for CMEC json schema
metric_template={"MetricName":{"Name":"", "Abstract":"", "URI":"", "Contact":"forrest AT climatemodeling.org"}, "MetricTree":{}}
region_template={"RegionName":{"LongName":"", "Description":"", "Generator":""}}
model_template={"ModelName":{"Description":"", "Source":"CMIP6 ESGF"}}

DimKws = ["region", "model", "metric", "statistic"]
RltKws = []


DimensionsDict = {}
ResultsDict = {}

DimensionsDict["json_structure"] = DimKws
DimensionsDict["dimensions"] = {}

for dkey in  DimKws:
    DimensionsDict["dimensions"][dkey] = {}

DimensionsDict["dimensions"]["statistic"]["indices"]=[]
DimensionsDict["dimensions"]["statistic"]["short_names"]={}    # shortname : indices


OutputDict = {"DIMENSIONS":DimensionsDict, "RESULTS":ResultsDict}


# now realize the class
FlattenList =  FlattenTreeOfTabJson(metricList, "", 0)

DimDict=OutputDict["DIMENSIONS"]["dimensions"]
RltDict=OutputDict["RESULTS"]

# models 
for m in models:
    modict = model_template.copy()
    modval = modict.pop("ModelName").copy()
    DimDict["model"][m] = modval

# metrics
metrics = []
regions = []
scores = []

for m in FlattenList:
    # region
    temp = m["scoreboard"].split(' ')
    regname = temp[-1].strip()
    scrname = ' '.join(temp[:-1]).strip()

    if regname not in RltDict.keys():
       RltDict[regname] = {}


    regions.append(regname)
    scores.append(scrname)

    # now for metric and RltDict
    metdct = metric_template.copy()
    metval = metdct.pop("MetricName").copy()

    metval["Name"] = m["metric"]

    if "!!" not in m["metric"]:
       metval["Abstract"] = "composite score"
    else:
       metval["Abstract"] = "benchmark score"

    metval["URI"] = ["https://www.osti.gov/biblio/1330803", "https://doi.org/10.1029/2018MS001354"] 

    DimDict["metric"][m["metric"].strip()] = metval

    for key in m.keys():

        if key != "metric" and key != "scoreboard":
           if key not in RltDict[regname].keys():
              RltDict[regname][key] = {}
           else:

              if m["metric"].strip() not in RltDict[regname][key].keys():
                 RltDict[regname][key][m["metric"].strip()] = {}
                 RltDict[regname][key][m["metric"].strip()][scrname] = m[key]
              else:
                 RltDict[regname][key][m["metric"].strip()][scrname] = m[key]

regions = list(set(regions))
scores  = list(set(scores))

#regions
for reg in regions:
    regdct = region_template.copy()
    regval = regdct.pop("RegionName").copy()

    if reg == "global":
       regval["LongName"] = "Global"
       regval["Description"] = "Global"
       print (reg, regval, regdct)

    else:

       print (reg, regdct)
       regval["LongName"] = "South American Amazon"
       regval["Description"] = "South American Amazon"
       print (reg, regval, regdct)
    regval["Generator"] = "From GEED4S definition"
    DimDict["region"][reg]=regval


#indices/scores/
DimDict["statistic"]["indices"] = scores
DimDict["statistic"]["short_names"] = [scr.replace(' ', '') for scr in scores]
    

#print (OutputDict)
with open ("output.json", "w") as fw:
     json.dump(OutputDict, fw)

with open ("flatten.json", "w") as fw:
     json.dump(FlattenList, fw)



#now the json to describe outpouts (html and nc files)
#this json file fromat might be changed based on the link templates as follows:
#   top_output_directory/$metric/$submetric/$benchmark/$$benchmark.html?model=$model=$modelname&$region=$regionname
#   top_output_directory/$metric/$submetric/$benchmark/$$benchmark.html#relationships

DesOutput={}
DesOutput["index"] = []


FindPdict={}
for m in FlattenList:
    if '!!' in m["metric"]:
        metsname = m["metric"].replace(' ', '') + '__' + m["scoreboard"]
        metsnam2 = m["metric"].replace(' ', '')
        DesOutput["index"].append(metsname)
        DesOutput["html::"+metsname] = {}

        for mkey in m.keys():
            if mkey != "metric" and mkey != "scoreboard":
               DesOutput["index"].append(metsname+ '_'+mkey)
               DesOutput["data::"+metsname+'_'+mkey] = {}
         
        filename = metsname
        for d in Delim[1:]:
            filename = filename.replace(d, '/');

        if "Relationships" not in m["metric"]:
            DesOutput["html::"+metsname]["filename"] = filename + "/" + filename.split('/')[-1] + ".html"

            for mkey in m.keys():
                if mkey != "metric" and mkey != "scoreboard":
                   DesOutput["data::"+metsname+'_'+mkey]["filename"] = filename + "/" + filename.split('/')[-1] + "_" + mkey + ".nc"
            

            FindPdict[metsnam2.split('::')[-1].replace('!!','/')] = metsnam2.split('::')[0]
        else:
            temp = metsname.split('::')[-1].split('!!')[0]
            link = temp + '/' + temp.split('/')[-1] + ".html#Relationships"
            print (temp)
            DesOutput["html::"+metsname]["filename"] = link

            for mkey in m.keys():
                if mkey != "metric" and mkey != "scoreboard":
                   DesOutput["data::"+metsname+'_'+mkey]["filename"] = temp + '/' + temp.split('/')[-1] + "_" + mkey + ".nc"

        DesOutput["html::"+metsname]["long_name"] = filename.replace('/', ' ')
        DesOutput["html::"+metsname]["Description"] = "Benchmark page contains a table of absoult scores, geographical distribution maps, Taylor Diagram etc." 


#print (FindPdict)

for key in DesOutput.keys():
    if "html::Relationships" in key:
       DesOutput[key]["filename"] = FindPdict[key.split('::')[-1].split('::')[-1].split('!!')[0]] + '/' + DesOutput[key]["filename"]

    if "data::Relationships" in key:
       DesOutput[key]["filename"] = FindPdict[key.split('::')[-1].split('::')[-1].split('!!')[0]] + '/' + DesOutput[key]["filename"]


num_html=0
num_data=0

for key in DesOutput.keys():
    if 'html' in key:
       num_html = num_html + 1

    if 'data' in key:
       num_data = num_data + 1
print (len(DesOutput["index"]))
print (len(set(DesOutput["index"])))
print (num_html, num_data)
print (len(FlattenList))
#print (DesOutput)

with open ("outputdes.json", "w") as fw:
     json.dump(DesOutput, fw)
            
