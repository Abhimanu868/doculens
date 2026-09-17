#!/usr/bin/env python3
"""Generate a synthetic domain-specific NLI dataset for company policies / contracts.

Produces ~2 000 sentence pairs labelled entailment / neutral / contradiction,
balanced roughly evenly across the three classes.

Topics covered: remote work, payment terms, termination, leave policy,
confidentiality, salary, deadlines.

Output: data/raw/domain_pairs.csv  (columns: sentence_a, sentence_b, label)
"""

import csv
import random
from pathlib import Path

random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "domain_pairs.csv"

# ---------------------------------------------------------------------------
# Base data — each tuple: (premise, entailment_hyp, contradiction_hyp, neutral_hyp)
# ---------------------------------------------------------------------------

REMOTE_WORK = [
    (
        "Employees may work from home up to three days per week.",
        "Staff members are allowed to work remotely for part of the work week.",
        "All employees must be physically present at the office every working day.",
        "The company cafeteria offers a new vegetarian menu on Wednesdays.",
    ),
    (
        "Remote workers must be available during core hours from 10 AM to 4 PM.",
        "Employees working from home are expected to be reachable during midday hours.",
        "Remote employees can choose their own working hours without any restrictions.",
        "The IT department will perform server maintenance this weekend.",
    ),
    (
        "Manager approval is required before an employee can begin working remotely.",
        "An employee needs their supervisor's permission to start a remote work arrangement.",
        "Employees can start working remotely at any time without notifying their manager.",
        "The company provides health insurance coverage starting from the first day.",
    ),
    (
        "The company provides a monthly stipend of $200 for home office equipment.",
        "Remote workers receive financial support to set up their workspace at home.",
        "Employees must purchase all home office equipment entirely at their own expense.",
        "Annual performance reviews are conducted in December each year.",
    ),
    (
        "All remote employees must connect through the company VPN when accessing internal systems.",
        "Using a secure VPN connection is mandatory for remote access to company resources.",
        "Remote employees can access company systems freely without any security measures.",
        "The marketing team launched a new brand campaign last quarter.",
    ),
    (
        "Remote work eligibility begins after completing six months of employment.",
        "New employees must work on-site for at least half a year before they can work from home.",
        "Employees are eligible for remote work from their very first day at the company.",
        "The office building has reserved parking spots in the basement garage.",
    ),
    (
        "Hybrid meetings require at least one participant to join from the office conference room.",
        "When holding a hybrid meeting, someone must be present in the physical meeting room.",
        "All hybrid meetings are conducted entirely through video calls with no in-office presence.",
        "The company recently switched its email provider to a cloud-based service.",
    ),
    (
        "Remote employees must maintain a minimum internet speed of 50 Mbps.",
        "A reliable high-speed internet connection is required for working from home.",
        "There are no internet speed requirements for employees who work remotely.",
        "The company holiday party will be held at the downtown convention center.",
    ),
    (
        "Remote work arrangements are reviewed quarterly based on employee performance metrics.",
        "The privilege of working from home is evaluated every three months using performance data.",
        "Once granted, remote work status is permanent and never subject to review.",
        "The legal department recently hired two new paralegals.",
    ),
    (
        "Employees working remotely from a different time zone must overlap at least four hours with headquarters.",
        "Remote workers in other time zones need to share a significant portion of working hours with the main office.",
        "Employees can work from any time zone with no requirement to align with headquarters hours.",
        "The company canteen now accepts contactless payments.",
    ),
]

