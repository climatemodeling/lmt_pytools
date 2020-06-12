Conversions of the ILAMB, Tabulator and CMEC JOSN formats

***Purpuse***: Converting a JSON in the ILAMB format to the Tabulator and CMEC formats that can be used by 
LMT unified dashboard directly.


 - read_jsontree: read the ILAMB JSON file and convert to a JSON file in the Tabulator format
 - FlattenTreeOfTabJson: flatten the tree structure of the Tabulator JSON file
 - main: read an ILAMB JSON file, convert it to the Tabulator JSON file, flatten it and further 
         convert it the CMEC JSON file
