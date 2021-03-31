tag: user.textarea_labels_showing
-
select <user.textarea_labels_anchor>:
  user.textarea_labels_select_text("{textarea_labels_anchor}", "{textarea_labels_anchor}")

select <user.textarea_labels_anchor> through <user.textarea_labels_anchor>:
  user.textarea_labels_select_text("{textarea_labels_anchor_1}", "{textarea_labels_anchor_2}")

click <user.textarea_labels_anchor>:
  user.textarea_labels_click_anchor("{textarea_labels_anchor}")
