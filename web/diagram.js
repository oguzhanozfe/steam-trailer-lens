/* Standalone browser view for the computed project report. */
window.drawProjectView = function (host, report, input) {
  "use strict";
  function el(tag, text, css) {
    const item = document.createElement(tag);
    if (text != null) item.textContent = String(text);
    if (css) item.style.cssText = css;
    return item;
  }
  const figure = el("figure", null, "box-sizing:border-box;margin:12px 0 16px;padding:12px 14px;border-radius:9px;background:#172329;color:#f4f5f2;max-height:210px;overflow:auto;font:13px/1.35 system-ui,sans-serif;text-align:left");
  const head = el("figcaption", "Six-slice trailer storyboard", "font-size:15px;font-weight:700;letter-spacing:-.015em;color:#ace0ae;margin-bottom:7px");
  figure.append(head);
  host.replaceChildren(figure);
  const rows = Array.isArray(report && report.rows) ? report.rows : [];
  if (!rows.length) {
    figure.append(el("p", "No findings to display.", "margin:0"));
    return;
  }

  const strip = el("div", null, "display:grid;grid-template-columns:repeat(6,minmax(82px,1fr));gap:4px;overflow-x:auto;padding:4px 0 7px");
  const colors = {gameplay:"#a0d2a6", cinematic:"#b2b7ec", title:"#efbd82", logo:"#b8d3d4", Unlogged:"#c3c6c5"};
  for (const row of rows.slice(0,6)) {
    const card = el("div", null, "display:grid;grid-template-rows:auto auto 1fr auto;min-height:86px;padding:6px 7px;border-radius:3px;background:#2a383c;min-width:0");
    const type = colors[row.Content] || "#c3c6c5";
    const heading = el("strong", row.Content, "text-transform:uppercase;color:"+type+";letter-spacing:.04em;font:700 9px system-ui");
    const copy = el("div", row.Shot, "font-size:11px;line-height:1.25;margin:5px 0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden");
    copy.title = row.Shot;
    card.append(el("div", "0"+row.Slice, "font:700 18px/1.2 ui-monospace,monospace;color:#fcf8f2"),heading,copy,
      el("div", row["Start (s)"]+"s / "+row["Length (s)"]+"s", "font:10px ui-monospace,monospace;color:#dee6e3"));
    strip.append(card);
  }
  figure.append(strip, el("div", "Illustrative cut list · source start / sample length · each card uses the logged shot description", "font-size:11px;color:#c9dad4"));

};
