# Merlin UK Growth Opportunity Fact Sheet

## Project Objective

This project identifies UK MSOAs with strong customer opportunity for Merlin Entertainments UK. It combines public demographic data, Merlin attraction locations, customer segment labels, attraction alignment, and simple commercial activation logic.

The dashboard is intended to support executive discussion about where Merlin could prioritise media investment and activation. It is a market opportunity prototype, not a customer-level propensity model.

## Geographic Level

- Geography: MSOA 2021.
- Each row represents one MSOA.
- Key identifiers: `geo_code`, `geo_name`, `latitude`, `longitude`.

MSOA is used because it is granular enough for local opportunity planning while remaining explainable to business stakeholders.

## Data Sources

- Public Census 2021 / ONS demographic data prepared at MSOA level.
- Public Merlin UK attraction location data.
- Derived opportunity scoring and recommendation outputs from `notebooks/3_clustering.ipynb` and `notebooks/4_opportunity_scoring.ipynb`.

The current prototype does not use internal Merlin booking, CRM, ticket sales, media spend, profitability, campaign response, or customer penetration data.

## Customer Segmentation

MSOAs are assigned to customer segments based on demand-side demographic features such as age structure, family households, affluence proxy, deprivation proxy, car access, and population density.

The segmentation is designed to describe customer markets. Merlin attraction distance and attraction supply are not used to create the customer segments.

## Growth Opportunity Index

The dashboard uses `overall_opportunity_score`, also referred to as the Growth Opportunity Index or GOI.

The simplified opportunity score is based on:

- Market size: larger local population indicates a larger addressable audience.
- Segment priority: some customer segments are more commercially attractive for Merlin.
- Recommended attraction alignment: the fit between the MSOA segment and the recommended Merlin attraction.

Opportunity ranking is calculated from the overall opportunity score. Rank 1 is the strongest MSOA opportunity in the output.

## Attraction Recommendation

Each MSOA receives one recommended Merlin attraction. The recommendation is based on attraction alignment with the local customer segment and customer profile. The recommended attraction distance is shown separately so users can assess practical activation feasibility.

## Activation Types

The dashboard uses four activation types:

- Multi-attraction cluster marketing: the MSOA has opportunity and is close enough to multiple Merlin attractions to support a multi-attraction message.
- Annual pass: the MSOA has opportunity and is within a reasonable repeat-visit distance from the recommended attraction.
- Short break: the MSOA has opportunity, stronger family/affluence characteristics, and is far enough from the recommended attraction that an overnight or short-break proposition may be more relevant.
- Other: the MSOA has opportunity but does not clearly meet the simpler annual pass, short break, or cluster marketing rules.

## Revenue Scenario

The dashboard revenue scenario is calculated as:

```text
population * selected market penetration percentage * £33 revenue per visitor
```

The £33 assumption is derived from Merlin annual report figures discussed in the project: approximately £1.999bn revenue divided by 60.5m visitors.

This is an illustrative revenue scenario, not a forecast. It does not adjust for current Merlin penetration, ticket mix, repeat visits, customer overlap, seasonality, marketing cost, conversion rate, or profitability.

## Dashboard Filters

The dashboard filters affect all headline numbers, charts, map points, and chatbot context:

- Merlin attraction
- Customer segment
- Activation type
- Top opportunity areas
- Market penetration percentage

## Important Limitations

- The model uses public demographic data and does not include actual Merlin customer behaviour.
- Revenue is illustrative and should not be presented as incremental revenue.
- The model does not include competitor supply, pricing, media cost, school holidays, tourism flows, or capacity constraints.
- The recommended attraction and activation type are decision-support outputs, not final campaign instructions.
- The analysis is best used to prioritise where to investigate and activate, not as a final investment allocation model.
