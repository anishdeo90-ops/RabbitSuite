from datetime import date, timedelta

import frappe


PREFIX = "HR Demo"

SEED_PLAN = {
    "hrms": [
        "Employee",
        "Leave Allocation",
        "Leave Application",
        "Attendance",
        "Attendance Request",
        "Employee Checkin",
        "Shift Assignment",
        "Shift Request",
        "Expense Claim",
        "Employee Advance",
        "Salary Slip",
        "Job Opening",
        "Job Applicant",
        "Interview",
        "Job Offer",
        "Appointment Letter",
    ],
    "support": ["HD Customer", "HD Team", "HD Agent", "HD Ticket", "HD Article"],
    "crm": ["CRM Organization", "CRM Contacts", "CRM Lead", "CRM Deal", "CRM Task"],
    "erp": ["Customer", "Supplier", "Item", "Sales Order", "Sales Invoice", "Project"],
}


def first_value(doctype, field="name", filters=None, fallback=None):
    return frappe.db.get_value(doctype, filters or {}, field) or fallback


def exists(doctype, name):
    return bool(name and frappe.db.exists(doctype, name))


def save_doc(doctype, name=None, **fields):
    if name and exists(doctype, name):
        return frappe.get_doc(doctype, name)

    doc = frappe.get_doc({"doctype": doctype, **fields})
    if name:
        doc.name = name
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_permissions = True
    return doc.insert(ignore_permissions=True, ignore_mandatory=True)


def save_by(doctype, filters, **fields):
    name = first_value(doctype, filters=filters)
    if name:
        return frappe.get_doc(doctype, name)
    return save_doc(doctype, None, **{**filters, **fields})


def submit_if_draft(doc):
    if getattr(doc, "docstatus", 0) == 0:
        doc.flags.ignore_permissions = True
        doc.submit()
    return doc


def seed_hrms(company):
    today = date.today()
    department = save_doc("Department", f"{PREFIX} Operations - RR", department_name=f"{PREFIX} Operations", company=company)
    designation = save_doc("Designation", f"{PREFIX} Specialist", designation_name=f"{PREFIX} Specialist")
    leave_type = save_doc("Leave Type", f"{PREFIX} PTO", leave_type_name=f"{PREFIX} PTO", is_lwp=0)
    lwp_leave_type = save_doc("Leave Type", f"{PREFIX} LWP", leave_type_name=f"{PREFIX} LWP", is_lwp=1)
    shift_type = save_doc("Shift Type", f"{PREFIX} General", start_time="09:00:00", end_time="18:00:00")

    employees = []
    for i, first in enumerate(["Asha", "Ben", "Cora", "Dev", "Esha", "Farhan"], start=1):
        emp = save_by(
            "Employee",
            {"employee_name": f"{first} Demo", "company": company},
            first_name=first,
            last_name="Demo",
            status="Active",
            gender="Female" if first in {"Asha", "Cora", "Esha"} else "Male",
            date_of_birth=str(today.replace(year=today.year - 28) - timedelta(days=i * 240)),
            date_of_joining=str(today - timedelta(days=420 - i * 20)),
            department=department.name,
            designation=designation.name,
        )
        employees.append(emp.name)

    for i, emp in enumerate(employees, start=1):
        day = today - timedelta(days=i)
        save_by(
            "Leave Allocation",
            {"employee": emp, "leave_type": leave_type.name, "from_date": str(today.replace(month=1, day=1))},
            to_date=str(today.replace(month=12, day=31)),
            new_leaves_allocated=18,
            total_leaves_allocated=18,
        )
        save_by(
            "Leave Application",
            {"employee": emp, "leave_type": lwp_leave_type.name, "from_date": str(day), "to_date": str(day)},
            total_leave_days=1,
            status="Approved" if i % 2 else "Open",
            leave_approver="Administrator",
            company=company,
        )
        save_by("Attendance", {"employee": emp, "attendance_date": str(day)}, status="Present", company=company)
        save_by("Employee Checkin", {"employee": emp, "time": f"{day} 09:05:00"}, log_type="IN")
        save_by("Employee Checkin", {"employee": emp, "time": f"{day} 18:10:00"}, log_type="OUT")
        save_by("Attendance Request", {"employee": emp, "from_date": str(day), "to_date": str(day)}, reason="Work From Home", company=company)
        save_by("Shift Assignment", {"employee": emp, "shift_type": shift_type.name, "start_date": str(today - timedelta(days=30))})
        save_by("Shift Request", {"employee": emp, "shift_type": shift_type.name, "from_date": str(day), "to_date": str(day)})
        claim = save_by("Expense Claim", {"employee": emp, "company": company, "posting_date": str(day)}, approval_status="Draft")
        if not claim.get("expenses"):
            claim.append("expenses", {"expense_type": first_value("Expense Claim Type", fallback="Travel"), "amount": 500 + i * 100, "sanctioned_amount": 500 + i * 100})
            claim.save(ignore_permissions=True)
        save_by("Employee Advance", {"employee": emp, "company": company, "posting_date": str(day)}, advance_amount=1000 + i * 500)

    earning = save_doc("Salary Component", f"{PREFIX} Basic", salary_component=f"{PREFIX} Basic", type="Earning")
    structure = save_doc("Salary Structure", f"{PREFIX} Salary Structure", company=company, payroll_frequency="Monthly", is_active="Yes")
    if not structure.get("earnings"):
        structure.append("earnings", {"salary_component": earning.name, "amount": 50000})
        structure.save(ignore_permissions=True)
    submit_if_draft(structure)

    for i, emp in enumerate(employees, start=1):
        assignment = save_by("Salary Structure Assignment", {"employee": emp, "salary_structure": structure.name, "from_date": str(today.replace(day=1))}, company=company, base=50000)
        submit_if_draft(assignment)
        slip = save_by("Salary Slip", {"employee": emp, "company": company, "start_date": str(today.replace(day=1)), "end_date": str(today)}, posting_date=str(today), gross_pay=50000, net_pay=50000)
        if not slip.get("earnings"):
            slip.append("earnings", {"salary_component": earning.name, "amount": 50000})
            slip.save(ignore_permissions=True)


