document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.querySelector("textarea[data-codemirror='editor']");
  if (!textarea) return;

  const languageSelect = document.getElementById("id_programming_language");

  const maxLength = textarea.getAttribute("maxlength");

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

  if (maxLength) {
    editor.on("beforeChange", function(cm, change) {
      if (!change.update) return;

      const oldValue = cm.getValue();

      const newValue =
        oldValue.substring(0, cm.indexFromPos(change.from)) +
        change.text.join("\n") +
        oldValue.substring(cm.indexFromPos(change.to));

      if (newValue.length > Number(maxLength)) {
        change.cancel();
      }
    });
  }


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