PAYMENT_TERMS = [
    (
        "All invoices must be paid within 30 days of receipt.",
        "Payment for invoices is due within one month after they are received.",
        "Invoices can be paid at any time with no deadline or time constraint.",
        "The company recently opened a new branch office in Seattle.",
    ),
    (
        "Late payments incur a penalty of 1.5% per month on the outstanding balance.",
        "Overdue invoices are subject to monthly interest charges.",
        "There are no penalties or fees associated with late payments.",
        "The HR department is organizing a team-building retreat next month.",
    ),
    (
        "Invoices must be submitted by the 15th of each month to be processed in the current billing cycle.",
        "To ensure timely processing, invoices should be sent before the middle of the month.",
        "Invoices can be submitted at any point during the month without affecting processing time.",
        "The company switched to renewable energy sources for its headquarters.",
    ),
    (
        "Payment can be made via wire transfer, ACH, or company check.",
        "Multiple electronic and traditional payment methods are accepted.",
        "The only accepted form of payment is cash delivered in person.",
        "Employees receive a 20% discount at the company store.",
    ),
    (
        "A 2% discount is applied to invoices paid within 10 days of receipt.",
        "Early payment of invoices is incentivized with a small discount.",
        "No discounts are offered regardless of how quickly an invoice is paid.",
        "The company picnic is scheduled for the last Saturday of July.",
    ),
    (
        "For contracts exceeding $50,000, payment may be made in quarterly installments.",
        "Large contracts allow for payment to be spread across multiple quarters.",
        "All contracts must be paid in full upfront regardless of the total amount.",
        "The design team uses Adobe Creative Suite for all projects.",
    ),
    (
        "All payments must be made in US dollars unless otherwise specified in the contract.",
        "The default currency for transactions is USD.",
        "Payments can only be made in cryptocurrency or foreign currencies.",
        "The company sponsors a local youth soccer team.",
    ),
    (
        "A valid purchase order number must be included on every invoice submission.",
        "Invoices require a reference purchase order to be processed.",
        "Invoices can be submitted without any purchase order or reference number.",
        "The office Wi-Fi password is changed every 90 days.",
    ),
    (
        "Employee expense reimbursements are processed within 14 business days of approval.",
        "Approved expenses are paid back to employees within about three weeks.",
        "Expense reimbursements take a minimum of six months to process.",
        "The company provides free coffee and snacks in the break room.",
    ),
    (
        "Service fees are subject to an annual adjustment of up to 5% based on market conditions.",
        "Prices for services may increase by a small percentage each year.",
        "Service fees are permanently fixed and will never change under any circumstances.",
        "The company's fiscal year runs from April to March.",
    ),
]

TERMINATION = [
    (
        "Employees must provide at least 30 days written notice before resigning.",
        "A one-month advance notification in writing is required before an employee leaves.",
        "Employees can resign effective immediately without any prior notice.",
        "The company gym is open to all employees from 6 AM to 10 PM.",
    ),
    (
        "Terminated employees are entitled to severance pay equal to two weeks per year of service.",
        "Workers who are let go receive compensation proportional to their tenure.",
        "The company does not provide any severance pay under any circumstances.",
        "The engineering team adopted a new code review process last sprint.",
    ),
    (
        "All company property including laptops, badges, and keys must be returned on the last day of employment.",
        "Departing employees are required to hand back all company-issued items.",
        "Employees may keep all company equipment after their employment ends.",
        "The company offers tuition reimbursement for approved courses.",
    ),
    (
        "An exit interview with HR is mandatory for all departing employees.",
        "Every employee leaving the company must participate in a formal exit discussion.",
        "Exit interviews are entirely optional and rarely conducted.",
        "The sales team exceeded their quarterly targets by 15%.",
    ),
    (
        "Former employees are bound by a non-compete clause for 12 months after departure.",
        "Ex-employees cannot work for a direct competitor for one year after leaving.",
        "There are no restrictions on where former employees can work after leaving.",
        "The company lobby was recently redecorated with modern artwork.",
    ),
    (
        "Employees terminated for gross misconduct are not eligible for severance benefits.",
        "Workers fired for serious violations forfeit their severance package.",
        "All terminated employees receive full severance regardless of the reason for termination.",
        "The IT help desk operates 24 hours a day, seven days a week.",
    ),
    (
        "Employees on probation may be terminated with only one week's notice.",
        "During the probationary period, the notice requirement for termination is shortened.",
        "Probationary employees require the same 90-day notice as all other staff.",
        "The company donates 1% of annual revenue to charitable causes.",
    ),
    (
        "Resignation must be submitted in writing to the employee's direct manager and HR.",
        "A formal written resignation addressed to both the supervisor and human resources is required.",
        "Employees can resign verbally with no written documentation needed.",
        "The company recently updated its logo and brand guidelines.",
    ),
    (
        "The final paycheck including accrued vacation must be issued within 72 hours of the last working day.",
        "Departing employees receive their remaining pay and unused vacation within three days.",
        "Final paychecks are issued no earlier than 90 days after an employee's last day.",
        "The data center migration is scheduled for next quarter.",
    ),
    (
        "Health insurance coverage continues for 60 days after the date of termination.",
        "Former employees retain their medical benefits for two months after leaving.",
        "Health insurance is canceled immediately on the employee's last working day.",
        "The company cafeteria now offers gluten-free options.",
    ),
]