def seed_recruitment(company):
    today = date.today()
    department = first_value("Department", filters={"department_name": f"{PREFIX} Operations"}) or first_value("Department")
    designation = first_value("Designation", filters={"designation_name": f"{PREFIX} Specialist"}) or first_value("Designation")
    interview_type = save_by("Interview Type", {"interview_type_name": f"{PREFIX} Screen"}, expected_average_rating=3.5, designation=designation)

    openings = []
    for i, title in enumerate(["Frontend Engineer", "HR Executive", "Support Specialist"], start=1):
        opening = save_by(
            "Job Opening",
            {"job_title": f"{PREFIX} {title}", "company": company},
            designation=designation,
            status="Open",
            posted_on=f"{today} 09:00:00",
            closes_on=str(today + timedelta(days=30)),
            department=department,
            vacancies=i,
            planned_vacancies=i,
            publish=1,
            route=f"hr-demo-{title.lower().replace(' ', '-')}",
            description=f"{PREFIX} seeded opening for {title}.",
        )
        openings.append(opening)

    statuses = ["Open", "Replied", "Accepted", "Hold", "Rejected"]
    for i in range(1, 10):
        opening = openings[(i - 1) % len(openings)]
        applicant = save_by(
            "Job Applicant",
            {"email_id": f"candidate{i}@example.com"},
            applicant_name=f"Candidate {i} Demo",
            phone_number=f"90000000{i:02d}",
            job_title=opening.name,
            designation=designation,
            status=statuses[(i - 1) % len(statuses)],
            applicant_rating=3 + (i % 3) * 0.5,
            cover_letter="Seeded recruitment demo candidate.",
        )
        interview = save_by(
            "Interview",
            {"job_applicant": applicant.name, "scheduled_on": str(today + timedelta(days=i % 5))},
            interview_type=interview_type.name,
            job_opening=opening.name,
            designation=designation,
            status="Pending" if i % 3 else "Cleared",
            from_time="10:00:00",
            to_time="10:30:00",
            expected_average_rating=3.5,
        )
        if i <= 3:
            save_by(
                "Job Offer",
                {"job_applicant": applicant.name},
                applicant_name=applicant.applicant_name,
                applicant_email=applicant.email_id,
                status="Awaiting Response",
                offer_date=str(today),
                designation=designation,
                company=company,
                terms="Seeded demo offer terms.",
            )
            save_by(
                "Appointment Letter",
                {"job_applicant": applicant.name},
                applicant_name=applicant.applicant_name,
                company=company,
                appointment_date=str(today + timedelta(days=14 + i)),
                introduction="Welcome to the Hire Rabbits demo team.",
                closing_notes="Generated as sample recruitment data.",
            )
        interview.save(ignore_permissions=True)


