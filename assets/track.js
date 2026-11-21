/* FridgePaper download + tool tracking for Google Analytics (G-BLV2XDN4JW).
   Events:
   printable_download  { printable: "kids-chore-chart", method: "download" | "print" | "browser_print" }
   tool_used           { tool: "grocery-budget-calculator" }                                          */
(function () {
  function send(name, params) {
    try { if (window.gtag) window.gtag('event', name, Object.assign({ transport_type: 'beacon' }, params)); } catch (e) {}
  }
  var path = location.pathname;
  var page = (path.split('/').pop() || 'index').replace(/\.html$/, '') || 'index';
  var section = path.indexOf('/tools/') >= 0 ? 'tools' : path.indexOf('/printables/') >= 0 ? 'printables' : 'other';

  // 1. Clicks on any PDF link (Download PDF and Print buttons)
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href$=".pdf"]');
    if (a) {
      var file = a.getAttribute('href').split('/').pop().replace(/\.pdf$/, '').replace(/^fridgepaper-/, '');
      send('printable_download', { printable: file, method: a.hasAttribute('download') ? 'download' : 'print' });
      return;
    }
    // 2. Chore Chart Maker buttons
    var b = e.target.closest && e.target.closest('#cPdf, #cPrint');
    if (b) send('printable_download', { printable: 'chore-chart-maker', method: b.id === 'cPdf' ? 'download' : 'print' });
  }, true);

  // 3. Printing straight from the browser (Print buttons on older pages, or Ctrl+P)
  var printed = false;
  window.addEventListener('beforeprint', function () {
    if (printed || section === 'other') return;
    printed = true;
    send('printable_download', { printable: page, method: 'browser_print' });
  });

  // 4. Someone actually uses a calculator or tool (counted once per visit)
  if (section === 'tools' && page !== 'index') {
    var used = false;
    var mark = function () { if (!used) { used = true; send('tool_used', { tool: page }); } };
    document.addEventListener('input', mark, true);
    document.addEventListener('change', mark, true);
  }
})();