LEAVE_POLICY = [
    (
        "Full-time employees are entitled to 20 days of paid annual leave per year.",
        "Permanent staff receive four weeks of paid vacation annually.",
        "Employees do not receive any paid time off during their employment.",
        "The company recently installed solar panels on the office roof.",
    ),
    (
        "Sick leave requires a medical certificate if the absence exceeds three consecutive days.",
        "Employees taking more than three sick days in a row must provide a doctor's note.",
        "No medical documentation is ever required for sick leave regardless of duration.",
        "The company offers a matching 401(k) retirement plan.",
    ),
    (
        "New mothers are entitled to 16 weeks of paid maternity leave.",
        "Female employees receive approximately four months of paid leave after childbirth.",
        "The company does not offer any paid maternity leave.",
        "Office temperatures are maintained between 68 and 72 degrees Fahrenheit.",
    ),
    (
        "Unused annual leave up to 5 days may be carried forward to the next calendar year.",
        "Employees can roll over a small portion of their unused vacation days.",
        "All unused vacation days expire at the end of the year with no carry-forward option.",
        "The company newsletter is published on the first Monday of each month.",
    ),
    (
        "The company observes 10 public holidays per year as paid days off.",
        "Employees get ten national holidays off with full pay each year.",
        "No public holidays are recognized by the company as paid days off.",
        "The company signed a new partnership with a European distributor.",
    ),
    (
        "Leave requests must be submitted at least two weeks in advance through the HR portal.",
        "Employees need to file their time-off requests 14 days before the planned absence.",
        "Leave can be taken at any time without prior notice or approval.",
        "The company uses Slack as its primary internal communication tool.",
    ),
    (
        "Employees may take up to 30 days of unpaid leave per year with manager approval.",
        "Workers can request an extended unpaid absence of up to one month annually.",
        "Unpaid leave is not available to any employee under any circumstances.",
        "The company headquarters is located in the downtown financial district.",
    ),
    (
        "Three days of paid bereavement leave are granted for the loss of an immediate family member.",
        "Employees receive paid time off to grieve the death of a close relative.",
        "The company does not provide any bereavement leave.",
        "The company recently launched an employee mentorship program.",
    ),
    (
        "Emergency leave of up to 5 days may be granted without prior approval in urgent situations.",
        "In critical circumstances, employees can take several days off without advance notice.",
        "All leave, including emergencies, requires at least 30 days of advance approval.",
        "The company parking lot has 200 spaces available for employees.",
    ),
    (
        "Employees who do not use their leave may encash up to 10 days at their daily rate.",
        "Workers can convert a portion of their unused vacation days into cash.",
        "Leave encashment is not available and unused days are simply forfeited.",
        "The R&D department is working on a next-generation product prototype.",
    ),
]