def seed_support():
    customer = save_by("HD Customer", {"customer_name": f"{PREFIX} Customer"})
    team = save_by("HD Team", {"team_name": f"{PREFIX} Support Team"})
    agent_name = first_value("HD Agent", filters={"user": "Administrator"})
    agent = frappe.get_doc("HD Agent", agent_name) if agent_name else save_doc("HD Agent", f"{PREFIX} Agent", user="Administrator")
    for i, subject in enumerate(["Login issue", "Invoice question", "PWA install help", "Leave portal bug", "CRM sync request"], start=1):
        save_by("HD Ticket", {"subject": f"{PREFIX}: {subject}"}, customer=customer.name, team=team.name, agent=agent.name, status="Open", priority="Medium")
    save_by("HD Article", {"title": f"{PREFIX} Getting Started"}, content="Demo knowledge base article.")


def seed_crm():
    org = save_by("CRM Organization", {"organization_name": f"{PREFIX} Org"})
    contact = save_by("CRM Contacts", {"email": "priya.demo@example.com"}, first_name="Priya", last_name="Demo", organization=org.name)
    for i in range(1, 6):
        lead = save_by("CRM Lead", {"email": f"lead{i}@example.com"}, first_name=f"Lead {i}", last_name="Demo", organization=org.name)
        deal = save_by("CRM Deal", {"first_name": f"Deal {i}", "last_name": "Demo", "lead": lead.name}, organization=org.name, status="Qualification")
        save_by("CRM Task", {"title": f"Follow up {i}"}, reference_doctype="CRM Deal", reference_docname=deal.name)


def seed_erp(company):
    customer = save_doc("Customer", f"{PREFIX} Customer", customer_name=f"{PREFIX} Customer", customer_type="Company", customer_group=first_value("Customer Group", fallback="All Customer Groups"), territory=first_value("Territory", fallback="All Territories"))
    supplier = save_doc("Supplier", f"{PREFIX} Supplier", supplier_name=f"{PREFIX} Supplier", supplier_group=first_value("Supplier Group", fallback="All Supplier Groups"))
    item = save_doc("Item", "HR-DEMO-SERVICE", item_code="HR-DEMO-SERVICE", item_name=f"{PREFIX} Service", item_group=first_value("Item Group", fallback="All Item Groups"), stock_uom=first_value("UOM", fallback="Nos"), is_stock_item=0)
    project_name = first_value("Project", filters={"project_name": f"{PREFIX} Project"})
    project = frappe.get_doc("Project", project_name) if project_name else save_doc("Project", None, project_name=f"{PREFIX} Project", company=company, customer=customer.name, status="Open")
    delivery_date = str(date.today() + timedelta(days=7))
    save_by(
        "Sales Order",
        {"customer": customer.name, "transaction_date": str(date.today())},
        company=company,
        delivery_date=delivery_date,
        items=[{"item_code": item.name, "qty": 1, "rate": 25000, "delivery_date": delivery_date}],
    )
    save_by(
        "Sales Invoice",
        {"customer": customer.name, "posting_date": str(date.today()), "project": project.name},
        company=company,
        due_date=str(date.today() + timedelta(days=15)),
        items=[{"item_code": item.name, "qty": 1, "rate": 25000}],
    )
    return supplier


def counts():
    out = {}
    for module, doctypes in SEED_PLAN.items():
        for doctype in doctypes:
            out[doctype] = frappe.db.count(doctype)
    return out


def run(hrms_full=1):
    company = first_value("Company", fallback="Rabbits")
    if hrms_full:
        seed_hrms(company)
        seed_recruitment(company)
        frappe.db.commit()
    seed_support()
    frappe.db.commit()
    seed_crm()
    frappe.db.commit()
    seed_erp(company)
    frappe.db.commit()
    print(counts())
