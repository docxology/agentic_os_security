# Local verification

The replay imports the checked-in defensive registry and checks that each category has unique, nonempty entries. Every domain must include contents and restrictions. Every control must include both a rule and a rationale. Native tests also check the pinned domain and control identifiers, minimum description coverage, wording of configuration invariants, and identifier syntax. The replay writes category counts to JSON and draws an inventory from the same values.

![Counts of distinct entries in the defensive design registry.](../../output/figures/defensive_registry_inventory.png){#fig:defensive-registry}

The bar chart reports inventory size. Each category uses a different unit of design description, so the counts do not rank categories or operating systems. The check uses no deployed systems, external data, or security events.
