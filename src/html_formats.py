# This string is html that displays a Reddit title,
# or at least my best recreation of a Reddit title.
# The string should be formatted with 6 parameters:
#   1. display bottom container
#   2. score
#   3. icon url
#   4. subreddit name
#   5. username
#   6. title
title_html_format = "<style>.root{{background:#1a1a1b;padding:1em;font-family:sans-serif;font-size:2em;max-width" \
                    ":1080px}}.encompassing-container{{display:flex}}.left-container{{" \
                    "display:flex;flex-direction:column;align-items:center;color:#818384;font-size:1em;gap:.2em" \
                    "}}@font-face{{font-family:vote;src:url(" \
                    "https://www.redditstatic.com/desktop2x/fonts/redesignIcon2020/redesignFont2020" \
                    ".a59e78115daeedbd9ef7f241a25c2031.ttf)}}.icon{{" \
                    "font-family:vote;font-size:1.2em}}.upvote-icon:before{{content:\"\\f34c\"}}.votes{{" \
                    "color:#d7dadc}}.downvote-icon:before{{content:\"\\f197\"}}.right-container{{" \
                    "margin-left:.75em}}.top-container{{" \
                    "display:flex;align-items:center;font-size:.65em;gap:.35em}}.avatar{{" \
                    "border-radius:50%;height:2em;width:2em}}.subreddit{{color:#d7dadc;font-weight:700}}.ago{{" \
                    "color:#818384}}.middle-container{{display:flex;margin-top:.5em}}.title{{" \
                    "color:#d7dadc;font-size:1.25em}}.bottom-container{{display:{" \
                    "};color:#818384;margin-top:1em;align-items:center;gap:.35em}}.comment-icon:before{{" \
                    "content:\"\\f16f\"}}.award-icon:before{{content:\"\\f123\"}}.share-icon:before{{" \
                    "content:\"\\f280\"}}.ellipsis-icon:before{{content:\"\\f229\"}}.option{{" \
                    "font-size:.75em;margin-right:1em;font-weight:700}}</style><div class=root><div " \
                    "class=encompassing-container><div class=left-container><div class=\"icon " \
                    "upvote-icon\"></div><div class=votes>{}</div><div class=\"icon " \
                    "downvote-icon\"></div></div><div class=right-container><div class=top-container><img " \
                    "class=avatar src={}><div class=subreddit>r/{}</div><div class=ago>·</div><div " \
                    "class=ago>Posted by u/{}</div></div><div class=middle-container><div class=title>{" \
                    "}</div></div><div class=bottom-container><div class=\"icon comment-icon\"></div><div " \
                    "class=option>Comment</div><div class=\"icon award-icon\"></div><div " \
                    "class=option>Award</div><div class=\"icon share-icon\"></div><div " \
                    "class=option>Share</div><div class=\"icon ellipsis-icon\"></div></div></div></div></div>"

# This string is html that displays a Reddit comment,
# or at least my best recreation of a Reddit comment.
# The string should be formatted with 5 parameters:
#   1. display bottom container
#   2. pfp url
#   3. username
#   4. comment
#   5. score.
comment_html_format = "<style>.root{{background:#1a1a1b;padding:1em;font-family:sans-serif;font-size:1.25em;max-width" \
                      ":1080px}}.top-container{{display:flex;align-items:center;gap:.35em}}.avatar{{" \
                      "border-radius:50%;height:2em;width:2em}}.username{{color:#d7dadc}}.ago{{" \
                      "font-size:.75em;color:#818384}}.line{{margin-left:1em;border-left:2px solid " \
                      "gray}}.middle-container{{display:flex;margin-top:.5em;margin-left:1em}}.comment{{" \
                      "color:#d7dadc;margin-left:.35em}}.bottom-container{{display:{" \
                      "};align-items:center;margin-top:1em;margin-left:1.35em;gap:.5em;color:#818384}}@font-face{{" \
                      "font-family:vote;src:url(" \
                      "https://www.redditstatic.com/desktop2x/fonts/redesignIcon2020/redesignFont2020" \
                      ".a59e78115daeedbd9ef7f241a25c2031.ttf)}}.icon{{" \
                      "font-family:vote;font-size:1.2em}}.upvote-icon:before{{content:\"\\f34c\"}}.votes{{" \
                      "color:#d7dadc}}.downvote-icon:before{{content:\"\\f197\"}}.comment-icon:before{{" \
                      "content:\"\\f16f\"}}.option{{font-size:.75em}}</style><div class=root><div " \
                      "class=top-container><img class=avatar src={}><div class=username>{}</div><div " \
                      "class=ago>·</div><div class=ago>sometime ago</div></div><div class=line><div " \
                      "class=middle-container><div class=comment>{}</div><script " \
                      "src=https://cdn.jsdelivr.net/npm/marked/marked.min.js></script><script>document" \
                      ".querySelectorAll(\".comment\").forEach(e => e.innerHTML = marked.parse(" \
                      "e.innerHTML))</script></div><div class=bottom-container><div class=\"icon " \
                      "upvote-icon\"></div><div class=votes>{}</div><div class=\"icon downvote-icon\"></div><div " \
                      "class=\"icon comment-icon\"></div><div class=option><b>Reply</b></div><div " \
                      "class=option><b>Give Award</b></div><div class=option><b>Share</b></div><div " \
                      "class=option><b>Report</b></div><div class=option><b>Save</b></div><div " \
                      "class=option><b>Follow</b></div></div></div></div>"