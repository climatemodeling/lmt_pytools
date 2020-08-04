#!/usr/bin/python


from cmec_json_schema import CMECJsonSchema
import json

def ReadEnsoJson (JsonFile):
    with open (JsonFile, 'r') as fp:
         VarJson = json.load(fp)
    return VarJson

DictKeyWords={"model"     : ["Description", "Source"],  
              "region"    : ["LongName", "Description", "Generator"],
              "metric"    : ["Name", "Abstract", "URI", "Contact"],
              "other"     : ["Name"],
              "statistic" : []}


Fncmip5Json = "cmip5_historical_ENSO_tel_v20200427_allModels_allRuns.json"
Fncmip6Json = "cmip6_historical_ENSO_tel_v20200427_allModels_allRuns.json"

structure = ['model', 'ensemble', 'metric']
metrics = ['EnsoSstLonRmse', 'EnsoAmpl', 'EnsoSeasonality', 'EnsoPrMapDjfRmse', 'EnsoPrMapJjaRmse', 'EnsoSstMapDjfRmse', 'EnsoSstMapJjaRmse'];
defaultkeys = {'model': DictKeyWords['model'], 'ensemble': DictKeyWords['other'], 'metric': DictKeyWords['metric']}

cmecJson = CMECJsonSchema('v1', 'PMP')

for MipJson in [Fncmip5Json, Fncmip6Json]:
    VarJsonCmip5 = ReadEnsoJson (MipJson)
    
    # find all the keys:
    models = VarJsonCmip5['RESULTS']['model'].keys()
    
    ensembles = []
    metrics = []
    for md in models:
        ensembles.extend(VarJsonCmip5['RESULTS']['model'][md].keys())
        for en in VarJsonCmip5['RESULTS']['model'][md].keys():
            metrics.extend(VarJsonCmip5['RESULTS']['model'][md][en]['value'].keys())
    
    ensembles = list(set(ensembles))
    metrics = list(set(metrics))
    print (models)
    print (ensembles)
    print (metrics)
    dimensions = [models, ensembles, metrics]
    
    cJson = CMECJsonSchema('v1', 'PMP')
    cJson.set_dimensions(structure, dimensions, defaultkeys, 'CMIP5 ESGF')
    DimsFilter = {'model':[], 'ensemble':[], 'metric':metrics}
    cJson.set_results(VarJsonCmip5, DimsFilter)
    cmecJson.merge(cJson)
    
with open ("pmp_enso_tel.json", "w") as fw:
    json.dump(cmecJson.CMECJsonDict, fw)
