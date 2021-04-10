# Actions for the word labels type UI (default) when it's showing
tag: user.telector_showing
not tag: user.telector_ui_underline
-
select <user.letters>:
  user.telector_select("{letters}", "{letters}")
  user.telector_hide()

select <user.letters> through <user.letters>:
  user.telector_select("{letters_1}", "{letters_2}")
  user.telector_hide()

cursor <user.letters>:
  user.telector_select("{letters}", "{letters}")
  user.telector_hide()
  key(right)

cursor before <user.letters>:
  user.telector_select("{letters}", "{letters}")
  user.telector_hide()
  key(left)

click <user.letters>:
  user.telector_click("{letters}")
  user.telector_hide()
