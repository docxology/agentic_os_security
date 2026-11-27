# Defensive design

The published review separates trust domains from design controls and configuration invariants [@friedman2026agentic]. A domain records the material it is intended to contain and the restrictions that apply to it. A control pairs a rule with a rationale so a reviewer can evaluate the intent of the rule. A configuration invariant records a capability that remains prohibited for the agent. These distinctions help a reviewer trace where decisions about authority are recorded. Least privilege motivates limiting every component to the authority it needs to do its job [@saltzer1975protection].

The wording in these records describes design intent. Enforcement depends on an implementation and its configuration. The static registry gives reviewers specific claims to inspect before reviewing a deployment.
