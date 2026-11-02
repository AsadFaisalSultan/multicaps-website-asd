/* Multicaps site scripts (no dependencies) */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector(".menu-toggle");
  if (toggle) {
    var navPanel = document.getElementById("site-nav");
    var siteHeader = document.querySelector(".site-header");
    toggle.addEventListener("click", function () {
      // Start the panel directly below the header (the top bar may still be in view)
      if (navPanel && siteHeader) navPanel.style.top = siteHeader.getBoundingClientRect().bottom + "px";
      var open = document.body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    if (navPanel) {
      navPanel.addEventListener("click", function (e) {
        if (e.target.closest("a")) {
          document.body.classList.remove("menu-open");
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    }
    window.matchMedia("(min-width: 981px)").addEventListener("change", function (e) {
      if (e.matches) {
        document.body.classList.remove("menu-open");
        toggle.setAttribute("aria-expanded", "false");
        if (navPanel) navPanel.style.top = "";
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("menu-open")) {
        document.body.classList.remove("menu-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* ---------- Header shadow once page scrolls (sentinel, no scroll listener) ---------- */
  var header = document.querySelector(".site-header");
  if (header && "IntersectionObserver" in window) {
    var sentinel = document.createElement("div");
    sentinel.style.cssText = "position:absolute;top:0;left:0;width:1px;height:80px;pointer-events:none;";
    document.body.prepend(sentinel);
    new IntersectionObserver(function (entries) {
      header.classList.toggle("is-scrolled", !entries[0].isIntersecting);
    }).observe(sentinel);
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reveals.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Animated counters ---------- */
  var counters = document.querySelectorAll("[data-count]");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (counters.length && "IntersectionObserver" in window && !reduceMotion) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = parseFloat(el.getAttribute("data-count"));
        var decimals = (el.getAttribute("data-count").split(".")[1] || "").length;
        var start = null;
        var duration = 1400;
        function tick(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / duration, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = (target * eased).toFixed(decimals);
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        cio.unobserve(el);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---------- Capsule size chart ---------- */
  var sizeChart = document.querySelector("[data-size-chart]");
  if (sizeChart) {
    var items = sizeChart.querySelectorAll(".size-item");
    var out = {
      size: document.querySelector("[data-size-out='size']"),
      volume: document.querySelector("[data-size-out='volume']"),
      length: document.querySelector("[data-size-out='length']"),
      weight: document.querySelector("[data-size-out='weight']")
    };
    function select(item) {
      items.forEach(function (i) { i.classList.remove("is-active"); i.setAttribute("aria-pressed", "false"); });
      item.classList.add("is-active");
      item.setAttribute("aria-pressed", "true");
      Object.keys(out).forEach(function (k) {
        if (out[k]) out[k].textContent = item.getAttribute("data-" + k);
      });
    }
    items.forEach(function (item) {
      item.addEventListener("mouseenter", function () { select(item); });
      item.addEventListener("focus", function () { select(item); });
      item.addEventListener("click", function () { select(item); });
    });
  }

  /* ---------- Production flow stage viewer ---------- */
  document.querySelectorAll("[data-flow]").forEach(function (flow) {
    var tabs = Array.prototype.slice.call(flow.querySelectorAll(".flow__tab"));
    var panels = flow.querySelectorAll(".flow__panel");
    var bar = flow.querySelector(".flow__progress span");
    var prev = flow.querySelector("[data-flow-prev]");
    var next = flow.querySelector("[data-flow-next]");
    var tabList = flow.querySelector(".flow__tabs");
    var current = 0;

    function go(i, focus) {
      current = Math.max(0, Math.min(tabs.length - 1, i));
      tabs.forEach(function (t, n) {
        var on = n === current;
        t.classList.toggle("is-active", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        panels[n].classList.toggle("is-active", on);
      });
      if (bar) bar.style.width = ((current + 1) / tabs.length * 100) + "%";
      if (prev) prev.disabled = current === 0;
      if (next) next.disabled = current === tabs.length - 1;
      // Keep the active chip in view on mobile without scrolling the page
      var t = tabs[current];
      if (tabList.scrollWidth > tabList.clientWidth) {
        var target = Math.max(0, Math.min(t.offsetLeft - tabList.clientWidth / 2 + t.offsetWidth / 2, tabList.scrollWidth - tabList.clientWidth));
        tabList.scrollTo({ left: target, behavior: reduceMotion ? "auto" : "smooth" });
        // Fallback for browsers that drop the smooth scroll (e.g. while snapping)
        setTimeout(function () {
          if (Math.abs(tabList.scrollLeft - target) > 30) tabList.scrollLeft = target;
        }, 450);
      }
      if (focus) t.focus();
    }

    tabs.forEach(function (t, n) {
      t.addEventListener("click", function () { go(n); });
      t.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown" || e.key === "ArrowRight") { e.preventDefault(); go(current + 1, true); }
        if (e.key === "ArrowUp" || e.key === "ArrowLeft") { e.preventDefault(); go(current - 1, true); }
        if (e.key === "Home") { e.preventDefault(); go(0, true); }
        if (e.key === "End") { e.preventDefault(); go(tabs.length - 1, true); }
      });
    });
    if (prev) prev.addEventListener("click", function () { go(current - 1); });
    if (next) next.addEventListener("click", function () { go(current + 1); });

    // Load all stage photos once the viewer approaches the viewport
    if ("IntersectionObserver" in window) {
      var fio = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        flow.querySelectorAll("img[loading='lazy']").forEach(function (img) { img.loading = "eager"; });
        fio.disconnect();
      }, { rootMargin: "400px 0px" });
      fio.observe(flow);
    }
    go(0);
  });

  /* ---------- Conditional form fields ---------- */
  document.querySelectorAll("[data-reveal-name]").forEach(function (block) {
    var form = block.closest("form");
    var name = block.getAttribute("data-reveal-name");
    var value = block.getAttribute("data-reveal-value");
    function sync() {
      var checked = form.querySelector('input[name="' + name + '"]:checked');
      var show = !!checked && checked.value === value;
      block.hidden = !show;
      block.querySelectorAll("input, select, textarea").forEach(function (f) { f.disabled = !show; });
    }
    form.querySelectorAll('input[name="' + name + '"]').forEach(function (r) { r.addEventListener("change", sync); });
    sync();
  });

  /* ---------- Lightbox ---------- */
  var galleries = document.querySelectorAll("[data-gallery]");
  if (galleries.length) {
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Image viewer");
    box.innerHTML =
      '<img alt="">' +
      '<button class="lightbox__close" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18"/></svg></button>' +
      '<button class="lightbox__prev" aria-label="Previous image"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 5l-7 7 7 7"/></svg></button>' +
      '<button class="lightbox__next" aria-label="Next image"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5l7 7-7 7"/></svg></button>' +
      '<div class="lightbox__count"></div>';
    document.body.appendChild(box);
    var img = box.querySelector("img");
    var count = box.querySelector(".lightbox__count");
    var set = [], index = 0, lastFocus = null;

    function show(i) {
      index = (i + set.length) % set.length;
      img.src = set[index].href;
      img.alt = set[index].querySelector("img").alt;
      count.textContent = (index + 1) + " / " + set.length;
    }
    function close() {
      box.classList.remove("is-open");
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    }
    galleries.forEach(function (g) {
      var links = Array.prototype.slice.call(g.querySelectorAll("a"));
      links.forEach(function (a, i) {
        a.addEventListener("click", function (e) {
          e.preventDefault();
          set = links; lastFocus = a;
          show(i);
          box.classList.add("is-open");
          document.body.style.overflow = "hidden";
          box.querySelector(".lightbox__close").focus();
        });
      });
    });
    box.querySelector(".lightbox__close").addEventListener("click", close);
    box.querySelector(".lightbox__prev").addEventListener("click", function () { show(index - 1); });
    box.querySelector(".lightbox__next").addEventListener("click", function () { show(index + 1); });
    box.addEventListener("click", function (e) { if (e.target === box) close(); });
    document.addEventListener("keydown", function (e) {
      if (!box.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(index - 1);
      if (e.key === "ArrowRight") show(index + 1);
    });
  }

  /* ---------- Click-to-load video ---------- */
  document.querySelectorAll("[data-video]").forEach(function (wrap) {
    var btn = wrap.querySelector("button");
    btn.addEventListener("click", function () {
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube-nocookie.com/embed/" + wrap.getAttribute("data-video") + "?autoplay=1&rel=0";
      iframe.title = btn.getAttribute("aria-label") || "Video";
      iframe.allow = "autoplay; encrypted-media; picture-in-picture";
      iframe.allowFullscreen = true;
      wrap.innerHTML = "";
      wrap.appendChild(iframe);
    });
  });

  /* ---------- Blog filter ---------- */
  var filters = document.querySelector("[data-blog-filters]");
  if (filters) {
    var cards = document.querySelectorAll("[data-blog-list] [data-category]");
    filters.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;
      filters.querySelectorAll("button").forEach(function (b) {
        b.classList.toggle("is-active", b === btn);
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      var cat = btn.getAttribute("data-filter");
      cards.forEach(function (c) {
        c.hidden = cat !== "all" && c.getAttribute("data-category") !== cat;
      });
    });
  }

  /* ---------- Article table of contents ---------- */
  var toc = document.querySelector("[data-toc]");
  var prose = document.querySelector(".prose");
  if (toc && prose) {
    var headings = prose.querySelectorAll("h2");
    if (headings.length < 2) {
      toc.closest(".toc-card").remove();
    } else {
      headings.forEach(function (h, i) {
        if (!h.id) h.id = "section-" + (i + 1);
        var a = document.createElement("a");
        a.href = "#" + h.id;
        a.textContent = h.textContent;
        toc.appendChild(a);
      });
      if ("IntersectionObserver" in window) {
        var links = toc.querySelectorAll("a");
        var tio = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              links.forEach(function (l) { l.classList.toggle("is-active", l.getAttribute("href") === "#" + entry.target.id); });
            }
          });
        }, { rootMargin: "0px 0px -70% 0px" });
        headings.forEach(function (h) { tio.observe(h); });
      }
    }
  }

  /* ---------- Forms ----------
     Each form posts to the URL in data-endpoint (e.g. a Formspree / Getform / own API URL).
     If no endpoint is set, it falls back to opening the visitor's email client
     with the details pre-filled, addressed to data-mailto. */
  document.querySelectorAll("form[data-form]").forEach(function (form) {
    var status = form.querySelector(".form-status");

    function setError(field, msg) {
      var wrap = field.closest(".field");
      if (!wrap) return;
      wrap.classList.toggle("has-error", !!msg);
      var err = wrap.querySelector(".field__error");
      if (err && msg) err.textContent = msg;
    }

    function validate() {
      var ok = true, first = null;
      var seenGroups = {};
      form.querySelectorAll("input, select, textarea").forEach(function (f) {
        if (f.type === "hidden" || f.name === "_gotcha" || f.disabled) return;
        var msg = "";
        var v = (f.value || "").trim();
        if (f.type === "radio" || f.type === "checkbox") {
          if (!f.required || seenGroups[f.name]) return;
          seenGroups[f.name] = true;
          if (!form.querySelector('input[name="' + f.name + '"]:checked')) msg = "Please choose an option.";
        } else if (f.required && !v) msg = "This field is required.";
        else if (f.type === "email" && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) msg = "Please enter a valid email address.";
        else if (f.type === "tel" && v && !/^[+()\d\s-]{7,}$/.test(v)) msg = "Please enter a valid phone number.";
        setError(f, msg);
        if (msg) { ok = false; if (!first) first = f; }
      });
      if (first) first.focus();
      return ok;
    }

    form.querySelectorAll("input, select, textarea").forEach(function (f) {
      f.addEventListener(f.type === "radio" ? "change" : "input", function () { setError(f, ""); });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (status) { status.className = "form-status"; status.textContent = ""; }
      if (!validate()) return;
      if (form._gotcha && form._gotcha.value) return;

      var endpoint = form.getAttribute("data-endpoint");
      var btn = form.querySelector("[type='submit']");
      var label = btn ? btn.innerHTML : "";

      if (endpoint) {
        if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
        fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
          .then(function (r) {
            if (!r.ok) throw new Error("Request failed");
            form.reset();
            if (status) { status.className = "form-status is-success"; status.textContent = form.getAttribute("data-success") || "Thank you. Our team will get back to you shortly."; }
          })
          .catch(function () {
            if (status) { status.className = "form-status is-error"; status.textContent = "Something went wrong while sending. Please call +92 300 1268033 or email info@multicaps.net."; }
          })
          .finally(function () { if (btn) { btn.disabled = false; btn.innerHTML = label; } });
        return;
      }

      // Fallback: compose an email
      var lines = [];
      new FormData(form).forEach(function (value, key) {
        if (key.charAt(0) === "_" || value instanceof File) return;
        if (String(value).trim()) lines.push(key + ": " + value);
      });
      var subject = form.getAttribute("data-subject") || "Website enquiry";
      var to = form.getAttribute("data-mailto") || "info@multicaps.net";
      window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
      if (status) { status.className = "form-status is-success"; status.textContent = "Your email app should open with the details filled in. If it doesn't, write to " + to + "."; }
    });
  });

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
