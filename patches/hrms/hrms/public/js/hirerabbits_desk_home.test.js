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

function renderHomeWith(desktopIcons, workspaceItems = {}) {
	let home;
	const clickHandlers = [];
	let editStarted = false;
	const el = () => ({
		_text: "",
		get textContent() {
			return this._text;
		},
		set textContent(value) {
			this._text = value;
		},
		innerHTML: "",
		querySelector(selector) {
			if (selector === "h1" || selector === ".hr-hello p") return el();
			if (selector === ".hr-stats" || selector === ".hr-board-wrap") return el();
			return null;
		},
		after(node) {
			home = node;
		},
	});
	const navbar = el();
	const wrapper = {
		querySelector(selector) {
			if (selector === ".desktop-navbar") return navbar;
			if (selector === ".hr-home") return null;
			return null;
		},
		querySelectorAll() {
			return [];
		},
	};
	const context = {
		console,
		URL,
		location: { pathname: "/desk", search: "", hash: "", origin: "http://suite.localhost:8010" },
		history: { replaceState() {} },
		matchMedia: () => ({ matches: true }),
		requestAnimationFrame: (fn) => fn(),
		MutationObserver: class {
			observe() {}
		},
		document: {
			body: {},
			querySelector: (selector) => (selector === ".desktop-wrapper" ? wrapper : null),
			querySelectorAll: () => [],
			addEventListener(type, handler) {
				if (type === "click") clickHandlers.push(handler);
			},
			createElement() {
				return el();
			},
		},
		frappe: {
			session: {},
			desktop_icons: desktopIcons,
			boot: { desktop_icons: desktopIcons, workspace_sidebar_item: workspaceItems, allowed_workspaces: [], module_app: {} },
			defaults: { get_default: () => "" },
			pages: { desktop: { desktop_page: { edit_mode: false, start_editing_layout: () => { editStarted = true; } } } },
			router: {
				hirerabbitsNamespaces: false,
				convert_to_standard_route: (route) => route,
				make_url: (params) => `/desk/${params.join("/")}`,
				push_state() {},
				route() {},
				slug: (value) => String(value).toLowerCase().replace(/ /g, "-"),
			},
			utils: {
				escape_html: (value) => String(value),
				icon: (name) => `<i>${name}</i>`,
				generate_route: (item) => `/desk/${String(item.name || item.doctype || item.link_to).toLowerCase().replace(/ /g, "-")}`,
			},
			call: ({ callback }) => callback({ message: {} }),
			xcall: () => ({ then: () => ({ catch() {} }) }),
		},
		__: (value) => value,
	};
	context.window = context;
	context.globalThis = context;
	vm.runInNewContext(fs.readFileSync(require.resolve("./hirerabbits_desk_home.js"), "utf8"), context);
	clickHandlers.forEach((handler) => handler({
		preventDefault() {},
		target: { closest: (selector) => selector === "[data-hr-edit-layout]" },
	}));
	return { html: home.innerHTML, editStarted, newDesktopIcons: context.frappe.new_desktop_icons };
}

const orphanedChildHome = renderHomeWith([
	{ name: "ERP", label: "ERP", idx: 1, hidden: 1, link_type: "External", link: "/desk/erp" },
	{ name: "Selling", label: "Selling", idx: 2, parent_icon: "ERP" },
], {
	selling: { items: [{ type: "Link", link_type: "Workspace", link_to: "Selling" }] },
});
assert.match(orphanedChildHome.html, /href="\/desk\/selling"/);
assert.doesNotMatch(orphanedChildHome.html, /data-hr-edit-layout/);
assert.equal(orphanedChildHome.editStarted, false);
assert.equal(orphanedChildHome.newDesktopIcons, undefined);

const folderHome = renderHomeWith([
	{ name: "Favorites", label: "Favorites", idx: 1 },
	{ name: "CRM", label: "CRM", idx: 2, parent_icon: "Favorites", link_type: "External", link: "/crm" },
	{ name: "Support", label: "Support", idx: 3, parent_icon: "Favorites", link_type: "External", link: "/helpdesk" },
]);
assert.match(folderHome.html, /href="\/crm"/);
assert.match(folderHome.html, /href="\/helpdesk"/);

const preferredAppOrderHome = renderHomeWith([
	{ name: "Support", label: "Support", idx: 1, link_type: "External", link: "/helpdesk" },
	{ name: "ERP", label: "ERP", idx: 2, link_type: "External", link: "/desk/erp" },
	{ name: "Admin", label: "Admin", idx: 3, link_type: "External", link: "/desk/admin" },
	{ name: "CRM", label: "CRM", idx: 99, link_type: "External", link: "/crm" },
]);
assert.ok(preferredAppOrderHome.html.indexOf('href="/crm"') < preferredAppOrderHome.html.indexOf('href="/desk/erp"'));
assert.ok(preferredAppOrderHome.html.indexOf('href="/desk/erp"') < preferredAppOrderHome.html.indexOf('href="/helpdesk"'));

function renderListBoard() {
	const context = {
		frappe: {
			utils: { escape_html: (value) => String(value) },
			avatar: (user) => `<span class="avatar">${user}</span>`,
		},
		__: (value) => value,
	};
	vm.createContext(context);
	const source = fs.readFileSync(require.resolve("./hirerabbits_desk_home.js"), "utf8");
	const start = source.indexOf("const esc =");
	const end = source.indexOf("\n\tfunction renderBoards", start);
	vm.runInContext(`${source.slice(start, end)}\nthis.boardHtml = boardHtml;`, context);
	return context.boardHtml({
		route: "/desk/task",
		columns: [{ status: "Open", label: "Open", count: 1, color: "blue" }],
		cards: [{ title: "Call candidate", status: "Open", route: "/desk/task/TASK-1", user: "user@example.com" }],
	}, "list");
}

const rowHtml = renderListBoard();
const firstRow = rowHtml.match(/<a class="hr-row"[\s\S]*?<\/a>/)[0];
assert.equal((firstRow.match(/<span\b/g) || []).length, 4);
assert.match(firstRow, /class="avatar"/);
