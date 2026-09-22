(function () {
	let deferredInstallPrompt = null;

	window.addEventListener("beforeinstallprompt", (event) => {
		event.preventDefault();
		deferredInstallPrompt = event;
	});

	function isHRMSDesk() {
		const route = window.frappe?.get_route?.() || [];
		const workspace = route[0] === "Workspaces" ? route[route.length - 1] : "";
		return location.pathname.includes("/desk/hr-setup") || ["HR Setup", "HRMS"].includes(workspace);
	}

	function installApp() {
		if (deferredInstallPrompt) {
			deferredInstallPrompt.prompt();
			deferredInstallPrompt = null;
			return;
		}
		window.open("/hrms", "_blank");
	}

	function makeItem() {
		const item = document.createElement("div");
		item.id = "hirerabbits-desk-install";
		item.className = "standard-sidebar-item";
		item.innerHTML = `
			<a class="item-anchor" href="#" title="Install app">
				<span class="sidebar-item-icon">
					<svg class="icon icon-md" aria-hidden="true">
						<use href="#icon-download"></use>
					</svg>
				</span>
				<span class="sidebar-item-label">Install app</span>
			</a>
		`;
		item.addEventListener("click", (event) => {
			event.preventDefault();
			installApp();
		});
		return item;
	}

	function ensureInstallItem() {
		const existing = document.getElementById("hirerabbits-desk-install");
		if (!isHRMSDesk()) {
			existing?.remove();
			return;
		}
		if (existing) return;

		const sidebar = document.querySelector(".standard-sidebar");
		if (!sidebar) return;

		const settingsItem = Array.from(sidebar.querySelectorAll(".standard-sidebar-item")).find(
			(item) => item.textContent.trim() === "Settings"
		);
		(settingsItem || sidebar).insertAdjacentElement(settingsItem ? "afterend" : "beforeend", makeItem());
	}

	setInterval(ensureInstallItem, 500);
	window.addEventListener("hashchange", ensureInstallItem);
	window.addEventListener("popstate", ensureInstallItem);
})();
