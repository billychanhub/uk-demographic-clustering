# Merlin UK Growth Opportunity Fact Sheet

## Project Objective

This project identifies UK MSOAs with strong customer opportunity for Merlin Entertainments UK. It combines public demographic data, Merlin attraction locations, customer segment labels, attraction alignment, and simple commercial activation logic.

The dashboard is intended to support executive discussion about where Merlin could prioritise media investment and activation. It is a market opportunity prototype, not a customer-level propensity model and not a final media allocation model.

## Dashboard Data Sources

The dashboard is powered mainly by:

- `data/output/msoa_layer_2_opportunity_scores.csv`: rich analytical dataset used for dashboard filters, headline metrics, charts, map, and chatbot summaries.
- `data/processed/merlin_attraction_data.csv`: Merlin attraction names, categories, brands, and locations used for mapping and distance calculations.
- `data/output/merlin_key_recommendation_output.csv`: concise brief-facing export containing the required recommendation output columns.

The chatbot receives this fact sheet plus compact summaries generated from `msoa_layer_2_opportunity_scores.csv`. It does not send every MSOA row to OpenAI.

## Geographic Level

- Geography: MSOA 2021.
- Each row represents one MSOA.
- Total rows in the opportunity dataset: 7,264 MSOAs.
- Key identifiers: `geo_code`, `geo_name`, `country`, `latitude`, `longitude`.

MSOA stands for Middle Layer Super Output Area. It is a small UK statistical geography, typically containing around 5,000 to 15,000 residents. MSOA is used because it is granular enough for local opportunity planning while remaining explainable to business stakeholders.

## Input Data Used

- Public Census 2021 / ONS demographic data prepared at MSOA level.
- Public Merlin UK attraction location data.
- Derived customer segmentation from `notebooks/3_clustering.ipynb`.
- Derived opportunity scoring and activation logic from `notebooks/4_opportunity_scoring.ipynb`.

The current prototype does not use internal Merlin booking data, CRM data, ticket sales, visit frequency, customer-level spend, media spend, profitability, campaign response, competitor supply, or current market penetration.

## Key Dataset Fields

Important fields in the dashboard dataset include:

- `overall_opportunity_score`: Growth Opportunity Index, also called GOI.
- `opportunity_rank`: rank of each MSOA by GOI. Rank 1 is the strongest MSOA opportunity.
- `opportunity_percentile`: percentile position of each MSOA by GOI.
- `market_size_score`: contribution from addressable local population.
- `segment_priority_score`: contribution from the commercial priority of the assigned customer segment.
- `recommended_attraction_alignment_score`: fit between the MSOA and its recommended Merlin attraction.
- `segment_category_fit_score`: fit between the MSOA segment and the recommended attraction category.
- `recommended_attraction_name`: recommended Merlin attraction for the MSOA.
- `recommended_attraction_distance_miles`: distance from the MSOA to the recommended attraction.
- `nearest_merlin_attraction` and `nearest_merlin_distance_miles`: closest Merlin attraction, which may differ from the recommended attraction.
- `recommended_activation_type`: simplified activation route for the MSOA.
- `activation_type_rationale`: text explanation for why that activation type was assigned.
- `key_contributing_driver`: the main reason the MSOA scores strongly.
- `total_population`: local market size used in population and revenue scenario calculations.

## Customer Segmentation

MSOAs are assigned to customer segments based on demand-side demographic features such as age structure, family households, affluence proxy, deprivation proxy, car access, and population density.

The segmentation is designed to describe customer markets. Merlin attraction distance and attraction supply are not used to create the customer segments.

The five customer segments are:

- Mainstream Affluent Suburban Markets: large, commercially attractive suburban markets with relatively high car access and stronger affluence indicators. This is one of the strongest Merlin opportunity segments because it combines scale, access, and spending potential.
- Balanced Regional Family Markets: family-heavy regional markets with higher children and family household shares. These are highly relevant for family-led propositions, annual pass messaging, and attractions with broad family appeal.
- Dense Urban Professional Markets: dense urban markets with stronger professional or AB/C1 characteristics but lower car access. These are relevant for city-centre attractions, short travel journeys, and premium urban experiences.
- Student & Young Adult Urban Markets: younger urban markets with high young-adult presence. These can be relevant for social, city-based, or experience-led attractions, but the segment is less family-led.
- Older Rural & Low-Density Markets: lower-density markets with older age profiles and high car access. These are less naturally aligned to the core family-growth opportunity unless there is a strong nearby attraction or a specific product reason.

