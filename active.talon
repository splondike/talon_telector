tag: user.telector_showing
-
select <user.telector_anchor>:
  user.telector_select("{telector_anchor}", "{telector_anchor}")

select <user.telector_anchor> through <user.telector_anchor>:
  user.telector_select("{telector_anchor_1}", "{telector_anchor_2}")

cursor <user.telector_anchor>:
  user.telector_select("{telector_anchor}", "{telector_anchor}")
  key(right)

cursor before <user.telector_anchor>:
  user.telector_select("{telector_anchor}", "{telector_anchor}")
  key(left)

click <user.telector_anchor>:
  user.telector_click("{telector_anchor}")
