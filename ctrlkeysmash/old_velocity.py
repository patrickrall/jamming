
# old snippets of code to mess with ball velocity

 ignore_key = None
            if True:

                for key in keys:
                    if key in level: kind = level[key]
                    else: kind = level["default"]
                    if keys_pressed[key] and len(kind) > 1: kind = kind[1]
                    else: kind = kind[0]

                    if kind != "wall": continue


                    rect = key_rects[key]
                    rpos = Vector2(rect["x"],rect["y"])
                    rdims = Vector2(rect["w"],rect["h"])

                    if circle_intersect_rect(ball["pos"], 10, rpos, rdims):

                        ignore_key = key

                        dright = (rpos.x + rdims.x - ball["pos"].x)
                        dleft = (ball["pos"].x - rpos.x)

                        dtop = (rpos.y + rdims.y - ball["pos"].y)
                        dbot = (ball["pos"].y - rpos.y)

                        mi = min(dright,dleft,dtop,dbot)
                        delta = mi*2

                        if mi == dright:
                            if ball["vel"].x < 0: ball["vel"].x = 0
                            ball["vel"].x += delta
                        if mi == dleft:
                            if ball["vel"].x > 0: ball["vel"].x = 0
                            ball["vel"].x -= delta
                        if mi == dtop:
                            if ball["vel"].y < 0: ball["vel"].y = 0
                            ball["vel"].y += delta
                        if mi == dbot:
                            if ball["vel"].y > 0: ball["vel"].y = 0
                            ball["vel"].y -= delta

                        ball["vel"].x = int(ball["vel"].x)
                        ball["vel"].y = int(ball["vel"].y)

                        break

            v2 = ball["vel"].x*ball["vel"].x + ball["vel"].y*ball["vel"].y
            if v2 > 20000:
                ball["vel"].x *= 0.8
                ball["vel"].y *= 0.8

                ball["vel"].x = int(ball["vel"].x)
                ball["vel"].y = int(ball["vel"].y)

            if v2 < 10000:
                ball["vel"].x *= 1.1
                ball["vel"].y *= 1.1

                ball["vel"].x = int(ball["vel"].x)
                ball["vel"].y = int(ball["vel"].y)

