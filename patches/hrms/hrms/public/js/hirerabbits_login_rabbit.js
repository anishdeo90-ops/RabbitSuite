// HireRabbits: 3D fur rabbit that peeks over the /login card and reacts to the form.
// Loaded on every web page via web_include_js; exits immediately anywhere but /login.
// ponytail: three.js comes from jsdelivr; vendor it into hrms/public if the suite must work offline.
(function () {
	if (!location.pathname.startsWith("/login")) return;
	if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;

	const THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.169.0/+esm";
	const ROOM_URL = "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/environments/RoomEnvironment.js/+esm";

	const css = `
		:root { --hr-rh: 320px; }
		@media (max-width: 480px) { :root { --hr-rh: 260px; } }
		/* rabbit floats up into the empty space above the card; only a small nudge down */
		section.for-login { position: relative; margin-top: 60px; }
		section.for-login .login-content {
			position: relative; z-index: 1; background: #fff; border: 1px solid #dfe2e7 !important; border-radius: 18px !important;
			box-shadow: 0 1px 2px rgba(20, 24, 33, .06), 0 18px 40px -12px rgba(20, 24, 33, .18); transition: opacity .5s ease, transform .5s ease;
		}
		section.for-login .login-content.hr-leave { opacity: 0; transform: translateY(16px) scale(.98); }
		#hr-rabbit {
			position: absolute; left: 50%; top: calc(var(--hr-rh) * -0.84); transform: translateX(-50%);
			width: var(--hr-rh); height: var(--hr-rh); max-width: 100vw; pointer-events: none; z-index: 0;
		}
		#freeze { background: transparent !important; }
	`;

	function start() {
		const section = document.querySelector("section.for-login");
		const card = section && section.querySelector(".login-content");
		const email = document.getElementById("login_email");
		const pwd = document.getElementById("login_password");
		if (!card || !email || !pwd || !window.login) return;

		const style = document.createElement("style");
		style.textContent = css;
		document.head.append(style);
		const canvas = document.createElement("canvas");
		canvas.id = "hr-rabbit";
		canvas.setAttribute("aria-hidden", "true");
		section.prepend(canvas);

		Promise.all([import(THREE_URL), import(ROOM_URL)])
			.then(([THREE, { RoomEnvironment }]) => run(THREE, RoomEnvironment, { section, card, email, pwd, canvas }))
			.catch((e) => {
				// never let the mascot break login
				console.warn("[hirerabbits] rabbit disabled:", e);
				canvas.remove();
				style.remove();
			});
	}

	function run(THREE, RoomEnvironment, { section, card, email, pwd, canvas }) {
		// ---------- renderer / scene ----------
		const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
		renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
		renderer.toneMapping = THREE.ACESFilmicToneMapping;
		renderer.toneMappingExposure = 1.05;
		const scene = new THREE.Scene();
		scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
		const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 50);
		camera.position.set(0, 1.9, 7.2);
		camera.lookAt(0, 1.85, 0);
		scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 1.1));
		const sun = new THREE.DirectionalLight(0xffffff, 2.2);
		sun.position.set(2.5, 4, 5);
		scene.add(sun);

		function resize() {
			const w = canvas.clientWidth, h = canvas.clientHeight;
			renderer.setSize(w, h, false);
			camera.aspect = w / h;
			camera.updateProjectionMatrix();
		}
		addEventListener("resize", resize);
		resize();

		// ---------- fur (shell texturing) ----------
		const SHELLS = 22;
		const shared = { uTime: { value: 0 }, uLightDir: { value: sun.position.clone().normalize() } };
		const furVert = `
			uniform float uLayer, uLen, uTime;
			varying vec3 vObj; varying vec3 vN; varying vec3 vView;
			void main() {
				vec3 n = normalize(mat3(modelMatrix) * normal);
				vec4 wp = modelMatrix * vec4(position, 1.0);
				float l = uLayer;
				wp.xyz += n * uLen * l;
				wp.y -= uLen * 0.35 * l * l;
				wp.xyz += vec3(sin(uTime * 2.0 + wp.y * 3.0), 0.0, cos(uTime * 1.7 + wp.x * 3.0)) * 0.004 * l * l;
				vObj = position; vN = n; vView = cameraPosition - wp.xyz;
				gl_Position = projectionMatrix * viewMatrix * wp;
			}`;
		const furFrag = `
			uniform float uLayer, uDensity; uniform vec3 uColor, uTip, uLightDir;
			varying vec3 vObj; varying vec3 vN; varying vec3 vView;
			float hash(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
			void main() {
				vec3 p = vObj * uDensity;
				vec3 f = fract(p) - 0.5;
				float h = hash(floor(p));
				if (uLayer > 0.0) {
					float r = 1.0 - uLayer / (0.35 + 0.65 * h);
					if (r <= 0.0 || length(f) > r * 0.62) discard;
				}
				vec3 N = normalize(vN), V = normalize(vView);
				float diff = clamp(dot(N, uLightDir) * 0.5 + 0.5, 0.0, 1.0);
				float ao = mix(0.38, 1.0, uLayer);
				vec3 col = mix(uColor, uTip, uLayer * uLayer) * (0.9 + 0.2 * h);
				float rim = pow(1.0 - max(dot(N, V), 0.0), 2.5);
				col = col * (0.35 + 0.85 * diff) * ao + rim * 0.22 * uTip;
				gl_FragColor = vec4(col, 1.0);
				#include <tonemapping_fragment>
				#include <colorspace_fragment>
			}`;

		const matCache = new Map();
		function furMat(spec, layer) {
			const key = spec.id + ":" + layer;
			if (!matCache.has(key)) {
				matCache.set(key, new THREE.ShaderMaterial({
					vertexShader: furVert, fragmentShader: furFrag,
					uniforms: {
						...shared, uLayer: { value: layer }, uLen: { value: spec.len }, uDensity: { value: spec.density },
						uColor: { value: new THREE.Color(spec.color) }, uTip: { value: new THREE.Color(spec.tip) },
					},
				}));
			}
			return matCache.get(key);
		}
		function fur(geo, spec) {
			const g = new THREE.Group();
			for (let i = 0; i < SHELLS; i++) {
				const m = new THREE.Mesh(geo, furMat(spec, i / (SHELLS - 1)));
				m.frustumCulled = false;
				g.add(m);
			}
			return g;
		}
		const ellipsoid = (r, sx, sy, sz, seg = 48) => new THREE.SphereGeometry(r, seg, seg * 0.75).scale(sx, sy, sz);

		const GREY = { id: "grey", color: "#6f6c6a", tip: "#c9c5c0", len: 0.075, density: 95 };
		const WHITE = { id: "white", color: "#cfccc7", tip: "#fbfaf8", len: 0.07, density: 95 };
		const PINKFUR = { id: "pink", color: "#c98a90", tip: "#f2c9cc", len: 0.02, density: 140 };

		// ---------- rabbit ----------
		const root = new THREE.Group();
		scene.add(root);
		const body = fur(ellipsoid(1, 0.95, 1.05, 0.85), GREY);
		root.add(body);
		const chest = fur(ellipsoid(0.62, 1, 1.2, 0.6), WHITE);
		chest.position.set(0, 0.2, 0.42);
		root.add(chest);

		const head = new THREE.Group();
		head.position.set(0, 0.85, 0.1);
		root.add(head);
		const skull = fur(ellipsoid(0.8, 1, 0.92, 0.95), GREY);
		skull.position.set(0, 0.6, 0.1);
		head.add(skull);
		for (const s of [-1, 1]) {
			const cheek = fur(ellipsoid(0.24, 1.1, 0.9, 1), WHITE);
			cheek.position.set(0.17 * s, 0.38, 0.62);
			head.add(cheek);
		}
		const nose = new THREE.Mesh(ellipsoid(0.07, 1.3, 0.9, 0.8, 24),
			new THREE.MeshPhysicalMaterial({ color: "#d98a94", roughness: 0.45, clearcoat: 0.4 }));
		nose.position.set(0, 0.52, 0.9);
		head.add(nose);

		const wPts = [];
		for (const s of [-1, 1]) for (const dy of [-0.08, 0, 0.08]) {
			wPts.push(new THREE.Vector3(0.22 * s, 0.42, 0.84), new THREE.Vector3(0.95 * s, 0.42 + dy * 2, 0.65));
		}
		head.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(wPts),
			new THREE.LineBasicMaterial({ color: "#f4f2ee", transparent: true, opacity: 0.75 })));

		const eyeMat = new THREE.MeshPhysicalMaterial({ color: "#1b1210", roughness: 0.04, clearcoat: 1, clearcoatRoughness: 0.02 });
		const lidGeo = new THREE.SphereGeometry(0.172, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);
		const eyes = [], lids = [];
		for (const s of [-1, 1]) {
			const eye = new THREE.Group();
			eye.position.set(0.44 * s, 0.72, 0.64);
			eye.rotation.y = 0.35 * s;
			eye.add(new THREE.Mesh(new THREE.SphereGeometry(0.16, 32, 24), eyeMat));
			const lid = fur(lidGeo, GREY);
			eye.add(lid);
			head.add(eye);
			eyes.push(eye); lids.push(lid);
		}

		const ears = [];
		for (const s of [-1, 1]) {
			const pivot = new THREE.Group();
			pivot.position.set(0.28 * s, 1.2, -0.05);
			const outer = fur(ellipsoid(1, 0.26, 0.8, 0.1).translate(0, 0.75, 0), GREY);
			const inner = fur(ellipsoid(1, 0.16, 0.6, 0.04).translate(0, 0.75, 0.075), PINKFUR);
			pivot.add(outer, inner);
			head.add(pivot);
			ears.push({ pivot, s });
		}

		const UP = new THREE.Vector3(0, 1, 0);
		const rest = (s) => new THREE.Vector3(0.38 * s, 0.45, 0.95);
		const arms = [-1, 1].map((s) => {
			const forearm = fur(ellipsoid(0.2, 1, 1.1, 1), GREY);
			const paw = fur(ellipsoid(0.2, 1.15, 0.95, 1.1), WHITE);
			root.add(forearm, paw);
			return { s, forearm, paw, shoulder: new THREE.Vector3(0.52 * s, 0.55, 0.45), cur: rest(s) };
		});
		function placeArm(arm) {
			const d = arm.cur.clone().sub(arm.shoulder);
			const len = d.length();
			arm.forearm.position.copy(arm.shoulder).addScaledVector(d, 0.5);
			arm.forearm.quaternion.setFromUnitVectors(UP, d.normalize());
			arm.forearm.scale.set(1, len / 0.44, 1);
			arm.paw.position.copy(arm.cur);
		}

		const carrot = new THREE.Group();
		const cone = new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.55, 24), new THREE.MeshPhysicalMaterial({ color: "#f07b1e", roughness: 0.5, clearcoat: 0.3 }));
		cone.rotation.z = Math.PI;
		carrot.add(cone);
		for (let i = 0; i < 3; i++) {
			const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.28, 8), new THREE.MeshStandardMaterial({ color: "#3f9b3a", roughness: 0.6 }));
			leaf.position.set((i - 1) * 0.05, 0.38, 0);
			leaf.rotation.z = (i - 1) * -0.4;
			carrot.add(leaf);
		}
		carrot.visible = false;
		scene.add(carrot);

		const drop = new THREE.Mesh(new THREE.SphereGeometry(0.07, 24, 16).scale(1, 1.4, 1),
			new THREE.MeshPhysicalMaterial({ color: "#a9dcff", roughness: 0, transmission: 0.6, thickness: 0.2, transparent: true }));
		drop.visible = false;
		head.add(drop);

		// ---------- state machine ----------
		const P = { yaw: 0, pitch: 0, roll: 0, ear: 0, splay: 0.18, lid: 0, y: 0 };
		let state = "enter", stateT = 0, caret = 0, t = 0, blinkAt = 2;
		const mouse = { x: 0, y: 0 };

		function targets() {
			const tg = { yaw: mouse.x * 0.5, pitch: mouse.y * 0.3, roll: 0, ear: 0, splay: 0.18, lid: 0, y: 0, paws: "rest" };
			switch (state) {
				case "enter": tg.y = -2.4 + Math.min(stateT / 0.9, 1) * 2.4; break;
				case "watch": Object.assign(tg, { yaw: -0.45 + caret * 0.9, pitch: 0.38, ear: 0.12, roll: (caret - 0.5) * -0.12 }); break;
				case "hide": Object.assign(tg, { yaw: 0, pitch: 0.12, ear: -1.25, splay: 0.35, paws: "eyes" }); break;
				case "peek": Object.assign(tg, { yaw: 0.12, pitch: 0.25, ear: -0.7, splay: 0.3, paws: "peek", roll: 0.08 }); break;
				case "verify": Object.assign(tg, { yaw: 0.15, pitch: -0.25, ear: 0.15, splay: 0.08, lid: 0.15 }); break;
				case "fail": Object.assign(tg, { yaw: 0, pitch: 0.3, ear: -0.35, splay: 1.15, lid: 0.4 }); break;
				case "success": Object.assign(tg, { yaw: 0, pitch: -0.15, ear: 0.1, splay: 0.02, lid: 0.72, paws: "wave" }); break;
			}
			return tg;
		}
		function setState(s) {
			state = s; stateT = 0;
			if (s === "fail") drop.visible = true;
			if (s === "success") carrot.visible = true;
		}
		function restState() {
			const a = document.activeElement;
			if (a === pwd) return pwd.type === "text" ? "peek" : "hide";
			if (a === email) return "watch";
			return "idle";
		}
		const busy = () => ["enter", "verify", "fail", "success"].includes(state);

		const damp = (a, b, k, dt) => a + (b - a) * (1 - Math.exp(-k * dt));
		const tmp = new THREE.Vector3();
		function eyeTarget(i, off) {
			eyes[i].getWorldPosition(tmp);
			root.worldToLocal(tmp);
			return tmp.add(off).clone();
		}

		function step(dt) {
			t += dt; stateT += dt;
			shared.uTime.value = t;
			const tg = targets();

			for (const k of ["yaw", "pitch", "roll", "ear", "splay", "lid"]) P[k] = damp(P[k], tg[k], state === "fail" ? 7 : 9, dt);
			P.y = state === "enter" ? tg.y : damp(P.y, tg.y, 10, dt);

			let yaw = P.yaw, y = P.y, earFlick = 0;
			y += Math.sin(t * 1.6) * 0.012;
			body.scale.setScalar(1 + Math.sin(t * 1.6) * 0.012);
			if (state === "enter" && stateT > 0.9) setState(restState());
			if (state === "fail") {
				const env = Math.max(0, 1 - stateT / 1.1);
				yaw += Math.sin(stateT * 22) * 0.32 * env;
				drop.position.set(0.62, 1.05 - Math.min(stateT, 1.2) * 0.35, 0.35);
				drop.material.opacity = Math.max(0, 1 - stateT / 1.5);
				if (stateT > 1.6) { drop.visible = false; setState(restState()); }
			}
			if (state === "verify") {
				y += Math.abs(Math.sin(t * 7)) * 0.06;
				earFlick = Math.sin(t * 14) * 0.08;
			}
			if (state === "success") {
				y += stateT < 0.6 ? Math.sin(Math.PI * stateT / 0.6) * 0.5 : 0;
				const e = 1 - Math.pow(1 - Math.min(stateT / 0.9, 1), 3);
				carrot.position.set(0.85 * e, 2.6 + 1.1 * e + (stateT > 0.9 ? Math.sin(t * 3) * 0.05 : 0), 0.6);
				carrot.rotation.set(0, t * 3, 0.5);
				carrot.scale.setScalar(Math.min(stateT / 0.35, 1));
			}
			if (state === "idle" && Math.sin(t * 0.9) > 0.995) earFlick = 0.25;

			let blink = 0;
			if (t > blinkAt) {
				blink = Math.sin(Math.min((t - blinkAt) / 0.16, 1) * Math.PI);
				if (t - blinkAt > 0.16) blinkAt = t + 2.2 + Math.random() * 3.5;
			}
			const lid = Math.max(P.lid, blink);

			root.position.y = y;
			head.rotation.set(P.pitch, yaw, P.roll);
			ears.forEach(({ pivot, s }, i) => {
				const fold = P.ear + (i === 1 ? earFlick : 0) + (state === "peek" && i === 1 ? 0.6 : 0);
				pivot.rotation.set(-fold, 0, -s * P.splay);
			});
			lids.forEach((l) => (l.rotation.x = THREE.MathUtils.lerp(-0.95, Math.PI / 2, lid)));

			root.updateMatrixWorld(true);
			arms.forEach((arm, i) => {
				let goal = rest(arm.s);
				if (tg.paws === "eyes") goal = eyeTarget(i, new THREE.Vector3(0.02 * arm.s, -0.03, 0.26));
				if (tg.paws === "peek") goal = i === 0 ? eyeTarget(0, new THREE.Vector3(0, -0.03, 0.26)) : eyeTarget(1, new THREE.Vector3(0.12, -0.42, 0.22));
				if (tg.paws === "wave" && i === 1) goal = new THREE.Vector3(1.05 + Math.sin(t * 12) * 0.12, 1.55, 0.6);
				arm.cur.lerp(goal, 1 - Math.exp(-(state === "enter" ? 30 : 11) * dt));
				placeArm(arm);
			});
		}

		const clock = new THREE.Clock();
		(function frame() {
			step(Math.min(clock.getDelta(), 0.05));
			if (section.offsetParent) renderer.render(scene, camera); // skip while forgot/signup is showing
			requestAnimationFrame(frame);
		})();

		// ---------- form wiring ----------
		addEventListener("mousemove", (e) => {
			const r = canvas.getBoundingClientRect();
			mouse.x = THREE.MathUtils.clamp((e.clientX - (r.left + r.width / 2)) / (innerWidth / 2), -1, 1);
			mouse.y = THREE.MathUtils.clamp((e.clientY - (r.top + r.height * 0.45)) / (innerHeight / 2), -1, 1);
		});
		const updateCaret = () => { caret = Math.min((email.selectionStart ?? email.value.length) / 26, 1); };
		email.addEventListener("focus", () => { updateCaret(); if (!busy()) setState("watch"); });
		for (const ev of ["input", "keyup", "click"]) email.addEventListener(ev, updateCaret);
		pwd.addEventListener("focus", () => { if (!busy()) setState(pwd.type === "text" ? "peek" : "hide"); });
		for (const el of [email, pwd]) {
			el.addEventListener("blur", () => setTimeout(() => { if (!busy() && !card.contains(document.activeElement)) setState("idle"); }, 0));
		}
		const toggle = section.querySelector(".toggle-password");
		if (toggle) {
			toggle.addEventListener("mousedown", (e) => e.preventDefault()); // keep focus in the password field
			// frappe's own click handler flips the input type; read it after that runs
			toggle.addEventListener("click", () => setTimeout(() => { if (!busy()) setState(pwd.type === "text" ? "peek" : "hide"); }, 0));
		}

		// ---------- hook into frappe's login.js ----------
		const L = window.login;
		const loginVisible = () => !!section.offsetParent;
		const origCall = L.call;
		L.call = function () {
			if (loginVisible()) setState("verify");
			const req = origCall.apply(this, arguments);
			// 500s / network errors skip set_invalid; don't leave the rabbit thinking forever
			req?.always?.(() => { if (state === "verify") setState(restState()); });
			return req;
		};
		const origInvalid = L.set_invalid;
		L.set_invalid = function () {
			if (loginVisible()) setState("fail");
			return origInvalid.apply(this, arguments);
		};
		const handlers = L.login_handlers;
		const orig200 = handlers[200];
		handlers[200] = function (data) {
			if (data && data.message === "Logged In" && loginVisible()) {
				setState("success");
				setTimeout(() => card.classList.add("hr-leave"), 900);
				setTimeout(() => orig200.call(this, data), 1300);
				return;
			}
			if (state === "verify") setState(restState());
			return orig200.apply(this, arguments);
		};
	}

	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
	else start();
})();
