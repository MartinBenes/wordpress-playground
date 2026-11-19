// Load only after the parser has finished reading the inert document.
(() => {
  const { playgroundEntry: role, base } = document.body.dataset;
  const marker = Symbol.for("wordpress-playground.trusted-entry");
  const panel = document.querySelector("main");

  function approvedWindow(candidate) {
    // Access to a cross-origin or opaque ancestor throws. Fail closed.
    try {
      return candidate.location.origin === location.origin &&
        candidate[marker]?.base === base && candidate.location.pathname.startsWith(base);
    } catch {
      return false;
    }
  }

  function approvedAncestors() {
    let child = window;
    let block = role === "block";
    let awaitingWordPress = false;
    try {
      while (child.parent !== child) {
        child = child.parent;
        if (approvedWindow(child)) {
          if (awaitingWordPress) return false;
          block ||= child[marker].role === "block";
          continue;
        }
        // The code block may sit inside Gutenberg's same-origin editor canvas.
        if (block && /^about:(?:srcdoc|blank)$/.test(child.location.href)) {
          awaitingWordPress = true;
          continue;
        }
        if (block && child.location.origin === location.origin &&
            child.location.pathname.startsWith(base + "scope:") &&
            child.frameElement?.id === "wp" && approvedWindow(child.parent) &&
            child.parent[marker].role === "frame") {
          awaitingWordPress = false;
          continue;
        }
        return false;
      }
      return !awaitingWordPress;
    } catch {
      return false;
    }
  }

  const safeOptions = {
    "site-slug": /^[a-z0-9_-]{1,160}$/i,
    language: /^[a-z]{2,3}(?:_[A-Z]{2})?(?:_[a-z]{2,15})?$/,
    php: /^(?:5\.2|7\.4|8\.[0-5]|latest)$/,
    wp: /^(?:6\.[3-9]|7\.[01]|latest)$/,
    storage: /^(?:temp|browser)$/,
    mode: /^(?:browser-full-screen|seamless)$/,
    "can-save": /^(?:yes|no)$/,
    login: /^(?:yes|no)$/,
    networking: /^(?:yes|no)$/,
    multisite: /^(?:yes|no)$/,
    url: /^(?:\/|\/wp-admin(?:\/?|\/(?:index|edit|post-new|upload|themes|plugins|site-editor)\.php(?:\?post_type=(?:page|post))?))$/,
  };

  function plainSetup(url) {
    if (url.hash) return false;
    const starterBlueprint = new URL(base + "platno/blueprint.json", location.origin).href;
    for (const [key, value] of url.searchParams) {
      if (key === "blueprint-url" && value === starterBlueprint) continue;
      if (!Object.hasOwn(safeOptions, key) || !safeOptions[key].test(value)) return false;
    }
    return true;
  }

  function show(message) {
    panel.querySelector("p").textContent = message;
    panel.hidden = false;
  }

  function loadApp() {
    const raw = atob(document.getElementById("original-entry").textContent);
    const source = new TextDecoder().decode(Uint8Array.from(raw, c => c.charCodeAt(0)));
    document.open();
    window[marker] = { base, role };
    if (role === "page" && window === window.top) {
      // The upstream router records in-app site selection, Blueprint edits and
      // related navigation with pushState/replaceState. Preserve its own handlers
      // for routes the running app has created, including browser back/forward.
      const routes = new Set([location.href]);
      for (const method of ["pushState", "replaceState"]) {
        const original = history[method];
        history[method] = function (...args) {
          const result = original.apply(this, args);
          routes.add(location.href);
          return result;
        };
      }
      for (const eventName of ["hashchange", "popstate"]) {
        window.addEventListener(eventName, event => {
          if (routes.has(location.href) || plainSetup(new URL(location.href))) return;
          event.stopImmediatePropagation();
          location.reload();
        }, { capture: true });
      }
    }
    document.write(source);
    document.close();
  }

  const embedded = window !== window.top;
  if (!approvedAncestors() || (["frame", "block"].includes(role) && !embedded) ||
      (role === "popup" && !approvedWindow(window.opener))) {
    show("Otevři Playground v samostatné kartě.");
    return;
  }
  if (!embedded && window.opener && !approvedWindow(window.opener)) {
    window.opener = null;
  }
  if (!embedded && role === "page" && !plainSetup(new URL(location.href))) {
    show("Tento odkaz předává Playgroundu nastavení, které může obsahovat kód. Spusť ho, jen pokud znáš jeho původ.");
    const button = panel.querySelector("button");
    button.hidden = false;
    button.addEventListener("click", event => {
      if (event.isTrusted) loadApp();
    });
    return;
  }
  loadApp();
})();
