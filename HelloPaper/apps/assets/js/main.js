function run() {
  let main_parent = document.getElementById("chat-tab").parentNode;

  main_parent.childNodes[0].classList.add("header-bar");
  main_parent.style = "padding: 0; margin: 0";
  main_parent.parentNode.style = "gap: 0";
  main_parent.parentNode.parentNode.style = "padding: 0";

  // add favicon
  const favicon = document.createElement("link");
  // set favicon attributes
  favicon.rel = "icon";
  favicon.type = "image/svg+xml";
  favicon.href = "/favicon.ico";
  document.head.appendChild(favicon);

  // move info-expand-button
  let info_expand_button = document.getElementById("info-expand-button");
  let chat_info_panel = document.getElementById("info-expand");
  chat_info_panel.insertBefore(
    info_expand_button,
    chat_info_panel.childNodes[2]
  );

  globalThis.fullTextSearch = () => {

    // Get sentences from evidence div
    var evidences = document.querySelectorAll(
      "#html-info-panel > div:last-child > div > details.evidence div.evidence-content"
    );
    console.log("Indexing evidences", evidences);

    const segmenterEn = new Intl.Segmenter("en", { granularity: "sentence" });
    // Split sentences and save to all_segments list
    var all_segments = [];
    for (var evidence of evidences) {
      // check if <details> tag is open
      if (!evidence.parentElement.open) {
        continue;
      }
      var markmap_div = evidence.querySelector("div.markmap");
      if (markmap_div) {
        continue;
      }

      var evidence_content = evidence.textContent.replace(/[\r\n]+/g, " ");
      sentence_it = segmenterEn.segment(evidence_content)[Symbol.iterator]();
      while ((sentence = sentence_it.next().value)) {
        segment = sentence.segment.trim();
        if (segment) {
          all_segments.push({
            id: all_segments.length,
            text: segment,
          });
        }
      }
    }
  }

}
