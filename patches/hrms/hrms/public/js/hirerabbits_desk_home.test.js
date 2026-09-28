const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

function load(pathname, sidebarTitle, preferred, fallbackWorkspace) {
	const labels = [];
	const context = {
		console,
		URL,
		localStorage: preferred ? { [`preferred_breadcrumbs:${preferred.doctype}`]: preferred.module } : {},
		location: { pathname, search: "", hash: "", origin: "http://suite.localhost:8010" },
		history: { replaceState() {} },
		matchMedia: () => ({ matches: true }),
		requestAnimationFrame: (fn) => fn(),
		MutationObserver: class {
			observe() {}
		},
		document: {
			body: {},
			querySelector: () => null,
			querySelectorAll: () => [],
			addEventListener() {},
		},
		frappe: {
			session: {},
			boot: {
				allowed_workspaces: [
					{ name: "HR Setup", module: "HR", app: "hrms" },
					{ name: "Stock", module: "Stock", app: "erpnext" },
					{ name: "CRM", module: "CRM", app: "crm" },
					{ name: "Support", module: "Support", app: "helpdesk" },
				],
				module_app: { HR: "hrms", Stock: "erpnext", CRM: "crm", Support: "helpdesk" },
			},
			app: { sidebar: { sidebar_title: sidebarTitle } },
			router: {
				hirerabbitsNamespaces: false,
				convert_to_standard_route: (route) => route,
				make_url: (params) => `/desk/${params.join("/")}`,
				push_state() {},
				route() {},
			},
			utils: {
				generate_route: (item) => `/desk/${String(item.name || item.doctype).toLowerCase().replace(/ /g, "-")}`,
				get_desktop_icon_by_label: (label) => ({ label }),
				get_route_for_icon: (icon) => `/desk/${String(icon.label).toLowerCase().replace(/ /g, "-")}`,
			},
			call: ({ callback }) => callback({ message: {} }),
			breadcrumbs: {
				get_doctype_module(doctype) {
					return context.localStorage[`preferred_breadcrumbs:${doctype}`];
				},
				set_workspace(breadcrumbs) {
					const preferredModule = this.get_doctype_module(breadcrumbs.doctype);
					breadcrumbs.workspace = preferredModule || fallbackWorkspace;
				},
				set_workspace_breadcrumb(breadcrumbs) {
					if (!breadcrumbs.workspace) this.set_workspace(breadcrumbs);
					this.append_breadcrumb_element("", context.frappe.app.sidebar.sidebar_title);
				},
				append_breadcrumb_element(_url, label) {
					labels.push(label);
				},
			},
		},
		__: (value) => value,
	};
	context.window = context;
	context.globalThis = context;

	vm.runInNewContext(fs.readFileSync(require.resolve("./hirerabbits_desk_home.js"), "utf8"), context);
	context.frappe.breadcrumbs.set_workspace_breadcrumb({ doctype: preferred?.doctype || "Item" });
	return labels.at(-1);
}

assert.equal(load("/desk/hrms/attendance", "Stock", { doctype: "Attendance", module: "Stock" }, "HR Setup"), "HR Setup");
assert.equal(load("/desk/erp/item", "HR Setup", { doctype: "Item", module: "HR" }, "Stock"), "Stock");
assert.equal(load("/desk/hrms/attendance", "CRM", { doctype: "Attendance", module: "CRM" }, "HR Setup"), "HR Setup");
assert.equal(load("/desk/erp/item", "Support", { doctype: "Item", module: "Support" }, "Stock"), "Stock");