CONFIDENTIALITY = [
    (
        "All employees must sign a non-disclosure agreement before accessing proprietary information.",
        "A signed NDA is a prerequisite for viewing any confidential company data.",
        "Employees can freely access all proprietary information without signing any agreements.",
        "The office building has a rooftop terrace available for employee use.",
    ),
    (
        "Confidentiality obligations remain in effect for five years after the end of employment.",
        "Former employees are bound by secrecy requirements for half a decade after leaving.",
        "Confidentiality obligations expire immediately when an employee leaves the company.",
        "The company softball team practices every Tuesday evening.",
    ),
    (
        "Client data must be stored exclusively on company-approved encrypted storage systems.",
        "Sensitive customer information can only be kept on authorized secure platforms.",
        "Client data may be stored on personal devices and public cloud services without restriction.",
        "The marketing budget was increased by 12% for the upcoming fiscal year.",
    ),
    (
        "Employees are prohibited from discussing company strategy on personal social media accounts.",
        "Sharing internal business plans on private social media profiles is not allowed.",
        "Employees are encouraged to post about company strategy on their personal social media.",
        "The company cafeteria menu changes every two weeks.",
    ),
    (
        "All internal documents must be classified as Public, Internal, Confidential, or Restricted.",
        "Company documents are categorized into four levels of sensitivity.",
        "Documents do not require any classification and are all treated equally.",
        "The company provides free transit passes to all employees.",
    ),
    (
        "Unauthorized disclosure of trade secrets may result in immediate termination and legal action.",
        "Leaking proprietary information can lead to both job loss and a lawsuit.",
        "Sharing trade secrets with competitors carries no consequences.",
        "The annual company retreat will be held in the mountains this year.",
    ),
    (
        "Confidential information may not be shared with third parties without written executive approval.",
        "Disclosing sensitive data to external parties requires formal authorization from leadership.",
        "Employees can share any company information with outside parties at their discretion.",
        "The company recently upgraded its elevator system.",
    ),
    (
        "All company laptops must use full-disk encryption and require biometric authentication.",
        "Corporate computers are required to have advanced security measures including encryption.",
        "Company laptops have no security requirements and employees can disable all protections.",
        "Free fruit baskets are delivered to each floor every Monday morning.",
    ),
    (
        "Employees must follow the clean desk policy and secure all documents before leaving the office.",
        "Workers are required to put away and lock up sensitive papers when they leave their workspace.",
        "Employees can leave confidential documents openly on their desks overnight.",
        "The company offers free yoga classes during lunch breaks.",
    ),
    (
        "Visitors to secure areas must be accompanied by an authorized employee at all times.",
        "Guests in restricted zones require a staff escort throughout their visit.",
        "Visitors are free to wander anywhere in the building without supervision.",
        "The company recently planted trees in the courtyard for environmental sustainability.",
    ),
]

SALARY = [
    (
        "Salaries are paid on the last business day of each month via direct deposit.",
        "Employees receive their monthly pay through bank transfer at month-end.",
        "Employees are paid in cash on a weekly basis every Friday.",
        "The company provides standing desks to employees who request them.",
    ),
    (
        "Overtime work beyond 40 hours per week is compensated at 1.5 times the regular hourly rate.",
        "Extra hours worked past the standard work week are paid at a premium rate.",
        "Overtime work is not compensated and is considered part of normal duties.",
        "The company organizes a hackathon event twice per year.",
    ),
    (
        "Annual performance bonuses of up to 15% of base salary are awarded based on individual and company performance.",
        "Employees may receive a year-end bonus proportional to their performance ratings.",
        "The company does not offer any performance-based bonuses.",
        "The office has a dedicated quiet room for meditation and relaxation.",
    ),
    (
        "Salary reviews are conducted annually in March and adjustments take effect in April.",
        "Employee compensation is evaluated once a year with changes applied in the spring.",
        "Salaries are never reviewed or adjusted after the initial offer.",
        "The company provides free parking for bicycle commuters.",
    ),
    (
        "Employee stock options vest over a four-year period with a one-year cliff.",
        "Equity grants become available gradually over four years with the first portion after one year.",
        "All stock options are fully vested on the employee's first day.",
        "The company kitchen is stocked with complimentary beverages.",
    ),
    (
        "A cost-of-living adjustment of 3% is applied automatically to all salaries each January.",
        "Wages are increased annually to keep pace with inflation.",
        "Salaries remain completely static and are never adjusted for cost of living.",
        "The company recently hired a new Chief Technology Officer.",
    ),
    (
        "Salary advances of up to one month's pay may be requested in cases of financial hardship.",
        "Employees facing financial difficulties can receive an early partial payment of their salary.",
        "Salary advances are strictly prohibited under all circumstances.",
        "The company hosts a bring-your-pet-to-work day once a month.",
    ),
    (
        "The total benefits package, including health, dental, and retirement, equals approximately 30% of base salary.",
        "Employee benefits add roughly a third more to the value of their cash compensation.",
        "The company does not provide any benefits beyond the base salary.",
        "The company recently redesigned its website with a new user interface.",
    ),
    (
        "All employees performing similar roles at the same level receive equal base compensation.",
        "The company maintains pay equity across employees in equivalent positions.",
        "Salary for the same role varies widely based on negotiation and personal connections.",
        "The company's annual report is published in the first quarter of each year.",
    ),
    (
        "Sales employees earn a base salary plus a 10% commission on all deals closed.",
        "Revenue-generating staff receive a fixed salary supplemented by performance-based commissions.",
        "Sales employees receive no commission and are paid only a flat salary.",
        "The engineering team recently migrated the codebase to a monorepo structure.",
    ),
]

