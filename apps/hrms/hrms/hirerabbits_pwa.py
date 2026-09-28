def allow_pwa_service_worker_scope(response, request):
	path = request.path or ""
	if path in {
		"/assets/crm/frontend/sw.js",
		"/assets/helpdesk/desk/sw.js",
		"/assets/hrms/frontend/sw.js",
	}:
		response.headers["Service-Worker-Allowed"] = "/"
