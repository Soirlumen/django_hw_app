document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.querySelector("textarea[data-codemirror='editor']");
  if (!textarea) return;

  const languageSelect = document.getElementById("id_programming_language");

  const editor = CodeMirror.fromTextArea(textarea, {
    lineNumbers: true,
    mode: languageSelect ? languageSelect.value : "python",
    lineWrapping: true,
    indentUnit: 4,
    tabSize: 4,
    autoCloseBrackets: true,
    matchBrackets: true,
    autoCloseTags: true,
    matchTags: { bothTags: true },
    foldGutter: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    extraKeys: {
      "Ctrl-/": "toggleComment",
      "Cmd-/": "toggleComment",
      "Ctrl-Q": function(cm) { cm.foldCode(cm.getCursor()); },
      "Tab": function(cm) {
        if (cm.somethingSelected()) {
          cm.indentSelection("add");
        } else {
          cm.replaceSelection("    ", "end");
        }
      },
      "Enter": "newlineAndIndentContinueMarkdownList"
    }
  });

  if (languageSelect) {
    languageSelect.addEventListener("change", function () {
      editor.setOption("mode", this.value);
    });
  }

  const form = textarea.closest("form");
  if (form) {
    form.addEventListener("submit", function () {
      editor.save();
    });
  }
});