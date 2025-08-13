# --- tuned for your Sign-In page ---

# Words in natural descriptions we should ignore when keywording
FILLER_WORDS = {
    "input", "box", "field", "text", "textbox", "entry",
    "please", "enter", "your", "the", "a", "an",
    "value", "type", "click", "press", "button", "password", "submit", "next", "continue",
    "select", "choose", "pick", "tap", "check", "uncheck", "tick", "untick",
    "clickable", "clicks", "clicking", "clicks on", "vault"
}

# Task-focused synonyms visible in the DOM you shared
SYNONYMS = {
    "username": {"username", "user name", "login", "login id", "user id", "userid"},
    "remember": {"remember", "remember me", "keep me signed in"},
    "next": {"next", "continue", "submit"},
    "password": {"password", "pass code", "passcode"},   # future-proof for the next step
}

# Attributes to search for keyword hits (from your DOM)
ATTR_KEYS = [
    # common identifiers
    "id", "name", "class", "title",
    # form UX
    "placeholder", "aria-label", "autocomplete", "autocapitalize", "autocorrect", "spellcheck", "maxlength",
    # datatest-style attrs & validation
    "data-testid", "data-test", "data-qa", "data-id", "data-val", "data-val-required", "data-pega-id",
    # semantics
    "role", "type", "for", "value",
]

# Ancestor tags that are good “context containers” on this page
PREFERRED_TAGS = [
    "fieldset", "div", "section", "form", "li", "tr", "td", "article", "label"
]

# Class names that indicate a useful grouping container in your markup
PREFERRED_CLASS_KEYS = {
    # form groups on this page
    "form-group", "ctrl", "ctrl-textbox", "ctrl-input-error",
    "has-feedback", "has-feedback-reverse",
    "checkbox-container",

    # layout/blocks
    "panel", "panel-default", "panel-body", "section", "section-content", "section-inner",

    # buttons/cta (rarely used as context, but included in case description targets them)
    "btn", "btn-primary", "btn-block",

    # branding block shown in your DOM
    "logo",
}
