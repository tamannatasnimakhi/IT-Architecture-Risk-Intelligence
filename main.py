import pandas as pd
import numpy as np

df = pd.read_csv("incident_event_log.csv")
print(df.head())

print("Dataset shape:", df.shape)
print("Unique incidents:", df["number"].nunique())

print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nHidden missing values (? marks):")
print((df == "?").sum())

df = df.replace("?", np.nan)

print("\nMissing values after cleaning:")
print(df.isnull().sum())

incidents = df.drop_duplicates(subset="number", keep="last")

print("\nIncident-level dataset shape:")
print(incidents.shape)
incidents["opened_at"] = pd.to_datetime(
    incidents["opened_at"],
    format="%d/%m/%Y %H:%M"
)

incidents["resolved_at"] = pd.to_datetime(
    incidents["resolved_at"],
    format="%d/%m/%Y %H:%M",
    errors="coerce"
)

incidents["resolution_hours"] = (
    incidents["resolved_at"] - incidents["opened_at"]
).dt.total_seconds() / 3600

print("\nResolution time:")
print(incidents["resolution_hours"].describe())

print("\nSLA performance:")
print(incidents["made_sla"].value_counts())

print("\nReassignment count:")
print(incidents["reassignment_count"].describe())

high_reassignment = incidents[incidents["reassignment_count"] > 3]

print("\nIncidents with more than 3 reassignments:")
print(len(high_reassignment))

print("\nReopen count:")
print(incidents["reopen_count"].value_counts().sort_index())

print("\nTop incident categories:")
print(incidents["category"].value_counts().head(10))

sla_by_category = incidents.groupby("category")["made_sla"].apply(
    lambda x: (x == False).mean() * 100
)

print("\nTop categories by SLA failure rate:")
print(sla_by_category.sort_values(ascending=False).head(10))

category_risk = incidents.groupby("category").agg(
    incident_count=("number", "count"),
    sla_failure_rate=("made_sla", lambda x: (x == False).mean() * 100)
)

print("\nCategory risk:")
print(
    category_risk
    .sort_values("incident_count", ascending=False)
    .head(10)
)

incidents["high_reassignment"] = incidents["reassignment_count"] > 3

print("\nSLA failure by reassignment group:")
print(
    incidents.groupby("high_reassignment")["made_sla"]
    .apply(lambda x: (x == False).mean() * 100)
)

print("\nResolution time by reassignment group:")
print(
    incidents.groupby("high_reassignment")["resolution_hours"].median()
)

print("\nTop assignment groups:")
print(incidents["assignment_group"].value_counts().head(10))

sla_by_category = incidents.groupby("category")["made_sla"].apply(
    lambda x: (x == False).mean() * 100
)

print("\nTop categories by SLA failure rate:")
print(sla_by_category.sort_values(ascending=False).head(10))

group_risk = incidents.groupby("assignment_group").agg(
    incident_count=("number", "count"),
    sla_failure_rate=("made_sla", lambda x: (x == False).mean() * 100)
)

print("\nAssignment group risk:")
print(
    group_risk
    .sort_values("incident_count", ascending=False)
    .head(10)
)

risky_groups = group_risk[
    (group_risk["incident_count"] >= 300) &
    (group_risk["sla_failure_rate"] >= 40)
].sort_values("sla_failure_rate", ascending=False)

print("\nHigh-risk assignment groups:")
print(risky_groups)

print("\nPriority distribution:")
print(incidents["priority"].value_counts())

print("\nSLA failure by priority:")
print(
    incidents.groupby("priority")["made_sla"]
    .apply(lambda x: (x == False).mean() * 100)
    .sort_values(ascending=False)
)

print("\nMedian resolution time by priority:")
print(
    incidents.groupby("priority")["resolution_hours"]
    .median()
    .sort_values(ascending=False)
)

print("\nMedian reassignments by priority:")
print(
    incidents.groupby("priority")["reassignment_count"]
    .median()
    .sort_values(ascending=False)
)

print("\nHigh reassignment rate by priority:")
print(
    incidents.groupby("priority")["high_reassignment"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("\nKnowledge usage:")
print(incidents["knowledge"].value_counts())

print("\nSLA failure by knowledge usage:")
print(
    incidents.groupby("knowledge")["made_sla"]
    .apply(lambda x: (x == False).mean() * 100)
)

print("\nKnowledge usage by priority:")
print(
    incidents.groupby("priority")["knowledge"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("\nMedian resolution time by knowledge usage:")
print(
    incidents.groupby("knowledge")["resolution_hours"]
    .median()
)

print("\nSystem modification count:")
print(incidents["sys_mod_count"].describe())

incidents["high_modification"] = incidents["sys_mod_count"] > 10

print("\nSLA failure by modification activity:")
print(
    incidents.groupby("high_modification")["made_sla"]
    .apply(lambda x: (x == False).mean() * 100)
)

print("\nResolution time by modification activity:")
print(
    incidents.groupby("high_modification")["resolution_hours"]
    .median()
)

incidents["risk_score"] = 0

incidents.loc[
    incidents["reassignment_count"] > 3,
    "risk_score"
] += 1

print("\nRisk score after reassignment rule:")
print(incidents["risk_score"].value_counts())

incidents.loc[
    incidents["sys_mod_count"] > 10,
    "risk_score"
] += 1

print("\nRisk score after modification rule:")
print(incidents["risk_score"].value_counts().sort_index())

print("\nSLA failure by risk score:")
print(
    incidents.groupby("risk_score")["made_sla"]
    .apply(lambda x: (x == False).mean() * 100)
)

incidents.to_csv(
    "incident_risk_analysis.csv",
    index=False
)

print("\nSaved: incident_risk_analysis.csv")
