import { createResource } from "frappe-ui";
import { computed, h, markRaw, type Component, type ComputedRef } from "vue";
import AppsIcon from "@/components/icons/AppsIcon.vue";
import { isCustomerPortal } from "@/utils";

export interface App {
  name: string;
  logo: string;
  title: string;
  route: string;
}

const appOverrides: Record<string, Partial<App>> = {
  erpnext: { title: "ERP", route: "/desk" },
  hrms: { title: "HRMS", route: "/desk/people" },
  crm: { title: "CRM", route: "/crm" },
  helpdesk: { title: "Support", route: "/helpdesk" },
};

const hiddenApps = new Set(["frappe", "helpdesk", "india_payroll", "telephony"]);

interface AppsMenuOption {
  label: string;
  icon: Component;
  submenu: Array<{ label: string; icon: unknown; onClick: () => void }>;
}

/**
 * Fetches the suite apps the user can switch to (ERP, HRMS, CRM, ...) and
 * exposes them as a native Dropdown submenu option that opens on hover.
 *
 * Mirrors the apps switcher in frappe/builder (`DashboardSidebar.vue`): plain
 * `label`/`icon`/`onClick` items so reka's submenu hover-intent works cleanly.
 */
export function useApps() {
  const resource = createResource({
    url: "frappe.apps.get_apps",
    cache: "apps",
    // customers lack permission for get_apps (403); sidebar remounts on portal
    // switch, so this re-evaluates for agents
    auto: !isCustomerPortal.value,
    transform: (data: App[]) => {
      return data
        .filter((app) => !hiddenApps.has(app.name) && app.route)
        .map((app) => ({ ...app, ...appOverrides[app.name] }));
    },
  });

  const apps = computed<App[]>(() => resource.data ?? []);

  const appsMenuOption: ComputedRef<AppsMenuOption> = computed(() => ({
    label: "Apps",
    icon: markRaw(AppsIcon),
    submenu: apps.value.map((app) => ({
      label: app.title,
      icon: h("img", { src: app.logo }),
      onClick: () => window.open(app.route, "_self"),
    })),
  }));

  return { apps, appsMenuOption };
}
