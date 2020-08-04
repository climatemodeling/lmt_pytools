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


Fncmip5Json = "cmip5_historical_ENSO_perf_v20200427_allModels_allRuns.json"
Fncmip6Json = "cmip6_historical_ENSO_perf_v20200427_allModels_allRuns.json"

structure = ['model', 'ensemble', 'metric']
#metrics = ['EnsoSstLonRmse', 'EnsoAmpl', 'EnsoSeasonality', 'EnsoPrMapDjfRmse', 'EnsoPrMapJjaRmse', 'EnsoSstMapDjfRmse', 'EnsoSstMapJjaRmse'];

metrics = ['BiasPrLatRmse' ,'BiasPrLonRmse' ,'BiasSshLatRmse' ,'BiasSshLonRmse' ,'BiasSstLatRmse' ,'BiasSstLonRmse'
,'BiasTauxLatRmse' ,'BiasTauxLonRmse' ,'EnsoAmpl' ,'EnsoDuration' ,'EnsoSeasonality' ,'EnsoSstDiversity_1'
,'EnsoSstDiversity_2' ,'EnsoSstLonRmse' ,'EnsoSstSkew' ,'EnsoSstTsRmse' ,'NinoSstDiversity_1' ,'NinoSstDiversity_2'
,'SeasonalPrLatRmse' ,'SeasonalPrLonRmse' ,'SeasonalSshLatRmse' ,'SeasonalSshLonRmse' ,'SeasonalSstLatRmse' ,'SeasonalSstLonRmse' 
,'SeasonalTauxLatRmse' ,'SeasonalTauxLonRmse']

defaultkeys = {'model': DictKeyWords['model'], 'ensemble': DictKeyWords['other'], 'metric': DictKeyWords['metric']}

cmecJson = CMECJsonSchema('v1', 'PMP')

for i, MipJson in enumerate([Fncmip5Json, Fncmip6Json]):
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
    if i == 0:
       cJson.set_dimensions(structure, dimensions, defaultkeys, 'CMIP5 ESGF')
    else:
       cJson.set_dimensions(structure, dimensions, defaultkeys, 'CMIP6 ESGF')
    DimsFilter = {'model':[], 'ensemble':[], 'metric':metrics}
    cJson.set_results(VarJsonCmip5, DimsFilter)

    if i == 0:
       cmecJson = cJson
    else:
       cmecJson.merge(cJson)
    
with open ("pmp_enso_perf.json", "w") as fw:
    json.dump(cmecJson.CMECJsonDict, fw)