Indicative segment profile from the current dataset:

- Mainstream Affluent Suburban Markets: 2,950 MSOAs, 23.9m population, mean GOI 74.8.
- Balanced Regional Family Markets: 1,693 MSOAs, 14.7m population, mean GOI 73.5.
- Dense Urban Professional Markets: 599 MSOAs, 5.2m population, mean GOI 69.1.
- Student & Young Adult Urban Markets: 139 MSOAs, 1.4m population, mean GOI 58.1.
- Older Rural & Low-Density Markets: 1,883 MSOAs, 14.5m population, mean GOI 51.7.

## Growth Opportunity Index

The dashboard uses `overall_opportunity_score`, also referred to as the Growth Opportunity Index or GOI.

The simplified opportunity score is based on:

- Market size: larger local population indicates a larger addressable audience.
- Segment priority: some customer segments are more commercially attractive for Merlin.
- Recommended attraction alignment: the fit between the MSOA segment/profile and the recommended Merlin attraction.

The GOI is useful for comparing MSOAs and prioritising where to investigate, target, or activate first. It should not be interpreted as predicted sales, actual current penetration, or guaranteed incremental revenue.

## Opportunity Ranking

`opportunity_rank` is calculated from `overall_opportunity_score`. Rank 1 is the strongest MSOA opportunity in the output. The dashboard's "Top opportunity MSOAs" filter includes MSOAs from rank 1 up to the selected rank.

When the dashboard refers to "Top Opportunity Area", it groups the currently filtered MSOAs by broader area name, calculates the mean GOI for each area, and selects the area with the highest mean GOI. Population and MSOA count are used as tie-breakers.

## Attraction Recommendation

Each MSOA receives one recommended Merlin attraction. The recommendation is based on attraction alignment with the local customer segment and profile. The recommended attraction is not necessarily the nearest attraction.

Distance is shown separately:

- `recommended_attraction_distance_miles`: distance to the recommended attraction.
- `nearest_merlin_distance_miles`: distance to the nearest Merlin attraction.

This distinction matters because the best proposition for a customer segment may not always be the closest attraction.

## Activation Types

Each MSOA receives one activation type based on simple fit and distance rules. The activation type explains how Merlin could activate the area if it is included in the planning view. Activation types are assigned to all MSOAs, regardless of their opportunity rank. The dashboard rank filter controls which MSOAs are shown or prioritised.

The dashboard uses four activation types:

- Multi-attraction cluster marketing: the MSOA is close enough to multiple Merlin attractions to support a multi-attraction message.
- Annual pass: the MSOA is within a reasonable repeat-visit distance from the recommended attraction.
- Short break: the MSOA has stronger family/affluence characteristics and is far enough from the recommended attraction that an overnight or short-break proposition may be more relevant.
- Other: the MSOA does not clearly meet the simpler annual pass, short break, or cluster marketing rules.

Indicative activation profile from the current dataset:

- Other: 3,306 MSOAs, 26.7m population, mean GOI 64.1.
- Multi-attraction cluster marketing: 2,760 MSOAs, 23.1m population, mean GOI 71.7.
- Annual pass: 986 MSOAs, 8.0m population, mean GOI 68.4.
- Short break: 212 MSOAs, 1.9m population, mean GOI 69.9.

## Recommended Activation

The recommended activation type is a planning suggestion, not a campaign instruction. It should be interpreted as:

- Annual pass: repeat-visit proposition for audiences near enough to return.
- Multi-attraction cluster marketing: cross-attraction or multi-site message for audiences near multiple Merlin attractions.
- Short break: family and affluence-led overnight or resort-style proposition.
- Other: lower-confidence activation route; may still be worth testing if the MSOA has a high GOI or a strong specific attraction fit.

