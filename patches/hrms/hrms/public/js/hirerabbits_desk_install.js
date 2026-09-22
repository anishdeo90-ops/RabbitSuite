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

	function makeMenuItem() {
		const item = document.createElement("div");
		item.id = "hirerabbits-desk-menu-install";
		item.className = "dropdown-menu-item";
		item.innerHTML = `
			<a href="#">
				<span class="frappe-menu-item-icon">
					<svg class="icon icon-sm" aria-hidden="true">
						<use href="#icon-download"></use>
					</svg>
				</span>
				<span class="menu-item-title">Install app</span>
			</a>
		`;
		item.addEventListener("click", (event) => {
			event.preventDefault();
			installApp();
		});
		return item;
	}

	function ensureHeaderMenuItem() {
		if (!isHRMSDesk()) return;
		const menu = Array.from(document.querySelectorAll(".frappe-menu, .dropdown-menu")).find(
			(menu) => menu.textContent.includes("Desktop") && menu.textContent.includes("Logout")
		);
		if (!menu || menu.querySelector("#hirerabbits-desk-menu-install")) return;

		const logoutItem = Array.from(menu.children).find((item) => item.textContent.trim() === "Logout");
		(logoutItem || menu).insertAdjacentElement(logoutItem ? "beforebegin" : "beforeend", makeMenuItem());
	}

	function ensureInstallActions() {
		ensureHeaderMenuItem();
	}

	setInterval(ensureInstallActions, 500);
	window.addEventListener("hashchange", ensureInstallActions);
	window.addEventListener("popstate", ensureInstallActions);
})();
