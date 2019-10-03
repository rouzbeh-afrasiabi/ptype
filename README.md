# ptype-demo

## Initialization
```
ptype = Ptype() 
```
By default, ptype considers the following data types: 'integer', 'string', 'float', 'boolean', 'gender', 'date'. However, this can be extended using the parameter named '_types'.


```
ptype = Ptype(_types={1:'integer', 2:'string', 3:'float', 4:'boolean', 5:'gender', 6:'date-iso-8601', 7:'date-eu', 8:'date-non-std-subtype', 9:'date-non-std', 10:'IPAddress', 11:'EmailAddress') 
```

## Running
```
ptype.set_data(_data_frame=df)
ptype.run_all_columns()
```

## Summarizing the Results

```
ptype.show_results()
```

This prints a summary of the predictions for the columns. Below, we present a section of this, which is generated for the second column named '1':
```
col: 1
	predicted type: integer
	posterior probs:  [1.00000000e+00 0.00000000e+00 4.73609772e-47 0.00000000e+00
 0.00000000e+00 0.00000000e+00 0.00000000e+00 0.00000000e+00
 0.00000000e+00]
	types:  ['integer', 'string', 'float', 'boolean', 'gender', 'date-iso-8601', 'date-eu', 'date-non-std-subtype', 'date-non-std'] 

	some normal data values:  ['101', '102', '103', '104', '106', '107', '108', '110', '113', '115', '118', '119', '121', '122', '125', '128', '129', '134', '137', '142']
	their counts:  [3, 5, 5, 6, 4, 1, 2, 2, 2, 3, 4, 2, 1, 4, 3, 6, 2, 6, 3, 1]
	percentage of normal: 0.8 

	missing values: ['?']
	their counts:  [41]
	percentage of missing: 0.2
```

Alternatively, you can only show the results for the columns that contain missing data or anomalies.
```
column_names = ptype.get_columns_with_missing()
ptype.show_results(column_names)
```

```
column_names = ptype.get_columns_with_anomalies()
ptype.show_results(column_names)
```

## Interactions
