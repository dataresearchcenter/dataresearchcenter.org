// As on openaleph.org: the section at the viewport's midpoint colors the page
// (body.bg--<color>, site.css), the header and the drawer (its screen--bg-*
// class). Without sections, header and drawer follow the page background.
(() => {
  const COLOR = /\bscreen--bg-(\w+)/;

  function current() {
    const sections = document.querySelectorAll(".md-content__inner > .screen[class*='screen--bg-']");
    if (!sections.length) {
      const bg = getComputedStyle(document.querySelector(".md-main")).backgroundColor;
      const [r, g, b, a = 1] = bg.match(/[\d.]+/g).map(Number);
      return [null, a > 0 && r + g + b > 384 ? "white" : "black"];
    }
    let color = sections[0].className.match(COLOR)[1];
    for (const section of sections) {
      if (section.getBoundingClientRect().top > innerHeight / 2) break;
      color = section.className.match(COLOR)[1];
    }
    return [color, color];
  }

  function setClass(el, prefix, color) {
    const name = color && prefix + color;
    if (name && el.classList.contains(name)) return;
    el.classList.remove(...[...el.classList].filter((c) => c.startsWith(prefix)));
    if (name) el.classList.add(name);
  }

  // The drawer is replaced on instant navigation, the header and body are not.
  function update() {
    const [page, chrome] = current();
    setClass(document.body, "bg--", page);
    for (const el of document.querySelectorAll(".md-header, .md-sidebar--nav-overlay")) {
      setClass(el, "screen--bg-", chrome);
    }
  }

  let frame = 0;
  const schedule = () => {
    frame ||= requestAnimationFrame(() => {
      frame = 0;
      update();
    });
  };
  addEventListener("scroll", schedule, { passive: true });
  addEventListener("resize", schedule, { passive: true });
  document$.subscribe(update);
})();
