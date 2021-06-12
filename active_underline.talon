# Actions for the line labels and underlines type UI when it's showing
tag: user.telector_showing
and tag: user.telector_ui_underline
not title: Talon Draft
-
select <user.letters> <number_small>:
  user.telector_select("{letters}{number_small}", "{letters}{number_small}")
  user.telector_hide()

select <user.letters> <number_small> through <user.letters> <number_small>:
  user.telector_select("{letters_1}{number_small_1}", "{letters_2}{number_small_2}")
  user.telector_hide()

select <user.letters> <number_small> through <number_small>:
  user.telector_select("{letters}{number_small_1}", "{letters}{number_small_2}")
  user.telector_hide()

cursor <user.letters> <number_small>:
  user.telector_select("{letters}{number_small}", "{letters}{number_small}")
  user.telector_hide()
  key(right)

cursor before <user.letters> <number_small>:
  user.telector_select("{letters}{number_small}", "{letters}{number_small}")
  user.telector_hide()
  key(left)

click <user.letters> <number_small>:
  user.telector_click("{letters}{number_small}")
  user.telector_hide()
