#!/usr/bin/evn python


class CMECJsonSchema:

      def __init__(self, jsonschemaver, nameofbenchmarkpkg):
          self.CMECJsonDict = {}
          self.CMECJsonDict['SCHEMA'] = {'name': 'CMEC', 'version': jsonschemaver, 'package': nameofbenchmarkpkg}
          self.CMECJsonDict['DIMENSIONS'] = {}
          self.CMECJsonDict['DIMENSIONS']['json_structure'] = []
          self.CMECJsonDict['DIMENSIONS']['dimensions'] = {}
          self.CMECJsonDict['RESULTS'   ] = {}

      def set_dimensions(self, structure, dimensions, defaultkeys, mipsource):
          self.CMECJsonDict['DIMENSIONS']['json_structure'] = structure
          for i, st in enumerate(structure):
              self.CMECJsonDict['DIMENSIONS']['dimensions'][st] = {}
              for dk in dimensions[i]:
                  self.CMECJsonDict['DIMENSIONS']['dimensions'][st][dk] = {}
                  self.CMECJsonDict['DIMENSIONS']['dimensions'][st][dk].fromkeys(defaultkeys[st], '')

                  if 'Name' in defaultkeys[st]:
                      self.CMECJsonDict['DIMENSIONS']['dimensions'][st][dk]['Name'] = dk
                  if 'Source' in defaultkeys[st]:
                      self.CMECJsonDict['DIMENSIONS']['dimensions'][st][dk]['Source'] = mipsource
                      
      def set_results(self, VarJson, Filter):
          import math
          RltDict = {}
          for md in VarJson["RESULTS"]["model"].keys():
              if len(Filter['model']) > 0:
                 if md not in Filter['model']:
                    continue
                   
              RltDict[md] = {}
              for en in VarJson["RESULTS"]["model"][md].keys():

                  if not 'f' in en:
                     ens = en + 'f1'
                  else:
                     ens = en

                  if len(Filter['ensemble']) > 0:
                     if en not in Filter['ensemble']:
                        continue

                  RltDict[md][ens] = {}
                  for mt in VarJson["RESULTS"]["model"][md][en]["value"].keys():

                      #print ( md, en, mt, VarJson["RESULTS"]["model"][md][en]["value"][mt]["metric"].keys() )
                      if len(Filter['metric']) > 0:
                         if mt not in Filter['metric']:
                            continue
                      try:
                          RltDict[md][ens][mt] = VarJson["RESULTS"]["model"][md][en]["value"][mt]["metric"]["Tropflux"]["value"]
                      except:
                          try:
                             RltDict[md][ens][mt] = VarJson["RESULTS"]["model"][md][en]["value"][mt]["metric"]["Tropflux_ERA-Interim"]["value"]
                          except:

                             try: 
                                RltDict[md][ens][mt] = VarJson["RESULTS"]["model"][md][en]["value"][mt]["metric"]["ERA-Interim"]["value"]
                             except:
                                RltDict[md][ens][mt] = VarJson["RESULTS"]["model"][md][en]["value"][mt]["metric"]["AVISO"]["value"]
 
                      if not RltDict[md][ens][mt] or math.isnan(RltDict[md][ens][mt]):

                         RltDict[md][ens][mt] = -999.0

          self.CMECJsonDict["RESULTS"] = RltDict

          pass

      def merge(self, OtherJson):
         
          if self.CMECJsonDict['SCHEMA'] != OtherJson.CMECJsonDict['SCHEMA']:
             print ("the two jsons cannot be merged due to differences in their schema")
             sys.exit()
             
          if self.CMECJsonDict['DIMENSIONS']['json_structure'] != OtherJson.CMECJsonDict['DIMENSIONS']['json_structure']:

             print (self.CMECJsonDict['DIMENSIONS']['json_structure'])
             print (OtherJson.CMECJsonDict['DIMENSIONS']['json_structure'])
             print ("the two jsons cannot be merged due to differences in their json_structure")
             sys.exit()

          adict = self.CMECJsonDict
          bdict = OtherJson.CMECJsonDict
          adict["RESULTS"].update(bdict["RESULTS"])

          for dim in self.CMECJsonDict['DIMENSIONS']['json_structure']:
              for k in bdict["DIMENSIONS"]["dimensions"][dim].keys():
                  adict["DIMENSIONS"]["dimensions"][dim][k] = bdict["DIMENSIONS"]["dimensions"][dim][k]


          self.CMECJsonDict = adict
