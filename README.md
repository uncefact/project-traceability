# Traceability APIs

API definitions and testable mocks for a UN standard supply chain traceability service based on GS1 EPCIS.

## Business Context

In partnership with the International Trade Centre ([ITC](https://www.intracen.org/)) and with support from the European Union (EU), the United Nations Economic Commision for Europe ([UNECE](https://unece.org/)) is running a [program](https://unece.org/trade/traceability-sustainable-garment-and-footwear) to leverage supply chain traceability to improve sustainability in textile and leather supply chains.

https://unece.org/trade/traceability-sustainable-garment-and-footwear

A component of the program is to demonstrate the feasibility of a decentralised blockchain-based architecture for digitally verifiable traceability. The [blockchain pilot](https://unece.org/sites/default/files/2021-04/ECE_TRADE_C_CEFACT_2021_12E-TextilePolicyBrief.pdf) has achieved significant interest from brands and jurisdictions and has successfully demonstrated the feasibility of leveraging transparency and verified claims to assure sustainability in the cotton and leather supply chain. However, the current platform requires manual entry of all data and so, whilst entirely suitable for early trials, faces two signifiant scalability challenges:

1. **Data volumes.** Manual data entry works for a few dozens or hundreds of transactions sifficient to prove a traceability chain.  However it will not scale to the billions of transactions across the modern global supply chain. Therefore, this project will define a JSON-LD vocabulary and suite of RESTful APIs to support automation of traceability data exchange.
2. **Supply chain complexity.** The textile & leather supply chain is truly global and very complex - including primary producers, ginning & weaving, garment manufacuring, distributoin & retail, and eventual disposal. Even with API automation interfaces, it is unreasonable to imagine that every supply chain participant around the world will push their data to a single central traceability platform. Therefore, this project will define a de-centralised linked data architecture based on W3C Verifiable Credentials and Decentralised Identifiers that will allow sustainability claims to be verified even when traceability data is distributed across thousands of different business systems and hundreds of different distributed ledger / traceability platforms.

The first step is to leverage standard GS1 and UN/CEFACT semantics to define standard APIs that the current UNECE traceability platform will support.  The next step is to leverage the same GS1 & UN/CEFACT semantics as the credential interoperability framework between a global network of platforms. 

## API Strategy

The data held by the UNECE platform is essentially a series of key supply chain “events” that, when linked together, can provide the traceability and verification evidence to support sustainability claims.  The API design will be based on some strategic principles.

* **Standards based.**  Aligned with the GS1 [EPCIS](https://www.gs1.org/standards/epcis/1-1) event model and conforming to UN/CEFACT supply chain semantics. This ensures consistency across multiple implementations.
* **Lightweight.**  A suite of modern RESTful APIs that are simple to understand and easy to implement. This ensures that implementation effort and cost is minimised for our industry partners.
* **Secure.**  Applies best practice security architectures (authentication, authorisation, encryption, etc) and collects only the minimum required data. This ensures that data from industry partners is secure, and that commercial sensitive information is not exposed to unauthorised parties.
* **Collaborative.**  We will co-design the APIs together with industry partners to ensure that they are fit for purpose and easily implementable.

The diagram shows the high-level system architecture.



The scope of APIs to be implemented is shown in the green box.

* **Reference data API** allows industry systems to access the common vocabulary of terms such as document type, business step, and sustainability claim type.
* **Business partner API** allows industry systems to create / update basic business partner data so that the platform has the contact information to verify claims.
* **Transaction event API** is used to notify/update business-to-business events such as shipments & invoices.
* **Transformation event API** is used to notify/update manufacturing events that transform input materials (eg thread) into output materials (eg fabric).
* **Aggregation event API** is used to notify/update transport events when materials are packed or unpacked (eg many packages grouped into a pallet)
* **Verification event API** is used to notify/update inspection or certification actions on either items or establishments.
* **Traceability graph API** provides a query interface for authorised users to retrieve all the linked events (commercially sensitive information redacted) for a given product that are used to verify sustainability. This API provides industry partners with the evidence to back their product sustainability claims.

## Vocabulary Strategy

The API structure (ie schema) for EPCIS based traceability events is very simple. essentially, each event is a small bundle of identifiers that say **who**  (party ID) and **why** (business action ID or certification ID) an event is created and about about **what** (productID or facilityID) and **where** (location ID) and **when** (timestamp) is is made. The interoperability challenge lies not in the message structure but in the consistent use of identifiers across multiple systems. without that consistency, there will be no easy way to link events to form a traceability graph that lies at the heart of verifiable sustainability claims.

All identifiers MUST be globally uniuque and SHOULD be

* **persistent** - they dont change over time
* **verifiable** - claimants can prove ownership of their IDs
* **resolvable** - given an ID, more information can be discovered about the ID.

There are a number of important identifer types.  

* **Sustainability Claims.** will always be represented as URIs.
  * Sustainability claims are typcially supported by certificates issued by accredited certifiers and will be made using the vocabulary of a specific referecne standard or national regulation. In order to participate in this sustainability project, standards authorities will need to publish their compliance criteria as JSON-LD vocabulary and all compliance claims must reference the specific critieria URI.
  * Claim equivalence. The ITC has analysed of 300 certification / compliance frameworks in order to develop a [standards map](https://www.standardsmap.org/en/identify) that can be used to identify equivalence between compliance claims from different standards. This data can be used to enrich specific sustainability claims with equivalence categories so that verifiers can accept sustainability claims without necessarily knowing the details of a specific standard.
* **Entity Identifiers.** In order to successfully join the dots in a given supply chain, all entitiy idenfiers must be resolvable to one or more verifiable public identities expressed as URIs. Suitable identifier schemes are
  *  DNS domain names - verified using [did:dns](https://danubetech.github.io/did-method-dns/) (for verifiable credentials) or [DKIM](https://datatracker.ietf.org/doc/html/rfc6376) (for email verificaiton) 
  *  National business register entries (eg https://www.abr.business.gov.au/ABN/View?abn=41161080146) verified via a register issued digital credential (automated) or via paper registration certificate inspection (manual). 
* **Product Identifiers.** should be a [GS1 GTIN](https://www.gs1.org/standards/id-keys/gtin) (Global Trade Item Number - presented as a URI (eg urn:epc:id:sgtin:0614141.107346.2017).  Ideally all GTIN should also be registered as a [GS1 digital link](https://www.gs1.org/standards/gs1-digital-link) so that further product information is easily discoverable.  
* **Location Identifiers.** should use [plus codes](https://maps.google.com/pluscodes/) as a URI (eg https://plus.codes/4RPFP4QJ+6G). A plus code identifies a lattitude / longditude bounded area of variable resolution (eg could identify a farming region, a specific field, or a street location). The use of plus codes allows easy rednering of traceability graphs as geographic maps, supports location idenfiication for non-address locations such as a field of cotton, and apprpriately separates geographic locations from entitiy identifers so that, if desired, location information can be provided without correlating to specific supplier identities that may be commercial in confidence.

## Verification Strategy

TBC

## Project Delivery Timeline

The timeline below shows the proposed activities for the next few months for each stakeholder / stream of work. The scope of work until end June 2022 is to co-design the APIs with industry partners and to develop testable mocks that can be used for early implementations.


 
Subsequent work scope (for example to implement the decentralised architecture) will be published when available.

## Project Participation

To ensure that the APIs are fit for purpose we seek early engagement with our industry partners in the co-design and (optionally) pilot implementation work.  Ideally, we will have representation across the partner types including brands, manufacturers, primary producers, and certifying authorities.  There are two levels of engagement

1.	**Co-Design only.**  Partners will be expected to provide one business subject matter expert and one information technology representative for around 4 hours per week each between march and June 2022.  The experts will participate in fortnightly conference calls and will have the opportunity to have their views, ideas, and feedback reflected in the API design and prototyping work.
2.	**Pilot implementation.** Partners will be expected to integrate their business systems (prototype / test environments only) to the platform APIs that are relevant to their role. This will prove the feasibility of the APIs and set benchmarks for the cost and effort of integration. We expect that this would require approximately one full time integration developer for two months (May and June 2022). Pilot implementers will benefit from technical support from the UNECE platform team and will be prioritised for future production implementation.

We understand that industry partner priorities may change and so we expect to manage the engagement process relatively informally. Partners may join late or leave early and may change their engagement level between co-design and implementation at any time. Please respond to Luca Brunello luca.brunello@un.org if you are able to participate in this important phase of the sustainability platform project, indicating your intended level of engagement.
