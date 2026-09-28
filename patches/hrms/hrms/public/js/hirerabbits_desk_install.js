(function () {
	let deferredInstallPrompt = null;
	const hrmsWorkspaces = new Set([
		"HRMS",
		"HR Setup",
		"Expenses",
		"Leaves",
		"Payroll",
		"Shift & Attendance",
		"Recruitment",
		"Performance",
		"Tax & Benefits",
		"Employee Lifecycle",
	]);

	function ensureNavbarLogoSize() {
		if (document.querySelector("#hirerabbits-navbar-logo-size")) return;
		const style = document.createElement("style");
		style.id = "hirerabbits-navbar-logo-size";
		style.textContent = `
			.navbar-home img[src*="hirerabbits-logo-tight"] {
				width: auto !important;
				height: 34px !important;
				max-width: 150px !important;
				object-fit: contain;
			}
		`;
		document.head.appendChild(style);
	}

	window.addEventListener("beforeinstallprompt", (event) => {
		event.preventDefault();
		deferredInstallPrompt = event;
	});

	function isHRMSDesk(sidebarHeader) {
		const route = window.frappe?.get_route?.() || [];
		const workspace = route[0] === "Workspaces" ? route[route.length - 1] : "";
		const headerTitle = sidebarHeader?.sidebar?.sidebar_title || document.querySelector(".header-title")?.textContent?.trim();
		const headerSubtitle = document.querySelector(".header-subtitle")?.textContent?.trim();
		return ["/desk/hrms", "/desk/hr-setup"].some((path) => location.pathname.includes(path))
			|| hrmsWorkspaces.has(workspace)
			|| hrmsWorkspaces.has(headerTitle)
			|| headerSubtitle === "HRMS";
	}

	function installApp() {
		if (deferredInstallPrompt) {
			deferredInstallPrompt.prompt();
			deferredInstallPrompt = null;
			return;
		}
		window.open("/hrms/login?install=1", "_blank");
	}

	function addInstallMenuItem(items) {
		if (!items || items.some((item) => item.name === "hirerabbits-install-app" || item.label === "Install app")) return;
		const index = items.findIndex((item) => item.name === "website" || item.is_divider);
		items.splice(index < 0 ? items.length : index, 0, {
			name: "hirerabbits-install-app",
			label: "Install app",
			icon: "download",
			onClick: installApp,
		});
	}

	function installSidebarMenuPatch() {
		ensureNavbarLogoSize();
		const SidebarHeader = window.frappe?.ui?.SidebarHeader;
		if (!SidebarHeader || SidebarHeader.prototype.hirerabbitsInstallPatch) return Boolean(SidebarHeader);
		SidebarHeader.prototype.hirerabbitsInstallPatch = true;
		const originalSetupAppSwitcher = SidebarHeader.prototype.setup_app_switcher;
		SidebarHeader.prototype.setup_app_switcher = function () {
			if (isHRMSDesk(this)) addInstallMenuItem(this.dropdown_items);
			return originalSetupAppSwitcher.apply(this, arguments);
		};
		return true;
	}

	const timer = setInterval(() => {
		if (installSidebarMenuPatch()) clearInterval(timer);
	}, 250);
	installSidebarMenuPatch();
})();
