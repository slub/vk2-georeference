# API ElasticSearch

The following document contains an example map record used by the `Virtual Map Forum 2.0`. For information regarding the communication with `elasticsearch` see the [documentation](https://www.elastic.co/guide/index.html).

```json
{  
	"dataid":"df_dk_0010001_5248_1933",
	// The clippolygon describe the exact cutline regarding the original map
    "clippolygon":[  
    	[  
        	13.664763004671837,
            50.69888411172953
		],
        [  
            13.665145761915698,
			50.7987156646713
        ],
        [  
            13.831402503802245,
			50.798877674967
        ],
        [  
            13.831791379133199,
    		50.69872776623451
        ],
        [  
        	13.664763004671837,
            50.69888411172953
		]
	],
    "description":"Altenberg. - Umdr.-Ausg., aufgen. 1910, hrsg. 1912, au\u00dfers\u00e4chs. Teil 1919, bericht. 1923, einz. Nachtr. 1933. - 1:25000. - Leipzig, 1939. - 1 Kt.",
	"denominator":25000,
    "zoomify":"http://fotothek.slub-dresden.de/zooms/df/dk/0010000/df_dk_0010001_5248_1933/ImageProperties.xml",
    "maptype":"M",
    "org":"http://fotothek.slub-dresden.de/fotos/df/dk/0010000/df_dk_0010001_5248_1933.jpg",
    "keywords":"Druckgraphik;Lithografie & Umdruck",
    "titlelong":"Me\u00dftischblatt 119 : Altenberg, 1939",
    "id":10001387,
    "plink":"http://digital.slub-dresden.de/id335921620",
    "online-resources":[  
    	{  
        	"url":"http://digital.slub-dresden.de/id335921620",
            "type":"Permalinkk"
		},
        {  
        	"url":"http://digital.slub-dresden.de/oai:de:slub-dresden:vk:id-10001387",
            "type":"Permalink"
		},
        {  
        	"url":"http://localhost/cgi-bin/dynamic-ows?map=10001387&SERVICE=WMS&VERSION=1.0.0&REQUEST=GetCapabilities",
            "type":"WMS"
		},
        {  
        	"url":"http://localhost/cgi-bin/mtbows?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=Historische Messtischblaetter&TRANSPARENT=true&FORMAT=image/png&STYLES=&SRS=EPSG:4314&BBOX=13.6666660309,13.8333339691,13.8333339691,50.8000030518&WIDTH=256&HEIGHT=256&TIME=1939",
            "type":"Time-enabled WMS"
		}
	],
    "tms":"http://vk2-cdn{s}.slub-dresden.de/tms/mtb/df_dk_0010001_5248_1933",
    "thumb":"http://fotothek.slub-dresden.de/thumbs/df/dk/0010000/df_dk_0010001_5248_1933.jpg",
    "title":"Altenberg",
    // The geometry represents the boundingbox of the georeferenced image. It is therefore a rectangle. 
    "geometry":{  
    	"type":"polygon",
        "coordinates":[  
        	[  
            	[  
                    13.6649521132183,
                    50.6988045811759
                ],
                [  
                    13.6649521132183,
                    50.7987980293604
                ],
                [  
                    13.8315992376244,
                    50.7987980293604
                ],
                [  
                    13.8315992376244,
                    50.6988045811759
                ],
                [  
                    13.6649521132183,
                	50.6988045811759
                ]
			]
		]
	},
    "georeference":true,
    "time":"1939-1-1"
},
```

