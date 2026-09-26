// HireRabbits: greeting, tile colours and a corner rabbit on the /desk home (frappe's Desktop page).
// Frappe rebuilds that page on every visit, so a MutationObserver re-applies the greeting + colours.
// Styles live in hirerabbits_desk_home.css.
(function () {
	const COLORS = {
		support: "#7c3aed", helpdesk: "#7c3aed", hrms: "#10b981", crm: "#e11de0",
		admin: "#6b7280", erp: "#0a84ff", erpnext: "#0a84ff",
	};

	function greeting() {
		const h = new Date().getHours();
		return h < 12 ? __("Good morning") : h < 17 ? __("Good afternoon") : __("Good evening");
	}

	function decorate() {
		const wrapper = document.querySelector(".desktop-wrapper");
		if (!wrapper) return;
		const container = wrapper.querySelector(".desktop-container");
		if (container && !wrapper.querySelector(".hr-hello")) {
			const name = (frappe.session.user_fullname || frappe.session.user || "").split(" ")[0];
			const hello = document.createElement("div");
			hello.className = "hr-hello";
			hello.innerHTML = "<h1></h1><p></p>";
			hello.querySelector("h1").textContent = `${greeting()}, ${name} 👋`;
			hello.querySelector("p").textContent =
				new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
			container.before(hello);
		}
		wrapper.querySelectorAll(".desktop-container .desktop-icon:not([data-hr])").forEach((el) => {
			el.dataset.hr = "1";
			const c = COLORS[(el.dataset.id || "").toLowerCase()];
			if (c) el.style.setProperty("--c", c);
		});
	}

	let queued = false;
	new MutationObserver(() => {
		if (queued) return;
		queued = true;
		requestAnimationFrame(() => { queued = false; decorate(); });
	}).observe(document.body, { childList: true, subtree: true });
	decorate();

	if (!matchMedia("(prefers-reduced-motion: reduce)").matches) {
		Promise.all([
			import("https://cdn.jsdelivr.net/npm/three@0.169.0/+esm"),
			import("https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/environments/RoomEnvironment.js/+esm"),
		])
			.then(([THREE, { RoomEnvironment }]) => bunny(THREE, RoomEnvironment))
			.catch((e) => console.warn("[hirerabbits] desk rabbit disabled:", e));
	}

	// ponytail: fur builder duplicated from hirerabbits_login_rabbit.js (login loads as a web page, desk as an app page);
	// pull into one shared module if a third rabbit shows up.
	function bunny(THREE, RoomEnvironment) {
		const canvas = document.createElement("canvas");
		canvas.id = "hr-bunny";
		canvas.setAttribute("aria-hidden", "true");
		document.body.append(canvas);

		const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
		renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
		renderer.toneMapping = THREE.ACESFilmicToneMapping;
		const scene = new THREE.Scene();
		scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
		const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 50);
		camera.position.set(0, 1.9, 7.2);
		camera.lookAt(0, 1.85, 0);
		scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 1.1));
		const sun = new THREE.DirectionalLight(0xffffff, 2.2);
		sun.position.set(2.5, 4, 5);
		scene.add(sun);

		const SHELLS = 20;
		const shared = { uTime: { value: 0 }, uLightDir: { value: sun.position.clone().normalize() } };
		const vert = `uniform float uLayer, uLen, uTime; varying vec3 vObj; varying vec3 vN; varying vec3 vView;
			void main() { vec3 n = normalize(mat3(modelMatrix) * normal); vec4 wp = modelMatrix * vec4(position, 1.0); float l = uLayer;
			wp.xyz += n * uLen * l; wp.y -= uLen * 0.35 * l * l;
			wp.xyz += vec3(sin(uTime * 2.0 + wp.y * 3.0), 0.0, cos(uTime * 1.7 + wp.x * 3.0)) * 0.004 * l * l;
			vObj = position; vN = n; vView = cameraPosition - wp.xyz; gl_Position = projectionMatrix * viewMatrix * wp; }`;
		const frag = `uniform float uLayer, uDensity; uniform vec3 uColor, uTip, uLightDir; varying vec3 vObj; varying vec3 vN; varying vec3 vView;
			float hash(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
			void main() { vec3 p = vObj * uDensity; vec3 f = fract(p) - 0.5; float h = hash(floor(p));
			if (uLayer > 0.0) { float r = 1.0 - uLayer / (0.35 + 0.65 * h); if (r <= 0.0 || length(f) > r * 0.62) discard; }
			vec3 N = normalize(vN), V = normalize(vView); float diff = clamp(dot(N, uLightDir) * 0.5 + 0.5, 0.0, 1.0);
			vec3 col = mix(uColor, uTip, uLayer * uLayer) * (0.9 + 0.2 * h); float rim = pow(1.0 - max(dot(N, V), 0.0), 2.5);
			col = col * (0.35 + 0.85 * diff) * mix(0.38, 1.0, uLayer) + rim * 0.22 * uTip;
			gl_FragColor = vec4(col, 1.0);
			#include <tonemapping_fragment>
			#include <colorspace_fragment>
			}`;
		const cache = new Map();
		const furMat = (s, l) => {
			const k = s.id + l;
			if (!cache.has(k)) cache.set(k, new THREE.ShaderMaterial({ vertexShader: vert, fragmentShader: frag, uniforms: { ...shared,
				uLayer: { value: l }, uLen: { value: s.len }, uDensity: { value: s.density },
				uColor: { value: new THREE.Color(s.color) }, uTip: { value: new THREE.Color(s.tip) } } }));
			return cache.get(k);
		};
		const fur = (geo, s) => {
			const g = new THREE.Group();
			for (let i = 0; i < SHELLS; i++) {
				const m = new THREE.Mesh(geo, furMat(s, i / (SHELLS - 1)));
				m.frustumCulled = false;
				g.add(m);
			}
			return g;
		};
		const ell = (r, x, y, z, seg = 40) => new THREE.SphereGeometry(r, seg, seg * 0.75).scale(x, y, z);
		const GREY = { id: "g", color: "#6f6c6a", tip: "#c9c5c0", len: 0.075, density: 95 };
		const WHITE = { id: "w", color: "#cfccc7", tip: "#fbfaf8", len: 0.07, density: 95 };
		const PINK = { id: "p", color: "#c98a90", tip: "#f2c9cc", len: 0.02, density: 140 };

		const root = new THREE.Group();
		scene.add(root);
		root.add(fur(ell(1, 0.95, 1.05, 0.85), GREY));
		const chest = fur(ell(0.62, 1, 1.2, 0.6), WHITE);
		chest.position.set(0, 0.2, 0.42);
		root.add(chest);
		const head = new THREE.Group();
		head.position.set(0, 0.85, 0.1);
		root.add(head);
		const skull = fur(ell(0.8, 1, 0.92, 0.95), GREY);
		skull.position.set(0, 0.6, 0.1);
		head.add(skull);
		for (const s of [-1, 1]) {
			const c = fur(ell(0.24, 1.1, 0.9, 1), WHITE);
			c.position.set(0.17 * s, 0.38, 0.62);
			head.add(c);
		}
		const nose = new THREE.Mesh(ell(0.07, 1.3, 0.9, 0.8, 24), new THREE.MeshPhysicalMaterial({ color: "#d98a94", roughness: 0.45, clearcoat: 0.4 }));
		nose.position.set(0, 0.52, 0.9);
		head.add(nose);
		const eyeMat = new THREE.MeshPhysicalMaterial({ color: "#1b1210", roughness: 0.04, clearcoat: 1 });
		const lidGeo = new THREE.SphereGeometry(0.172, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);
		const lids = [];
		for (const s of [-1, 1]) {
			const eye = new THREE.Group();
			eye.position.set(0.44 * s, 0.72, 0.64);
			eye.rotation.y = 0.35 * s;
			eye.add(new THREE.Mesh(new THREE.SphereGeometry(0.16, 32, 24), eyeMat));
			const lid = fur(lidGeo, GREY);
			eye.add(lid);
			head.add(eye);
			lids.push(lid);
		}
		const ears = [-1, 1].map((s) => {
			const p = new THREE.Group();
			p.position.set(0.28 * s, 1.2, -0.05);
			p.add(fur(ell(1, 0.26, 0.8, 0.1).translate(0, 0.75, 0), GREY), fur(ell(1, 0.16, 0.6, 0.04).translate(0, 0.75, 0.075), PINK));
			head.add(p);
			return { p, s };
		});
		for (const s of [-1, 1]) {
			const paw = fur(ell(0.2, 1.15, 0.95, 1.1), WHITE);
			paw.position.set(0.38 * s, 0.45, 0.95);
			root.add(paw);
		}

		// follow the mouse, perk up over an app tile, hop when one is clicked
		const mouse = { x: -0.6, y: -0.4 };
		let excited = false, hopT = -1, t = 0, blinkAt = 2, enterT = 0, wasOn = false;
		const P = { yaw: 0, pitch: 0, ear: 0, splay: 0.18 };
		const TILE = ".desktop-container .desktop-icon";
		addEventListener("mousemove", (e) => {
			const r = canvas.getBoundingClientRect();
			mouse.x = THREE.MathUtils.clamp((e.clientX - (r.left + r.width / 2)) / (innerWidth / 2), -1, 1);
			mouse.y = THREE.MathUtils.clamp((e.clientY - (r.top + r.height * 0.4)) / (innerHeight / 2), -1, 1);
			excited = !!e.target.closest?.(TILE);
		});
		document.addEventListener("click", (e) => { if (e.target.closest?.(TILE)) hopT = 0; }, true);

		const damp = (a, b, k, dt) => a + (b - a) * (1 - Math.exp(-k * dt));
		const clock = new THREE.Clock();
		(function frame() {
			requestAnimationFrame(frame);
			const dt = Math.min(clock.getDelta(), 0.05);
			const on = !!document.querySelector(".desktop-wrapper")?.offsetParent;
			if (on !== wasOn) {
				canvas.style.display = on ? "block" : "none";
				if (on) {
					renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
					enterT = 0;
				}
				wasOn = on;
			}
			if (!on) return;
			t += dt; enterT += dt; shared.uTime.value = t;
			const tg = { yaw: mouse.x * 0.7, pitch: mouse.y * 0.35, ear: excited ? 0.15 : 0, splay: excited ? 0.04 : 0.2 };
			for (const k in P) P[k] = damp(P[k], tg[k], 8, dt);
			let y = -2.4 + Math.min(Math.max(enterT - 0.8, 0) / 0.8, 1) * 2.4; // pops up after the tiles land
			y += Math.sin(t * 1.6) * 0.012;
			if (hopT >= 0) {
				hopT += dt;
				y += hopT < 0.5 ? Math.sin((Math.PI * hopT) / 0.5) * 0.45 : 0;
				if (hopT > 0.5) hopT = -1;
			}
			let blink = 0;
			if (t > blinkAt) {
				blink = Math.sin(Math.min((t - blinkAt) / 0.16, 1) * Math.PI);
				if (t - blinkAt > 0.16) blinkAt = t + 2 + Math.random() * 3.5;
			}
			root.position.y = y;
			head.rotation.set(P.pitch, P.yaw, 0);
			const twitch = Math.sin(t * 0.9) > 0.995 ? 0.25 : 0;
			ears.forEach(({ p, s }, i) => p.rotation.set(-(P.ear + (i ? twitch : 0)), 0, -s * P.splay));
			lids.forEach((l) => (l.rotation.x = THREE.MathUtils.lerp(-0.95, Math.PI / 2, blink)));
			renderer.render(scene, camera);
		})();
	}
})();
