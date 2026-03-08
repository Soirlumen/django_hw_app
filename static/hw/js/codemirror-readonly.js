document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.getElementById("hw-code-viewer");
  if (!textarea) return;

  const language = textarea.dataset.codeLanguage || "python";

  const viewer = CodeMirror.fromTextArea(textarea, {
    mode: language === "null" ? null : language,
    lineNumbers: true,
    lineWrapping: true,
    readOnly: "nocursor",
    indentUnit: 4,
    tabSize: 4,
    viewportMargin: Infinity,
    foldGutter: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
  });

  viewer.setSize("100%", "auto");
});