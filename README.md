# Traceability APIs

API definitions, JSON-LD vocabulary, and testable mocks for a UN standard supply chain traceability service based on GS1 EPCIS.

Quick link| Description
--|--
Vocabulary| JSON-LD vocabularies (coming march 2022)
API specification| RESTful Open API 3.0 specifications (coming march 2022)
Postman collection | API test client (coming April 2022)
GraphQL playground | test area for trust graph queries
[Project kanban](https://github.com/orgs/uncefact/projects/2/views/4)| epics, tasks, and milestones
[Discussion Board](https://github.com/uncefact/traceability/discussions)|discussions about key topics and decisions


## Business Context

In partnership with the International Trade Centre ([ITC](https://www.intracen.org/)) and with support from the European Union (EU), the United Nations Economic Commision for Europe ([UNECE](https://unece.org/)) is running a [program](https://unece.org/trade/traceability-sustainable-garment-and-footwear) to leverage supply chain traceability to improve sustainability in textile and leather supply chains.

https://unece.org/trade/traceability-sustainable-garment-and-footwear

A component of the program is to demonstrate the feasibility of a decentralised blockchain-based architecture for digitally verifiable traceability. The [blockchain pilot](https://unece.org/sites/default/files/2021-04/ECE_TRADE_C_CEFACT_2021_12E-TextilePolicyBrief.pdf) has achieved significant interest from brands and jurisdictions and has successfully demonstrated the feasibility of leveraging transparency and verified claims to assure sustainability in the cotton and leather supply chain. However, the current platform requires manual entry of all data and so, whilst entirely suitable for early trials, faces two significant scalability challenges:

1. **Data volumes.** Manual data entry works for a few dozens or hundreds of transactions sifficient to prove a traceability chain.  However it will not scale to the billions of transactions across the modern global supply chain. Therefore, this project will define a JSON-LD vocabulary and suite of RESTful APIs to support automation of traceability data exchange.
2. **Supply chain complexity.** The textile & leather supply chain is truly global and very complex - including primary producers, ginning & weaving, garment manufacturing, distribution & retail, and eventual disposal. Even with API automation interfaces, it is unreasonable to imagine that every supply chain participant around the world will push their data to a single central traceability platform. Therefore, this project will define a decentralised linked data architecture based on W3C Verifiable Credentials and Decentralised Identifiers that will allow sustainability claims to be verified even when traceability data is distributed across thousands of different business systems and hundreds of different distributed ledger / traceability platforms.

The first step is to leverage standard GS1 and UN/CEFACT semantics to define standard APIs that the current UNECE traceability platform will support.  The next step is to leverage the same GS1 & UN/CEFACT semantics as the credential interoperability framework between a global network of platforms. 

## API Requirements

The data held by the UNECE platform is essentially a series of key supply chain “events” that, when linked together, can provide the traceability and verification evidence to support sustainability claims.  The API design will be based on some strategic principles.

### API Principles

* **Standards based.**  Aligned with the GS1 [EPCIS](https://www.gs1.org/standards/epcis/1-1) event model and conforming to UN/CEFACT supply chain semantics. This ensures consistency across multiple implementations.
* **Lightweight.**  A suite of modern RESTful APIs that are simple to understand and easy to implement. This ensures that implementation effort and cost is minimised for our industry partners.
* **Decentralisation aligned.** Since event data will come from multiple industry systems and must be correlated across the supply chain, the APIs will avoid locally maintained master data (products, locations, entities, etc) and will instead focus on the use of resolvable public identifiers where master data is maintained in whatever system is the identity authrority (eg a national business register).
* **Secure.**  Applies best practice security architectures (authentication, authorisation, encryption, etc) and collects only the minimum required data. This ensures that data from industry partners is secure, and that commercial sensitive information is not exposed to unauthorised parties.
* **Collaborative.**  We will co-design the APIs together with industry partners to ensure that they are fit for purpose and easily implementable.

### API Resource model

The diagram shows the high-level system architecture.

![architecture diagram](/docs/APIArchitecture.png)

The scope of APIs to be implemented is shown in the green box.

* **Reference data API** allows industry systems to access the common vocabulary of terms such as document type, business step, and sustainability claim type.
* **Business partner API** allows industry systems to create / update basic business partner data so that the platform has the contact information to verify claims (not needed for digitally verifiable claims).
* **Transaction event API** is used to notify / update business-to-business events such as shipments & invoices.
* **Transformation event API** is used to notify / update manufacturing events that transform input materials (eg thread) into output materials (eg fabric).
* **Aggregation event API** is used to notify / update transport events when materials are packed or unpacked (eg many packages grouped into a pallet)
* **Verification event API** is used to notify / update inspection or certification actions on either items or establishments.
* **Traceability graph API** provides a query interface for authorised users to retrieve all the linked events (commercially sensitive information redacted) for a given product that are used to verify sustainability. This API provides industry partners with the evidence to back their product sustainability claims.

### API Security model

API Security will follow standard token based access control using OAuth implicit flow. This model is preferred over simple API keys as it is less susceptible to man-in-the-middle attacks and support finer grained role based acces via claims in the JWT.  For the UNECE platform which is hosted on Google Cloud, this means

* Google [IAM](https://cloud.google.com/iam) for service account management and 
* Google API Gatway [JWT}(https://cloud.google.com/api-gateway/docs/authenticating-users-jwt) authentication method.]

## Vocabulary Requirements

The API structure (ie schema) for EPCIS based traceability events is very simple. Essentially, each event is a small bundle of identifiers that say **who**  (party ID) and **why** (business action ID or certification ID) an event is created and about about **what** (productID or facilityID) and **where** (location ID) and **when** (time-stamp) is is made. The interoperability challenge lies not in the message structure but in the consistent use of identifiers across multiple systems. Without that consistency, there will be no easy way to link events to form the traceability graph that lies at the heart of verifiable sustainability claims.

All identifiers MUST be globally unique and SHOULD be

* **persistent** - they don't change over time
* **verifiable** - claimants can prove ownership of their IDs
* **resolvable** - given an ID, more information can be discovered about the ID.

There are a number of important identifier types.  

* **Sustainability Claims.** will always be represented as URIs.
  * Sustainability claims are typically supported by certificates issued by accredited certifiers and will be made using the vocabulary of a specific reference standard or national regulation. In order to participate in this sustainability project, standards authorities will need to publish their compliance criteria as JSON-LD vocabulary and all compliance claims must reference the specific criteria URI.
  * Claim equivalence. The ITC has analysed of 300 certification / compliance frameworks in order to develop a [standards map](https://www.standardsmap.org/en/identify) that can be used to identify equivalence between compliance claims from different standards. This data can be used to enrich specific sustainability claims with equivalence categories so that verifiers can accept sustainability claims without necessarily knowing the details of a specific standard.
* **Entity Identifiers.** In order to successfully join the dots in a given supply chain, all entity identifiers must be resolvable to one or more verifiable public identities expressed as URIs. Suitable identifier schemes are
  *  DNS domain names - verified using [did:dns](https://danubetech.github.io/did-method-dns/) (for verifiable credentials) or [DKIM](https://datatracker.ietf.org/doc/html/rfc6376) (for email verification) 
  *  National business register entries (eg https://www.abr.business.gov.au/ABN/View?abn=41161080146) verified via a register issued digital credential (automated) or via paper registration certificate inspection (manual). 
* **Product Identifiers.** should be a [GS1 GTIN](https://www.gs1.org/standards/id-keys/gtin) (Global Trade Item Number - presented as a URI (eg urn:epc:id:sgtin:0614141.107346.2017).  Ideally all GTIN should also be registered as a [GS1 digital link](https://www.gs1.org/standards/gs1-digital-link) so that further product information is easily discoverable.  
* **Location Identifiers.** should use [plus codes](https://maps.google.com/pluscodes/) as a URI (eg https://plus.codes/4RPFP4QJ+6G). A plus code identifies a latitude / longitude bounded area of variable resolution (eg could identify a farming region, a specific field, or a street location). The use of plus codes allows easy rendering of traceability graphs as geographic maps, supports location identification of non-address locations such as a field of cotton.  It also appropriately separates geographic locations from entity identifiers so that location information can be provided without correlating to specific supplier identities that may be commercial in confidence.

## Verification Requirements

As the demand (and price) for verifiable sustainable produce increases, so does the opportunity and attractiveness of fraudulent sustainability claims. A number of fraud opportunities exist - here's three;

* **Fake material inputs.** For example, a manufacturer creates a fake invoice from a reputable supplier to claim organic / carbon neutral inputs. Mitigation is to verify that the input was really sourced from the trusted supplier.  
* **Collaboration fraud.** For example, a tanning plant bribes an inspector to issue a "real" chemical safety certificate without actually doing the inspection. Mitigation is to take evidence from tamper evident sensors where possible. Also to confirm that the the inspector is accredited by a trusted authority.
* **Mass-imbalance.**  for example a manufacturer has purchased genuine and verifiable sustainable inputs, but only enough for 10% of production volume. The rest is cheaper non-sustainable inputs. Mitigation is to verify that the quantity of sustainable inputs matches the quantity of finished product output. 

In the ideal world, all traceability claims would be digitally verifiable via cryptographic proofs and verifiable links to trust anchors such as national regulators. However there is still a lot of paper or pdf evidence in the supply chain and so the traceability framework needs to support semi-manual verification whilst driving behavior towards digitally verifiable claims. 

* when a transaction or verification event is supported by a pdf attachment (eg invoice or certificate), the platform will send a verification email with a verification link to the counter-party (supplier or certifier). The recipient email domain must match the registered party DNS domain. This requires the counter-party to be previously registered on the platform.
* when a transaction or verification event is supported by a digital verifiable credential then the platform will simply verify the credential and the issuer identity (signature) and, if appropriate, verify any linked credentials such as certifier accreditation certificates from competent authorities. There is no requirement for any advanced registration.


## Decentralisation Requirements

There are two reasons why all textile supply chain traceability information cannot and should not be aggregated into a single platform.

* **Existing & emerging platforms.** There are already hundreds of supply chain traceability solutions and platforms that service specific sectors or geographies. Some may grow to dominate their niche and others may fail but there will never be a single global "facebook of trade". The UNECE platform (and any non-commercial or government platforms in general) must be designed to complement and not compete with these existing networks. 
* **Security & privacy concerns.** There is a (justifiably) increasing concern about web platforms mining personal or commercial data for profit. Supply chain data will, by it's nature, contain commercially sensitive information such as supplier / customer lists. A well designed traceability platform will minimise it's data holdings so that it presents a less attractive target to cyber attack or accidental unauthorised access. 

The solution to both these concerns is to design a traceability architecture that is decentralised from the outset. Discovering the trust graph that describes a specific product traceability map should be like pulling on and following a piece of string that connects different platforms and private data holdings to discover only the required data for one query - and not like querying a centralised big data lake that holds all the data.

The W3C Verifiable Credentials (VC) and Decentralised Identifiers (DID) standards describe exactly such a a decentralised architecture. The consequence for any traceability platform operator including UNECE is
 
* that any specific platform will need to be able to verify credentials issued from other platforms. Therefore technical and semantic interoperability matter much more than specific technology choices.
* that no single blockchain ledger will hold proofs for the supply chain. So whilst the UNECE platform may choose to anchor it's credentials to Ethereum or some other ledger, it must inevitably be able to verify credentials from other platforms anchored to different ledgers.

## Project Delivery Time-line

The time-line below shows the proposed activities for the next few months for each stakeholder / stream of work. The scope of work until end June 2022 is to co-design the APIs with industry partners and to develop testable mocks that can be used for early implementations.

![API delivery timeline](/docs/APIDeliveryPlan.png)
 
Subsequent work scope (for example to implement the decentralised architecture) will be published when available.

## Project Participation

To ensure that the APIs are fit for purpose we seek early engagement with our industry partners in the co-design and (optionally) pilot implementation work.  Ideally, we will have representation across the partner types including brands, manufacturers, primary producers, and certifying authorities.  There are two levels of engagement

1.	**Co-Design only.**  Partners will be expected to provide one business subject matter expert and one information technology representative for around 4 hours per week each between march and June 2022.  The experts will participate in fortnightly conference calls and will have the opportunity to have their views, ideas, and feedback reflected in the API design and prototyping work.
2.	**Pilot implementation.** Partners will be expected to integrate their business systems (prototype / test environments only) to the platform APIs that are relevant to their role. This will prove the feasibility of the APIs and set benchmarks for the cost and effort of integration. We expect that this would require approximately one full time integration developer for two months (May and June 2022). Pilot implementers will benefit from technical support from the UNECE platform team and will be prioritised for future production implementation.

We understand that industry partner priorities may change and so we expect to manage the engagement process relatively informally. Partners may join late or leave early and may change their engagement level between co-design and implementation at any time. Please respond to Luca Brunello luca.brunello@un.org if you are able to participate in this important phase of the sustainability platform project, indicating your intended level of engagement.