DEADLINES = [
    (
        "All project milestones must be completed by the dates specified in the project charter.",
        "Teams are required to meet the deadlines outlined in the official project plan.",
        "Project milestones are purely aspirational and carry no obligation to be met on time.",
        "The company provides noise-canceling headphones to all open-office employees.",
    ),
    (
        "Deadline extensions must be requested in writing at least 5 business days before the original due date.",
        "Requests to push back a due date need to be submitted formally well before the deadline.",
        "Deadline extensions are granted automatically without any formal request process.",
        "The company uses Jira for project tracking and task management.",
    ),
    (
        "Late deliverables are subject to a penalty of 2% of the contract value per week of delay.",
        "Missing a delivery date results in financial penalties that increase weekly.",
        "There are no penalties for delivering work late, regardless of the delay duration.",
        "The office has a game room with a ping-pong table and foosball.",
    ),
    (
        "Quarterly financial reports must be submitted to the board by the 10th of the following month.",
        "Financial summaries are due to the board within ten days after each quarter ends.",
        "There is no fixed deadline for submitting quarterly financial reports to the board.",
        "The company offers a generous employee referral bonus program.",
    ),
    (
        "Client deliverables have a service level agreement requiring delivery within 48 hours of request.",
        "Customer-facing work must be completed within two business days of being requested.",
        "Client deliverables have no time constraints and can be completed whenever convenient.",
        "The company is considering expanding into the Asian market next year.",
    ),
    (
        "Development sprints are two weeks long and begin on the first Monday of the cycle.",
        "Each sprint lasts 14 days and kicks off at the start of the work week.",
        "Sprint durations are undefined and can last anywhere from one day to six months.",
        "The company provides annual flu vaccinations free of charge.",
    ),
    (
        "A grace period of 48 hours is allowed for document submissions after the stated deadline.",
        "Submissions received within two days after the due date are still considered on time.",
        "No grace period exists and any submission received even one minute late is rejected.",
        "The company has a pet-friendly policy in its San Francisco office.",
    ),
    (
        "Issues unresolved within 24 hours must be escalated to the department director.",
        "Problems that persist for more than a day require management-level escalation.",
        "Issues can remain unresolved indefinitely with no requirement for escalation.",
        "The company recently switched to compostable cups in all kitchens.",
    ),
    (
        "Service contracts must be renewed no later than 30 days before the expiration date.",
        "Contract renewals need to be completed at least a month before the contract ends.",
        "Contracts automatically renew forever and never require any action for renewal.",
        "The company's employee satisfaction survey runs every September.",
    ),
    (
        "End of day for deadline purposes is defined as 5:00 PM in the company's headquarters time zone.",
        "The cutoff time for meeting daily deadlines is 5 PM at the main office location.",
        "There is no defined end-of-day time and deadlines can be met at any hour.",
        "The company provides complimentary dry-cleaning services for executives.",
    ),
]

ALL_TOPICS = {
    "remote_work": REMOTE_WORK,
    "payment_terms": PAYMENT_TERMS,
    "termination": TERMINATION,
    "leave_policy": LEAVE_POLICY,
    "confidentiality": CONFIDENTIALITY,
    "salary": SALARY,
    "deadlines": DEADLINES,
}

# ---------------------------------------------------------------------------
# Augmentation helpers
# ---------------------------------------------------------------------------

PREMISE_PREFIXES = [
    "The company policy states that ",
    "According to the employee handbook, ",
    "As outlined in the contract, ",
    "Per the latest company guidelines, ",
    "The official documentation specifies that ",
    "As per the organization's rules, ",
    "The agreement clearly indicates that ",
    "Company regulations mandate that ",
]

HYPOTHESIS_PREFIXES = [
    "This means that ",
    "In other words, ",
    "Therefore, ",
    "It follows that ",
    "Consequently, ",
    "This implies that ",
    "As a result, ",
    "Put simply, ",
]


def _lower_first(s: str) -> str:
    """Lowercase the first character of a string (for prefix prepending)."""
    if not s:
        return s
    return s[0].lower() + s[1:]


