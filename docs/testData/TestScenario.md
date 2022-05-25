# Test Data

The Cotton & Leather supply chain is long and complex. Sample (test) data can provide a useful reference to help ensure that implementers have a good shared understanding of their part in the supply chain and what that means for the data they will issue and/or consume.  This page provides a sample tracability graph from grower to garment together with sample data for each step in the chain.

# Traceability Scanario

The graph shows an example pathway from grower to consumer and includes all the steps in the cotton supply chain. 

  * Parties (ie stakeholder types) are represented as elipses and things (eg a shipment of goods) are represented as rounded rectangles. Links between parties and/or things are supply chain events.
  * Each supply chain event is reporesented by an EPCIS event (yellow) and MAY also include a referenced trade document (green) and/or a referenced certificate (blue).
  * The parties with the anchor icon are "trust anchors" such as national regulators or accreditation authorities. When claims (eg "orgabic") can be traced to trust anchors then the integroty of the claim is improved.  for example a self-assessed claim is weakter than an intependently certified claim. But even a certified claim is stronger when the inspector / auditor is accredited under a well goverened national scheme.
  * The graph does not show various forks and joins that would exist in the real world.  For example the pallet containing cotton bales that is shipped by the trader may include bales from more than one different grower / ginning mill. There are many points of aggregation in a real chain where multiple sources combine into one item (eg multiple blaes in a pallet) - or where one item (eg a 100m bolt of woven cloth may be used on multiple different garmet types)


!sustainabilitytrustgraph.png

|Step|Event Type|BizStep|Location|Source Party|Dest Party|Input Items|Output Items|Ref Doc|Ref Cert|JSON Sample|
|--|--|--|--|--|--|--|--|--|--|--|
| 1 |  |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |
| 4 | transaction | shipping | https://plus.codes/4RWC3600+ | did:dns:fertilizers.com| did:dns:riverinacotton.com.au | epc:106141412345678908 |  | desadv:12345 |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |  |  |  |
| 8 |  |  |  |  |  |  |  |  |  |  |
| 9 |  |  |  |  |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |  |  |  |  |
| 11 |  |  |  |  |  |  |  |  |  |  |
| 12 |  |  |  |  |  |  |  |  |  |  |
| 13 |  |  |  |  |  |  |  |  |  |  |
| 14 |  |  |  |  |  |  |  |  |  |  |
| 16 |  |  |  |  |  |  |  |  |  |  |
| 17 |  |  |  |  |  |  |  |  |  |  |
| 18 |  |  |  |  |  |  |  |  |  |  |
| 19 |  |  |  |  |  |  |  |  |  |  |
| 20 |  |  |  |  |  |  |  |  |  |  |
| 21 |  |  |  |  |  |  |  |  |  |  |
| 22 |  |  |  |  |  |  |  |  |  |  |
| 23 |  |  |  |  |  |  |  |  |  |  |
| 24 |  |  |  |  |  |  |  |  |  |  |
| 26 |  |  |  |  |  |  |  |  |  |  |
| 27 |  |  |  |  |  |  |  |  |  |  |
| 28 |  |  |  |  |  |  |  |  |  |  |
| 29 |  |  |  |  |  |  |  |  |  |  |
| 30 |  |  |  |  |  |  |  |  |  |  |
| 31 |  |  |  |  |  |  |  |  |  |  |