## Key Contributing Driver

`key_contributing_driver` identifies the main reason an MSOA scores well. It is simplified to one driver for explainability.

The three driver labels are:

- large local market: the MSOA is primarily attractive because it has a large addressable population.
- priority customer segment: the MSOA belongs to a segment that has been prioritised for Merlin opportunity.
- strong Merlin proposition alignment: the MSOA has a strong fit with the recommended attraction proposition.

Current dataset driver profile:

- large local market: 2,337 MSOAs, 24.0m population.
- strong Merlin proposition alignment: 2,552 MSOAs, 18.2m population.
- priority customer segment: 2,375 MSOAs, 17.4m population.

## Revenue Scenario

The dashboard revenue scenario is calculated as:

```text
population * selected market penetration percentage * £33 revenue per visitor
```

The £33 assumption is derived from Merlin annual report figures discussed in the project: approximately £1.999bn revenue divided by 60.5m visitors.

This is an illustrative revenue scenario, not a forecast. It does not adjust for current Merlin penetration, ticket mix, repeat visits, customer overlap, seasonality, marketing cost, conversion rate, capacity, cannibalisation, or profitability.

Do not describe the revenue scenario as "headroom", "incremental revenue", or "forecast revenue". Better wording is "illustrative revenue scenario", "addressable revenue scenario", or "revenue-at-stated-penetration scenario".

## Dashboard Filters

The dashboard filters affect all headline numbers, charts, map points, and the current-view context supplied to the chatbot. The chatbot also receives a compact full-dataset context so it can answer broader stakeholder questions.

Dashboard filters:

- Merlin attraction
- Customer segment
- Activation type
- Area name
- Top opportunity MSOAs
- Market penetration percentage

If a stakeholder asks about "the current view", "selected filters", or "what I am seeing now", use the current dashboard filter context. If they ask a broader question, such as "explain each segment" or "where should Merlin target LEGOLAND", use the full-dataset context.

## Map Interpretation

The map shows MSOA opportunity points and Merlin attractions. MSOA colour represents recommended activation type. Merlin attractions are shown as attraction markers. The selected leaderboard area can be highlighted on the map.

Map hover information is intended to help stakeholders inspect a local opportunity, including geography, segment, score/rank, population, recommended attraction, distance, activation type, and key contributing driver.

## Common Stakeholder Questions The Chatbot Can Answer

The chatbot should be able to answer questions such as:

- Explain each customer segment.
- Which areas are highest opportunity overall?
- Which areas are highest opportunity for a selected attraction such as LEGOLAND?
- Where should Merlin target family annual passes?
- Which attractions have the largest recommended audience?
- Which activation type should be prioritised in the current dashboard view?
- What are the main caveats or limitations?

The chatbot should answer using only the supplied fact sheet and generated dataset summaries. If the data does not support an answer, it should say it does not have enough information.

## Important Limitations

- The model uses public demographic data and does not include actual Merlin customer behaviour.
- Revenue is illustrative and should not be presented as incremental revenue.
- The model does not include competitor supply, pricing, media cost, school holidays, tourism flows, customer penetration, repeat visitation, capacity constraints, or profit margin.
- The recommended attraction and activation type are decision-support outputs, not final campaign instructions.
- The analysis is best used to prioritise where to investigate and activate, not as a final investment allocation model.
- The model is at MSOA level, not customer level. It can identify promising local markets but cannot identify individual customers.
- Strong opportunity does not guarantee conversion; it indicates demographic fit, market size, and attraction alignment under the stated model assumptions.

## Suggested Next Steps

To strengthen this prototype with internal or additional external data:

- Propensity modelling: use Merlin customer and visitation data to estimate attraction-level propensity by MSOA or customer profile.
- Penetration analysis: compare current Merlin visitors against local population to identify under-penetrated high-opportunity markets.
- Attraction alignment modelling: replace rule-based attraction alignment with observed customer visitation patterns by attraction, segment, distance, and product type.
- Tourism and travel context: add domestic/inbound tourism flows, journey time, accommodation supply, and seasonality to strengthen short-break and destination-led recommendations.
