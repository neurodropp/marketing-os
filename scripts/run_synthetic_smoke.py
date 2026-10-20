"""Reproducible, authored reference examples; not a model benchmark or live execution."""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mos import core as c, processes as p


def write(project, name, text):
    path=project/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')
    return name


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    project=Path(args.out).resolve()
    c.initialize(project,'synthetic-brand','Harbor Notes (synthetic)')
    fixture=json.loads((ROOT/'evals/fixtures/cohort.json').read_text())
    write(project,'inbox/cohort.json',json.dumps(fixture,indent=2))
    write(project,'inbox/brief.md', '''# Synthetic brief
Harbor Notes is a hypothetical subscription service for small teams. Review observed cohort economics, prepare a customer-research plan, draft a paid-social preparation plan and design an activation experiment. No real customers, participants, ad-account access or external-action authorization are supplied. Do not invent missing observations. Working capacity is 120 new accounts per month. All data is synthetic and confined to this workspace.
''')
    completed=[]
    def run(pid,rid,artifact_text,unknown):
        spec=p.show(pid)
        bindings={i['id']:{'status':'unknown' if i['id'] in unknown else 'provided',
                         'references':['inbox/cohort.json','inbox/brief.md'],
                         'note':unknown.get(i['id'],'Synthetic brief and scoped fixture supply this input.')} for i in spec['inputs']}
        result=p.start(project,pid,rid,'Synthetic authored reference case',{'project_id':'synthetic-brand','inputs':bindings})
        output=write(project,f"{spec['output_folder']}/{rid}/result.md",artifact_text)
        completion=result['completion_template']
        completion.update(status='draft' if unknown else 'ready',artifacts=[output],
          review={'reviewer':'Authored reference review','mode':'role-pass','summary':'Inspected against the synthetic source and SOP. No independent reviewer or live action.'},
          limitations=list(unknown.values()),next_action='Resolve stated gaps before live work.' if unknown else 'Use observed economics; do not infer lifetime value or authorize scaling.')
        for q in completion['checks']:
            q.update(verdict='unverified' if unknown else 'pass',evidence=[output],
                     note='Draft-only: missing evidence is identified in the artifact.' if unknown else 'See formulas, cost basis, cohort table and limitation notes in the report.')
        done=p.finish(project,rid,completion)
        assert p.status(project,rid)['status']==completion['status']
        completed.append({'process':pid,'run':rid,'status':done['status'],'artifact':output})
        return output

    f=fixture
    cac=f['allocated_acquisition_cost']/f['initial_customers']
    rows=[]; cumulative=0
    for month,active in enumerate(f['active_customers'],1):
        revenue=active*f['monthly_price']
        cost=active*f['variable_cost_per_active_customer_month']
        contribution=revenue-cost
        cumulative+=contribution
        rows.append((month,active,revenue,cost,contribution,cumulative,cumulative/f['initial_customers']))
    assert cac==140 and cumulative==18900 and rows[1][-1]==133 and rows[2][-1]==189
    downside=sum(n*(100-40) for n in f['active_customers'])/100
    assert downside==162
    table='\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in rows)
    economics=f'''# Observed cohort economics — synthetic

Source: inbox/cohort.json; 100 initially acquired customers, EUR 14,000 fully allocated acquisition cost, three observed months. Revenue excludes VAT and has no refunds in this fixture. Variable service cost is EUR 30 per active customer-month. Fixed overhead is excluded from contribution and must be considered before a business profitability decision.

| Month | Active | Net revenue | Variable cost | Contribution | Cumulative contribution | Per initial customer |
| --- | --- | --- | --- | --- | --- | --- |
{table}

CAC = allocated acquisition cost / initial customers = EUR {cac:.0f}. Contribution = net revenue minus variable cost. Observed three-month contribution per initial customer is EUR 189; observed three-month net revenue per initial customer is EUR 270. Neither is lifetime value.

Cumulative contribution is EUR 133 per acquired customer after month two and EUR 189 after month three. The first observed month-end at which contribution covers CAC is month three. No within-month timing is inferred. Third-month customer retention is 80/100 = 80%; this is not annual retention or revenue retention.

Downside sensitivity: holding observed activity fixed, variable cost EUR 40 produces EUR {downside:.0f} of three-month contribution per acquired customer. At CAC EUR 180, payback is not reached in the observed period. Changing retention would require a separate scenario; no mature lifetime estimate is available.

Proposed decision: treat three-month contribution coverage as an observed diagnostic, not a universal scale threshold. Do not scale beyond capacity of 120 new accounts per month without a capacity and marginal acquisition-cost review. The fixture does not establish future CAC, customer lifetime, fixed-cost profitability or authorization to spend.

Quality review: revenue and contribution are separated; zero/missing denominators must return unavailable; this fixture has a nonzero known denominator. Cohort maturity is three months and all extrapolation is excluded. Every numerical value is reproducible from the source using the script that generated this report.
'''
    output=run('F1.03','economics',economics,{})
    csvpath=project/'strategy/economics/cohort.csv'
    with csvpath.open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['month','active','net_revenue','variable_cost','contribution','cumulative_contribution','contribution_per_initial_customer']);writer.writerows(rows)
    # Additional reproducible table is supplemental; accepted report already contains all figures.
    run('F2.04','research', '''# Customer research plan — draft, synthetic

Decision: why do small teams stop using Harbor Notes before month three? Cohort activity suggests attrition but does not identify a cause. No interviews, support logs or survey responses were supplied.

Recruitment proposal: invite a pilot of six accounts, balanced between retained and lapsed accounts, including users and purchase decision makers where different. This is purposive qualitative sampling, not a population estimate. Recruitment requires actual access and authorization; no invitations have been sent.

Interview guide: describe the last time your team needed to organize notes; what did you do before Harbor Notes; what triggered trying it; walk through first use; where did the expected outcome fail; what alternative did you choose; what would have made continued use worthwhile? Ask for concrete episodes without suggesting price or onboarding as the answer.

Observation: ask a willing participant to attempt a representative first task. Record task, friction and outcome with consent and minimal personal data. Pilot the guide before extending the sample.

Survey: defer until interviews clarify plausible barriers. Then pilot neutral questions about actual behavior, allow other/not applicable answers and record nonresponse. Do not turn six interview themes into percentages of all customers.

Evidence matrix columns: source ID, participant context, exact observation/quote, code, interpretation, contradictory evidence, limitation and decision implication. Quantitative comparison uses the supplied cohort only; selection bias and missing support evidence remain explicit.

Output status: research instrument and sampling plan prepared. No findings, quotes, participants or causal conclusions have been invented. Obtain participant access and actual evidence before reporting research results.
''',{'i2':'No participant access or transcripts supplied.','i3':'Cohort totals are available, but individual research/support data is absent.'})
    run('O3.03','paid-social', '''# Paid social preparation — draft, synthetic

Objective: assess qualified acquisition only after the activation event and economics threshold are approved. Do not optimize to clicks as a substitute for customer value. This is a setup specification, not a live campaign.

Proposed structure: one controlled prospecting test for the agreed segment; keep retargeting separate and inactive until audience eligibility, scale and permissions are verified. Exclude existing customers where lawful, supported and appropriate. Record potential audience overlap and missing identity coverage.

Creative brief: test a practical team-workflow angle against a clarity-of-information angle. No fabricated testimonial or claimed percentage productivity gain. Assets still need production, rights review and current placement checks.

Readiness path: ad preview -> destination -> signup -> activation event -> analytics -> customer record. Check event deduplication, destination errors and consent behavior. Save test evidence before launch. Record exact campaign/ad IDs only after an authorized tool observes them.

Budget and pacing: EUR 14,000 is historical acquisition cost in the fixture, not a new spend mandate. Ask for an actual test budget and authority only when a concrete launch is ready. No account tool is available, so no campaign has been created, paused or edited.

Monitoring plan: inspect spend against the approved test envelope, conversion lag, qualified progression, marginal acquisition cost and customer support capacity. Examine frequency alongside declining marginal results before inferring fatigue. Proposed pause triggers include broken destination or unreliable critical events, within granted authority.

Blockers: live account access, spend authorization, produced assets, approved audience definitions and end-to-end tracking evidence. Deliver a plan now; do not report live delivery or measured campaign results.
''',{'i2':'No new spending authority or live account access.','i3':'Creative assets are unavailable.','i4':'Tracking QA evidence is unavailable.'})
    run('G2.02','experiment', '''# Activation experiment protocol — draft, synthetic

Hypothesis: a task-oriented onboarding checklist increases the proportion of newly created team workspaces that complete the agreed first-value task within seven days. The activation event must be agreed and validated before exposure. Decision: whether to adopt the checklist for eligible new workspaces.

Randomization unit: workspace, with all members assigned consistently to reduce cross-variant contamination. Population: genuinely new eligible workspaces, excluding internal/test accounts using a predeclared rule. Analyze at workspace level on an intention-to-treat basis; document non-exposure and crossovers.

Primary outcome: activated eligible workspaces / assigned eligible workspaces within seven days. Guardrails: task errors, support contacts per workspace and cancellation/refund outcomes over a prespecified follow-up. Definitions and collection methods must be validated.

Design: fixed-horizon randomized comparison with unchanged offer and pricing. Before launch, estimate baseline activation, choose a minimum practically useful effect, significance level and power, then calculate required sample for the workspace-level design. Do not invent sample size or duration: traffic and baseline activation are missing. Budget enough time for the seven-day outcome to mature and the relevant business cycle.

Analysis: check assignment integrity and sample-ratio mismatch; inspect missing outcomes and exposure contamination; estimate absolute effect with an appropriate interval. The primary comparison is prespecified. Additional segment analyses are exploratory and require multiplicity-aware interpretation. No unplanned early winner declaration.

Decision rules: ship only if the agreed practical/uncertainty criteria and guardrails pass; stop for a material operational failure within authority; otherwise iterate or call the result inconclusive. A failed validity check prevents a causal claim. The exact thresholds and analysis choices must be fixed before launch.

Status: test design draft. Missing baseline, eligible traffic and agreed activation event prevent sizing and execution. No experiment has run and no lift is claimed.
''',{'i2':'Baseline activation and eligible traffic are missing.'})
    report={'type':'authored-reference-smoke','synthetic':True,'independent_model_evaluation':False,
            'checks':['CAC 140','three-month contribution 189 per initial customer','payback observed at month 3','downside contribution 162 below CAC 180','missing research/account/experiment data stays draft'],
            'runs':completed,'external_actions':[]}
    write(project,'smoke-report.json',json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