def _augment_pair(premise: str, hypothesis: str) -> tuple[str, str]:
    """Return a variation of (premise, hypothesis) by prepending random prefixes."""
    new_prem = premise
    new_hyp = hypothesis
    if random.random() < 0.6:
        new_prem = random.choice(PREMISE_PREFIXES) + _lower_first(premise)
    if random.random() < 0.4:
        new_hyp = random.choice(HYPOTHESIS_PREFIXES) + _lower_first(hypothesis)
    return new_prem, new_hyp


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def generate_base_pairs() -> list[tuple[str, str, str]]:
    """Expand topic groups into (sentence_a, sentence_b, label) triples."""
    pairs: list[tuple[str, str, str]] = []
    for groups in ALL_TOPICS.values():
        for premise, ent_hyp, con_hyp, neu_hyp in groups:
            pairs.append((premise, ent_hyp, "entailment"))
            pairs.append((premise, con_hyp, "contradiction"))
            pairs.append((premise, neu_hyp, "neutral"))
    return pairs


def generate_cross_topic_neutrals(n: int = 350) -> list[tuple[str, str, str]]:
    """Pair premises from one topic with hypotheses from a different topic → neutral."""
    topics = list(ALL_TOPICS.keys())
    all_premises: dict[str, list[str]] = {}
    all_hypotheses: dict[str, list[str]] = {}

    for topic, groups in ALL_TOPICS.items():
        all_premises[topic] = [g[0] for g in groups]
        # Use the entailment hypotheses as the "hypothesis" pool
        all_hypotheses[topic] = [g[1] for g in groups]

    pairs: list[tuple[str, str, str]] = []
    attempts = 0
    seen: set[tuple[str, str]] = set()

    while len(pairs) < n and attempts < n * 10:
        attempts += 1
        t1, t2 = random.sample(topics, 2)
        p = random.choice(all_premises[t1])
        h = random.choice(all_hypotheses[t2])
        if (p, h) not in seen:
            seen.add((p, h))
            pairs.append((p, h, "neutral"))
    return pairs


def augment_to_target(
    base: list[tuple[str, str, str]],
    target: int = 2000,
) -> list[tuple[str, str, str]]:
    """Augment pairs with prefix variations to reach the target count, balanced by label."""
    from collections import Counter

    counts = Counter(label for _, _, label in base)
    target_per_label = target // 3

    by_label: dict[str, list[tuple[str, str, str]]] = {
        "entailment": [],
        "neutral": [],
        "contradiction": [],
    }
    for sa, sb, lbl in base:
        by_label[lbl].append((sa, sb, lbl))

    augmented: list[tuple[str, str, str]] = list(base)
    seen = {(sa, sb) for sa, sb, _ in base}

    for label in ["entailment", "neutral", "contradiction"]:
        needed = target_per_label - counts[label]
        pool = by_label[label]
        added = 0
        attempts = 0
        while added < needed and attempts < needed * 20:
            attempts += 1
            sa, sb, lbl = random.choice(pool)
            new_sa, new_sb = _augment_pair(sa, sb)
            if (new_sa, new_sb) not in seen:
                seen.add((new_sa, new_sb))
                augmented.append((new_sa, new_sb, lbl))
                added += 1

    return augmented


def main() -> None:
    print("🏗️  Generating domain-specific NLI pairs …")

    # Step 1: base pairs from templates (210 = 70 groups × 3 labels)
    base = generate_base_pairs()
    print(f"  Base pairs:         {len(base):>5}")

    # Step 2: cross-topic neutrals (350)
    cross = generate_cross_topic_neutrals(350)
    base.extend(cross)
    print(f"  + cross-topic neut: {len(cross):>5}")

    # Step 3: augment to ~2000, balanced
    final = augment_to_target(base, target=2001)
    random.shuffle(final)
    print(f"  After augmentation: {len(final):>5}")

    # Write CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sentence_a", "sentence_b", "label"])
        writer.writerows(final)

    # Summary
    from collections import Counter
    counts = Counter(lbl for _, _, lbl in final)
    print(f"\n✅ Saved {len(final)} pairs → {OUTPUT_FILE}")
    for lbl in ["entailment", "neutral", "contradiction"]:
        print(f"   {lbl:15s}: {counts[lbl]:>5}")


if __name__ == "__main__":
    main()
